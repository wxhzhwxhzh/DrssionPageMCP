#!/usr/bin/env python
# -*- coding:utf-8 -*-

from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.items import ChromiumTab
import threading


# ------------------ 工具函数 ------------------

def cdp_send(browser, method, session_id, **params):
    """统一发送 CDP 指令"""
    browser._driver._send({
        'method': method,
        'sessionId': session_id,
        **params
    })


def listen(tab: ChromiumTab):
    """后台线程监听资源"""  

    threading.Thread(target=_listen,args=(tab,)).start()


def _listen(tab,targets=".js"):
    tab.listen.start(targets=targets)
    tab.refresh()
    for res in tab.listen.steps():
        print(f"[{tab.title}] [Resource] {res.url}")    


# ------------------ 事件回调 ------------------

def on_tab_attached(browser, **kwargs):
    """新标签页被附加时触发"""
    info = kwargs.get('targetInfo', {})
    session_id = kwargs.get('sessionId')
    target_id = info.get('targetId')

    print(f"[发现新标签页：] {session_id} [{target_id}]")

    # 恢复执行 & 停止加载
    cdp_send(browser, 'Runtime.runIfWaitingForDebugger', session_id)
    cdp_send(browser, 'Page.stopLoading', session_id)

    tab = browser.get_tab(target_id)
    listen(tab)


# ------------------ 打开浏览器 ------------------


co = ChromiumOptions()
# co.set_argument('--no-sandbox')


browser = Chromium(co)

# 自动附加新目标
browser._driver.run(
    'Target.setAutoAttach',
    autoAttach=True,
    waitForDebuggerOnStart=True,
    flatten=True
)

# 注册回调（用 lambda 消除全局变量依赖）
browser._driver.set_callback(
    'Target.attachedToTarget',
    lambda **kw: on_tab_attached(browser, **kw)
)


tab = browser.latest_tab
tab.get("https://www.baidu.com/")

link = tab.ele('@tx():贴吧')
if link:
    link.click()

tab.wait(200)

   

