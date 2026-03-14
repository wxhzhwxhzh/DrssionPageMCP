# -*- coding: utf-8 -*-

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional, Sequence


PointLike = tuple[float, float]


@dataclass(frozen=True)
class MousePoint:
    x: float
    y: float
    t: float


@dataclass(frozen=True)
class ReplayStep:
    dx: int
    dy: int
    duration: float


@dataclass
class TrajectoryConfig:
    sample_hz_min: int = 90
    sample_hz_max: int = 140
    duration_min: float = 0.18
    duration_max: float = 1.6
    base_offset_ratio: float = 0.16
    max_offset_px: float = 90.0
    jitter_perp_ratio: float = 0.010
    jitter_para_ratio: float = 0.0035
    jitter_max_px: float = 2.4
    overshoot_chance: float = 0.78
    overshoot_ratio: float = 0.035
    overshoot_min_px: float = 3.0
    overshoot_max_px: float = 18.0
    correction_duration_ratio: float = 0.16
    pause_chance: float = 0.22
    pause_min: float = 0.015
    pause_max: float = 0.055


class HumanMouseTrajectory:
    """
    Generate smoother, less robotic mouse movement for drag operations.
    """

    def __init__(self, config: Optional[TrajectoryConfig] = None):
        self.config = config or TrajectoryConfig()

    def generate(
        self,
        start: PointLike,
        end: PointLike,
        *,
        seed: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> list[MousePoint]:
        rng = random.Random(seed)
        start_xy = (float(start[0]), float(start[1]))
        end_xy = (float(end[0]), float(end[1]))

        distance = self._distance(start_xy, end_xy)
        if distance < 0.001:
            return [MousePoint(start_xy[0], start_xy[1], 0.0)]

        total_duration = self._resolve_duration(distance, rng, duration)
        has_overshoot = distance >= 60 and rng.random() < self.config.overshoot_chance

        if has_overshoot:
            overshoot_end = self._build_overshoot_point(start_xy, end_xy, rng)
            main_ratio = 1.0 - self.config.correction_duration_ratio
            main_duration = total_duration * main_ratio
            correction_duration = total_duration - main_duration

            main_points = self._build_segment(
                start_xy,
                overshoot_end,
                duration=main_duration,
                rng=rng,
                is_correction=False,
            )
            correction_points = self._build_segment(
                overshoot_end,
                end_xy,
                duration=correction_duration,
                rng=rng,
                is_correction=True,
            )
            merged = self._merge_segments(main_points, correction_points)
        else:
            merged = self._build_segment(
                start_xy,
                end_xy,
                duration=total_duration,
                rng=rng,
                is_correction=False,
            )

        return self._normalize_time(merged)

    def to_replay_steps(self, points: Sequence[MousePoint]) -> list[ReplayStep]:
        if len(points) < 2:
            return []

        steps: list[ReplayStep] = []
        carry_x = 0.0
        carry_y = 0.0
        pending_wait = 0.0
        total_dx = 0
        total_dy = 0

        for prev, curr in zip(points, points[1:]):
            dt = max(0.0, curr.t - prev.t)
            carry_x += curr.x - prev.x
            carry_y += curr.y - prev.y

            move_x = int(round(carry_x))
            move_y = int(round(carry_y))

            if move_x == 0 and move_y == 0:
                pending_wait += dt
                continue

            steps.append(ReplayStep(move_x, move_y, max(0.001, pending_wait + dt)))
            total_dx += move_x
            total_dy += move_y
            carry_x -= move_x
            carry_y -= move_y
            pending_wait = 0.0

        target_dx = int(round(points[-1].x - points[0].x))
        target_dy = int(round(points[-1].y - points[0].y))
        fix_dx = target_dx - total_dx
        fix_dy = target_dy - total_dy

        if fix_dx != 0 or fix_dy != 0:
            if steps:
                last = steps[-1]
                steps[-1] = ReplayStep(last.dx + fix_dx, last.dy + fix_dy, last.duration)
            else:
                steps.append(ReplayStep(fix_dx, fix_dy, 0.001))
        elif pending_wait > 0:
            steps.append(ReplayStep(0, 0, pending_wait))

        return steps

    def replay_on_actions(
        self,
        actions,
        points: Sequence[MousePoint],
        *,
        move_to_start: bool = True,
        hold_before_move: bool = False,
        release_after_move: bool = False,
    ) -> list[ReplayStep]:
        if len(points) < 2:
            return []

        steps = self.to_replay_steps(points)
        start = points[0]

        if move_to_start:
            actions.move_to((round(start.x), round(start.y)))
        if hold_before_move:
            actions.hold()

        for step in steps:
            if step.dx == 0 and step.dy == 0:
                actions.wait(step.duration)
            else:
                actions.move(step.dx, step.dy, duration=step.duration)

        if release_after_move:
            actions.release()

        return steps

    def build_report(
        self,
        points: Sequence[MousePoint],
        steps: Sequence[ReplayStep],
        *,
        seed: Optional[int],
    ) -> dict:
        if not points:
            return {
                "human_like": True,
                "seed": seed,
                "point_count": 0,
                "step_count": 0,
                "actual_duration_ms": 0,
            }

        return {
            "human_like": True,
            "seed": seed,
            "point_count": len(points),
            "step_count": len(steps),
            "actual_duration_ms": int(round(points[-1].t * 1000)),
            "start": {"x": round(points[0].x, 2), "y": round(points[0].y, 2)},
            "end": {"x": round(points[-1].x, 2), "y": round(points[-1].y, 2)},
        }

    def _build_segment(
        self,
        start: PointLike,
        end: PointLike,
        *,
        duration: float,
        rng: random.Random,
        is_correction: bool,
    ) -> list[MousePoint]:
        distance = self._distance(start, end)
        sample_hz = rng.randint(self.config.sample_hz_min, self.config.sample_hz_max)
        steps = max(8, int(round(duration * sample_hz)))

        cp1, cp2 = self._control_points(start, end, rng, is_correction=is_correction)
        unit_x, unit_y = self._unit_vector(start, end)
        normal_x, normal_y = -unit_y, unit_x

        jitter_perp = min(self.config.jitter_max_px, distance * self.config.jitter_perp_ratio)
        jitter_para = min(self.config.jitter_max_px * 0.45, distance * self.config.jitter_para_ratio)
        if is_correction:
            jitter_perp *= 0.45
            jitter_para *= 0.35

        perp_noise = self._smoothed_noise(steps + 1, rng, window=5)
        para_noise = self._smoothed_noise(steps + 1, rng, window=7)
        time_marks = self._time_marks(
            duration,
            steps,
            rng,
            allow_pause=not is_correction and distance >= 180,
        )

        points: list[MousePoint] = []
        for i in range(steps + 1):
            progress = i / steps
            eased = self._minimum_jerk(progress)
            x, y = self._cubic_bezier(start, cp1, cp2, end, eased)

            if 0 < i < steps:
                envelope = math.sin(math.pi * progress) ** 1.35
                x += unit_x * para_noise[i] * jitter_para * envelope
                y += unit_y * para_noise[i] * jitter_para * envelope
                x += normal_x * perp_noise[i] * jitter_perp * envelope
                y += normal_y * perp_noise[i] * jitter_perp * envelope

            points.append(MousePoint(x, y, time_marks[i]))

        return points

    def _merge_segments(
        self,
        first: Sequence[MousePoint],
        second: Sequence[MousePoint],
    ) -> list[MousePoint]:
        if not first:
            return list(second)
        if not second:
            return list(first)

        offset = first[-1].t
        merged = list(first)
        for point in second[1:]:
            merged.append(MousePoint(point.x, point.y, point.t + offset))
        return merged

    def _normalize_time(self, points: Sequence[MousePoint]) -> list[MousePoint]:
        if not points:
            return []
        start_t = points[0].t
        return [MousePoint(point.x, point.y, max(0.0, point.t - start_t)) for point in points]

    def _resolve_duration(
        self,
        distance: float,
        rng: random.Random,
        requested_duration: Optional[float],
    ) -> float:
        if requested_duration is not None:
            return self._clamp(
                float(requested_duration),
                self.config.duration_min,
                self.config.duration_max,
            )
        duration = 0.11 + 0.0020 * distance + 0.018 * math.log2(distance + 1.0)
        duration *= rng.uniform(0.92, 1.12)
        return self._clamp(duration, self.config.duration_min, self.config.duration_max)

    def _build_overshoot_point(
        self,
        start: PointLike,
        end: PointLike,
        rng: random.Random,
    ) -> PointLike:
        distance = self._distance(start, end)
        unit_x, unit_y = self._unit_vector(start, end)
        normal_x, normal_y = -unit_y, unit_x

        overshoot = self._clamp(
            distance * self.config.overshoot_ratio * rng.uniform(0.8, 1.35),
            self.config.overshoot_min_px,
            self.config.overshoot_max_px,
        )
        side_drift = overshoot * rng.uniform(-0.28, 0.28)
        return (
            end[0] + unit_x * overshoot + normal_x * side_drift,
            end[1] + unit_y * overshoot + normal_y * side_drift,
        )

    def _control_points(
        self,
        start: PointLike,
        end: PointLike,
        rng: random.Random,
        *,
        is_correction: bool,
    ) -> tuple[PointLike, PointLike]:
        distance = self._distance(start, end)
        unit_x, unit_y = self._unit_vector(start, end)
        normal_x, normal_y = -unit_y, unit_x

        cp1_ratio = rng.uniform(0.18, 0.32)
        cp2_ratio = rng.uniform(0.62, 0.86)
        offset_amp = self._clamp(
            distance * self.config.base_offset_ratio,
            5.0 if not is_correction else 1.5,
            self.config.max_offset_px if not is_correction else 18.0,
        )
        if is_correction:
            offset_amp *= 0.45

        cp1_offset = rng.uniform(-offset_amp, offset_amp)
        cp2_offset = rng.uniform(-offset_amp, offset_amp)

        cp1 = (
            start[0] + unit_x * distance * cp1_ratio + normal_x * cp1_offset,
            start[1] + unit_y * distance * cp1_ratio + normal_y * cp1_offset,
        )
        cp2 = (
            start[0] + unit_x * distance * cp2_ratio + normal_x * cp2_offset,
            start[1] + unit_y * distance * cp2_ratio + normal_y * cp2_offset,
        )
        return cp1, cp2

    def _time_marks(
        self,
        duration: float,
        steps: int,
        rng: random.Random,
        *,
        allow_pause: bool,
    ) -> list[float]:
        durations = [1.0 + rng.uniform(-0.18, 0.18) for _ in range(steps)]

        pause_budget = 0.0
        if allow_pause and rng.random() < self.config.pause_chance:
            pause_budget = rng.uniform(self.config.pause_min, self.config.pause_max)

        active_duration = max(0.001, duration - pause_budget)
        scale = active_duration / sum(durations)
        durations = [part * scale for part in durations]

        pause_index = None
        if pause_budget > 0:
            pause_index = rng.randint(max(2, steps // 4), max(3, int(steps * 0.82)))

        marks = [0.0]
        current_t = 0.0
        for idx, dt in enumerate(durations, start=1):
            current_t += dt
            marks.append(current_t)
            if pause_index is not None and idx == pause_index:
                current_t += pause_budget
                marks[-1] = current_t

        marks[-1] = duration
        return marks

    @staticmethod
    def _smoothed_noise(length: int, rng: random.Random, window: int) -> list[float]:
        raw = [rng.gauss(0.0, 1.0) for _ in range(length)]
        out: list[float] = []
        radius = max(1, window // 2)
        for i in range(length):
            start = max(0, i - radius)
            end = min(length, i + radius + 1)
            out.append(sum(raw[start:end]) / (end - start))
        return out

    @staticmethod
    def _cubic_bezier(
        p0: PointLike,
        p1: PointLike,
        p2: PointLike,
        p3: PointLike,
        t: float,
    ) -> PointLike:
        mt = 1.0 - t
        mt2 = mt * mt
        t2 = t * t
        x = (
            mt2 * mt * p0[0]
            + 3.0 * mt2 * t * p1[0]
            + 3.0 * mt * t2 * p2[0]
            + t2 * t * p3[0]
        )
        y = (
            mt2 * mt * p0[1]
            + 3.0 * mt2 * t * p1[1]
            + 3.0 * mt * t2 * p2[1]
            + t2 * t * p3[1]
        )
        return x, y

    @staticmethod
    def _minimum_jerk(t: float) -> float:
        return 10 * t**3 - 15 * t**4 + 6 * t**5

    @staticmethod
    def _distance(a: PointLike, b: PointLike) -> float:
        return math.hypot(b[0] - a[0], b[1] - a[1])

    @staticmethod
    def _unit_vector(a: PointLike, b: PointLike) -> PointLike:
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        distance = math.hypot(dx, dy)
        if distance < 1e-9:
            return 1.0, 0.0
        return dx / distance, dy / distance

    @staticmethod
    def _clamp(value: float, lower: float, upper: float) -> float:
        return max(lower, min(upper, value))
