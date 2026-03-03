#！/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any,Literal
import re
from collections import deque
from pathlib import Path
from DrissionPage import Chromium,ChromiumOptions
from mcp.server.fastmcp import FastMCP,Image,Context

from DrissionPage.items import SessionElement, ChromiumElement, ShadowRoot, NoneElement, ChromiumTab, MixTab, ChromiumFrame
from DrissionPage.common import Keys


提示='''
DrissionPage MCP  是一个基于 DrissionPage 和 FastMCP 的浏览器自动化MCP server服务器，它提供了一系列强大的浏览器操作 API，让您能够轻松通过AI实现网页自动化操作。
点击元素前，建议先获取页面 DOM 信息，使用 getSimplifiedDomTree() 方法。
输入元素前，建议先获取可输入元素信息，使用 getInputElementsInfo() 方法。

'''



#region DrissionPageMCP
class DrissionPageMCP():
    def __init__(self):
        # Listener buffers must be bounded; otherwise long-running sessions can OOM.
        self._listener_maxlen = 500
        self.browser = None
        self.session = None
        self.current_tab = None
        self.current_frame = None
        self.current_shadow_root = None
        self.cdp_event_data = deque(maxlen=self._listener_maxlen)
        self.cdp_event_dropped = 0
        self.response_listener_data = deque(maxlen=self._listener_maxlen)
        self.response_listener_dropped = 0
        self._last_connect_config: dict[str, Any] = {}

    def test(self):
        return "test"
    def get_DrissionPage_code_guide(self)-> str:
        """ 获取 DrissionPage 代码指南"""
        guide_path = Path(__file__).parent / "docs" / "guides" / "DrissionPage_code_guide.md"
        with open(guide_path, "r", encoding="utf-8") as f:
            return f.read()
        # return "1.0.3"
    def get_version(self)-> str:
        """ 获取版本号"""
        return "1.0.4"
    async def connect_or_open_browser(self, config: dict | None = None) -> dict:
        """
        用DrissionPage 打开或接管已打开的浏览器，参数通过字典传递。
        必要参数:
            config (dict): 可选键包括 debug_port、address、browser_path、headless
        返回:
            dict: 浏览器信息
        """
        config = config or {}
        debug_port = config.get("debug_port", 9222)
        address = config.get("address")

        co = ChromiumOptions()
        if address:
            co.set_address(address)
        elif debug_port:
            co.set_local_port(debug_port)
        if config.get("browser_path"):
            co.set_browser_path(config["browser_path"])
        if config.get("headless", False):
            co.headless(True)

        self.browser = Chromium(co)
        self._last_connect_config = dict(config)
        tab = self.browser.latest_tab        

        if address:
            connect_line = f"co.set_address('{address}')"
        else:
            connect_line = f"co.set_local_port({debug_port})"

        return {
            "browser_address": self.browser._chromium_options.address,
            "latest_tab_title": tab.title,
            "latest_tab_id": tab.tab_id,
            "active_connection": dict(self._last_connect_config),
            "等价Python代码":f'''
from DrissionPage import Chromium, ChromiumOptions
form DrissionPage.common import Keys
# 创建配置对象
co = ChromiumOptions()
{connect_line}
# 创建浏览器对象，浏览器对象不能打开网址，只有标签页对象才能打开网址
browser = Chromium(co)
# 获取最新标签页
tab = browser.latest_tab
'''
        }
    
    async def new_tab(self, url: str) -> str:
        """用DrissionPage 控制的浏览器,打开新标签页并 打开一个网址"""    
        tab = self.browser.new_tab(url)    
        return {"title": tab.title, "tab_id": tab.tab_id, "url": tab.url,"dom":self.getSimplifiedDomTree(),
               "等价Python代码":f'''
tab = browser.new_tab('{url}')
''' }
    
    def wait(self, a:int) :
        """等待a秒"""
        self.browser.latest_tab.wait(a)
        return {"rsult":f"等待{a}秒成功", "等价Python代码":f"tab.wait({a})"}
    
    async def get(self,url:str)->str:
        """在当前标签页打开一个网址"""
        if not  self.browser:
            await self.connect_or_open_browser()
            # return "请先打开或者连接浏览器"
        self.lastest_tab.get(url)
        tab=self.browser.latest_tab
        return {"title": tab.title, "tab_id": tab.tab_id, "url": tab.url,"dom":self.getSimplifiedDomTree(),"等价Python代码":f'''tab.get('{url}')'''}

        
    
    #region 上传和下载
    def download_file(self, url: str, path: str, rename: str) -> str:
        """控制浏览器下载文件到指定路径
        
        Args:
            url (str): 文件的URL地址
            path (str): 文件保存的路径
            rename (str): 重命名文件名
        
        Returns:
            str: 下载结果信息
        """
        tab = self.lastest_tab
        result = tab.download(file_url=url, save_path=path, rename=rename)
        return str(result)
    
    def upload_file(self,  file_path: str, xpath: str = "//input[@type='file']") -> dict:
        """点击当网页上的 <input type="file"> 元素触发上传文件的操作，上传 file_path 文件到当前网页
        
        Args:
            file_path (str): 要上传的文件路径
            xpath (str): 触发上传的元素 xpath（默认 //input[@type='file']）
        
        Returns:
            str: 上传结果信息，如果元素不存在则返回错误信息
        """
        x = xpath
        t:ChromiumTab=self.lastest_tab
        if e:= t(f"xpath:{x}"):
            t.set.upload_files(file_path)
            e.click(by_js=True)
            t.wait.upload_paths_inputted()
            return {"uploaded": True, "file_path": file_path, "xpath": xpath}
        else:
            raise LookupError(f"元素{x}不存在，无法触发上传文件")

        

    @property
    def lastest_tab(self) -> ChromiumTab:
        """获取最新标签页"""       
        return self.browser.latest_tab
    
    def send_enter(self) -> str:
        """向当前页面发送 enter 回车键"""
        tab = self.browser.latest_tab
        try:
            tab.actions.type(Keys.ENTER)
            return {"result":f'{tab.title} 网页发送 enter 回车键成功', "等价Python代码":f"tab.actions.type(Keys.ENTER)"}
        except Exception as e:
            raise RuntimeError(f"{tab.title} 网页发送 enter 回车键失败") from e
        
    def getInputElementsInfo(self) -> list:
        """获取当前标签页的所有可进行输入操作的元素，对元素进行输入操作前优先使用这个方法"""
        tab = self.browser.latest_tab
        js_code='''
        const inputElements = Array.from(document.querySelectorAll('input, select, textarea, button'));
        return inputElements.filter(el => !el.disabled); // 排除禁用的元素
        '''
        elements = tab.run_js(js_code)
        return elements
    
    def click_by_xpath(self, xpath: str) -> dict:
        """通过xpath点击当前标签页中某个元素,最好先获取页面dom信息,再决定Xpath的写法"""
        
        locator = f"xpath:{xpath}"
        element = self.browser.latest_tab.ele(locator, timeout=3)
        if not element:
            raise LookupError(f"元素{locator}不存在，需要getSimplifiedDomTree先获取元素信息")
        result = {"locator": locator, "element": str(element), "click_result": element.click(), "等价Python代码":f"tab.ele('{locator}', timeout=3).click()"}
        return result
    
    def click_by_containing_text(self, content: str, index: int = None) :
        """
        根据包含指定文本的方式点击网页元素。
        
        参数：
            content: 要查找的文本内容。
            index: 当匹配到多个元素时指定要点击的索引，默认不指定。

        返回：
            点击结果说明，或错误提示。
        """
        
        # 获取包含指定文本的所有元素，等待最多 3 秒
        elements = self.browser.latest_tab.eles(content, timeout=3)

        # 如果没有匹配到任何元素，返回错误提示
        if len(elements) == 0:
            raise LookupError(f"元素{content}不存在，需要getInputElementsInfo先获取元素信息")
        
        # 如果只找到一个元素，直接点击它
        if len(elements) == 1:
            elements[0].click()
            return {"clicked": True, "content": content, "index": 0}
        
        # 如果找到多个元素
        if len(elements) > 1:
            # 如果未指定 index，提示用户提供索引
            if index is None:
                raise ValueError(f"元素{content}存在多个，请调整 index 参数，index=0表示第一个元素")
            if index < 0 or index >= len(elements):
                raise IndexError(f"index 越界：{index}，可用范围 0..{len(elements)-1}")
            # 根据指定索引点击对应的元素
            elements[index].click()
            return {"clicked": True, "content": content, "index": index}
  
        
    
    def input_by_xapth(self, xpath: str, input_value: str, clear_first: bool = True) :
        """通过xpath给当前标签页中某个元素输入内容，最好先判断元素是否存在
        
        Args:
            xpath (str): 元素的XPath表达式
            input_value (str): 要输入的内容
            clear_first (bool): 是否先清除已有内容，默认为True
        
        Returns:
            Any: 输入操作的结果，如果元素不存在则返回错误信息
        """
        locator = f"xpath:{xpath}"
        if e := self.browser.latest_tab.ele(locator, timeout=4):
            result = {"locator": locator, "result": e.input(input_value, clear=clear_first), "等价Python代码":f"tab.ele('{locator}', timeout=4).input({input_value}, clear={clear_first})"}
            return result
        else:
            raise LookupError(f"元素{locator}不存在，需要getInputElementsInfo先获取元素信息")

    def get_body_text(self) -> str:
        """获取当前标签页的body的文本内容"""
        
        tab = self.browser.latest_tab
        body_text = tab('t:body').text
        r={"body_text":body_text,"等价Python代码":f"tab('t:body').text"}
        return r
    def run_js(self, js_code: str, as_expr: bool = False):
        """
        在当前标签页中运行JavaScript代码并返回执行结果
        查找网页元素，获取元素信息，操作网页元素优先使用这个方法
        
        Args:
            js_code (str): 要执行的JavaScript代码
            as_expr (bool): 是否将 js_code 按表达式执行。默认 False（函数体语义）。
        
        Returns:
            Any: JavaScript代码执行结果
        
        Note:
            想要获取执行的js代码的返回值，可以在js_code中使用return语句。
            或者传入 as_expr=True，把 js_code 当表达式求值（无需写 return）。
            想要获取异步函数的返回值，可以参考下面代码
            return (async (url) => {
                const response = await fetch(url);
                const data = await response.json();    
                return data;
            })("https://www.baidu.com/");
        """
        tab = self.browser.latest_tab
        result = tab.run_js(js_code, as_expr=as_expr)
        return result
        
    
    def run_cdp( self,cmd, **cmd_args) :
        """在当前标签页中运行谷歌CDP协议代码并获取结果
        
        Args:
            
            cmd: CDP协议命令
            **cmd_args: CDP命令参数
        
        Returns:
            Any: CDP命令执行结果
        
        Note:
            举例1说明 run_cdp('Page.stopLoading')
            举例2说明 run_cdp('Page.navigate', url='https://example.com')
        """
        result=self.browser.latest_tab.run_cdp(cmd, **cmd_args)
        return result
    def listen_cdp_event(self,event_name: str) :
        """设置监听CDP事件
        
         应该先运行cdp  命令 激活对应的域，比如  Network.enable
        """
        # b=Chromium(debug_port)
        def r(**event):
            if len(self.cdp_event_data) == self.cdp_event_data.maxlen:
                self.cdp_event_dropped += 1
            self.cdp_event_data.append({"event_name": event_name, "event_data": event})

        try:
            self.browser.latest_tab.driver.set_callback(event_name, r)
            return {"listening": True, "event_name": event_name}
        except Exception as e:
            raise RuntimeError(f"CDP event callback for '{event_name}' set failed") from e

    def get_cdp_event_data(self) -> list:
        """获取CDP事件回调函数收集到的数据"""
        return list(self.cdp_event_data)



    #region 监听网页接收的数据包  
    
    def get_url_with_response_listener(self,
        tab_url: str,
        mimeType: Literal[
            # 文本类
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "text/plain",
            "text/xml",
            "text/csv",
            "application/json",
            
            # 应用类
            "application/octet-stream",
            "application/zip",
            "application/pdf",    
            "multipart/form-data",
            "application/xml",
            
            # 图片类
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            "image/x-icon",
            
            # 音视频类
            "audio/mpeg",
            "audio/ogg",
            "video/mp4",
            "video/webm",
            "video/ogg"
        ],
        url_include: str = "."        
    ) :
        '''
        开启一个新的标签页，设置监听，访问tab_url,
        tab_url: 被监听的标签页的url
        mimeType: 需要监听的接收的数据包的mimeType类型
        url_include: 需要监听的接收的数据包的url包含的关键字
        refresh: 是否刷新页面,
        '''
        t = self.browser.new_tab("about:blank")

        t.run_cdp("Network.enable")

        def r(**event):
            _url = event.get("response", {}).get("url", "")
            _mimeType = event.get("response", {}).get("mimeType", "")
            
            if mimeType in _mimeType and url_include in _url:
                if len(self.response_listener_data) == self.response_listener_data.maxlen:
                    self.response_listener_dropped += 1
                self.response_listener_data.append({
                    "event_name": "Network.responseReceived",
                    "event_data": event
                })
        
        t.driver.set_callback("Network.responseReceived", r)
        t.get(tab_url)
        
        return {
            "listening": True,
            "tab_url": tab_url,
            "mimeType": mimeType,
            "url_include": url_include,
        }
    

    
    def response_listener_stop(self,clear_data:bool=False) -> dict:
        """关闭监听网页发送的数据包"""
        t=self.browser.latest_tab
        t.run_cdp("Network.disable")
        if clear_data:
            self.response_listener_data.clear()
            self.response_listener_dropped = 0
        return {"stopped": True, "cleared": clear_data}

    
    def get_response_listener_data(self) -> list:
        """获取监听到的数据,返回数据列表"""
        return list(self.response_listener_data)

    def get_current_tab_screenshot(self) -> bytes:
        """
        获取当前标签页的网页截图   
        
        Returns:
            bytes: 截图的二进制数据
        """
        t:ChromiumTab=self.browser.latest_tab
        screenshot=t.get_screenshot(as_bytes='jpeg')
        return screenshot
    
    def get_current_tab_screenshot_as_file(self,path:str=".",name:str="screenshot.png") -> str:
        """
        获取当前标签页的屏幕截图并保存为文件
        
        Args:
            path (str): 截图保存路径，默认为当前目录
        
        Returns:
            str: 截图的文件路径
        """ 

        screenshot=self.browser.latest_tab.get_screenshot(path=path,name=name)
        return screenshot 
    
    def get_current_tab_info(self) -> dict:
        """获取当前标签页的信息,包括url, title,  id"""
        tab =self.browser.latest_tab
        info = {
            "url": tab.url,
            "title": tab.title,          
            "id": tab.tab_id,
            "browser_address": self.browser._chromium_options.address,
            "active_connection": dict(self._last_connect_config),
        }
        return info
    
    def send_key(self, key: str) -> str:
        """向当前标签页发送特殊按键"""
        tab = self.browser.latest_tab
        k={"Enter": Keys.ENTER,
           "Backspace": Keys.BACKSPACE,
           "HOME": Keys.HOME,
           "END": Keys.END,
           "PAGE_UP": Keys.PAGE_UP,
           "PAGE_DOWN": Keys.PAGE_DOWN,          
           "DOWN": Keys.DOWN,
           "UP": Keys.UP,
           "LEFT": Keys.LEFT,
           "RIGHT": Keys.RIGHT,
           "ESC": Keys.ESCAPE,
           "Escape": Keys.ESCAPE,
           "Ctrl+C": Keys.CTRL_C,
           "Ctrl+V": Keys.CTRL_V,
           "Ctrl+A": Keys.CTRL_A,
           "Delete": Keys.DELETE,}
        if key not in k:
            raise ValueError(f"不支持的按键：{key}")
        try:
            tab.actions.type(k[key])
            return {"sent": key, "result": f"{tab.title} 网页发送 {key} 键成功"}
        except Exception as e:
            raise RuntimeError(f"{tab.title} 网页发送 {key} 键失败") from e
    
    def getSimplifiedDomTree(self) -> dict:
        """获取当前标签页的简化版DOM树"""
        from utils.codebox import domTreeToJson
        tab = self.browser.latest_tab
        dom_tree = tab.run_js(domTreeToJson)
        return dom_tree
 
    #region 拖动

    def move_to(self,xpath:str) -> dict:
        """鼠标移动悬停到指定xpath的元素上"""
        tab = self.browser.latest_tab
        locator = f"xpath:{xpath}"
        element = tab.ele(locator, timeout=3)
        if element:
            element.hover()
            result = {"locator": locator, "element": str(element)}
            return result
        else:
            raise LookupError(f"元素{locator}不存在，需要getSimplifiedDomTree先获取元素信息")
    def drag(self,xpath:str, offset_x: int, offset_y: int, duration: int = 1000) -> dict:
    
        """
        将元素拖动到指定偏移位置
        
        Args:
            xpath: 要拖动的元素xpath路径
            offset_x: x轴偏移量(像素)
            offset_y: y轴偏移量(像素)
            duration: 拖动持续时间(毫秒)，默认为1000
        
        Returns:
            dict: 包含偏移量和持续时间的字典，格式为{"offset_x": int, "offset_y": int, "duration": int}
            或 str: 当元素不存在时返回错误信息
        
        Raises:
            无显式抛出异常，但内部可能因元素不存在而返回错误信息
        """
        tab = self.browser.latest_tab
        if e:=tab.ele(f'xpath:{xpath}', timeout=3):
            tab.actions.move_to(e).wait(0.5).hold().move(offset_x, offset_y).release()
            result = {"offset_x": offset_x, "offset_y": offset_y, "duration": duration}
            return result
        else:
            raise LookupError(f"元素{xpath}不存在，需要getSimplifiedDomTree先获取元素信息")
