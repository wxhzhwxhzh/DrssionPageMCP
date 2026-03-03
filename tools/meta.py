# -*- coding: utf-8 -*-

from state import get_dp
from utils.contract import ok


def get_version():
    return ok({"version": get_dp().get_version()})


def get_DrissionPage_code_guide():
    return ok({"markdown": get_dp().get_DrissionPage_code_guide()})
