
# DrissionPage 使用教程

> 📌 DrissionPage® 是一个基于 Python 的网页自动化工具,能控制浏览器,功能强大，语法简洁优雅，代码量少，对新手友好.支持：Chromium 内核浏览器（如 Chrome 和 Edge）

---

## ✨ 安装

```bash
pip install -U DrissionPage
```

如需使用浏览器功能，请安装对应的浏览器驱动（如 ChromeDriver）并确保版本匹配。

---



## 🛠 启动或者连接浏览器(带配置),然后打开一个网页
默认状态下，程序会自动在系统内查找 Chrome 路径

```python
        
#!/usr/bin/env python
# -*- coding:utf-8 -*-
#-导入库
from DrissionPage import Chromium, ChromiumOptions
# 创建配置对象
co = ChromiumOptions()
co.headless(True)
co.set_argument('--start-maximized')
# 设置debug port
co.set_local_port('9222')
# 设置浏览器路径，不设置则默认是谷歌浏览器
co.set_browser_path(r'C:\chrome.exe')

# 创建浏览器对象
browser = Chromium(co)
tab = browser.latest_tab

#访问网页..
tab.get("https://www.baidu.com/")
print(tab.title)

```

---

## 📄 自动登录gitee网站

```python
# 使用默认模式访问网页
from DrissionPage import Chromium

# 启动或接管浏览器，并获取标签页对象
tab = Chromium().latest_tab
# 跳转到登录页面
tab.get('https://gitee.com/login')

# 定位到账号文本框，获取文本框元素
ele = tab.ele('#user_login')
# 输入对文本框输入账号
ele.input('您的账号')
# 定位到密码文本框并输入密码
tab.ele('#user_password').input('您的密码')
# 点击登录按钮
tab.ele('@value=登 录').click()
```

---

## 🔍 查找元素

支持 CSS 选择器、XPath 和自定义选择器：

```python
# 查找tag为div的元素
ele = tab.ele('tag:div')  # 原写法
ele = tab('t:div')  # 简化写法

# 用xpath查找元素
ele = tab.ele('xpath://****')  # 原写法
ele = tab('x://****')  # 简化写法

# 查找text为'something'的元素
ele = tab.ele('text=something')  # 原写法
ele = tab('tx=something')  # 简化写法
```

---

## ✏️ 获取电商网站的评论

```python

#!/usr/bin/env python
# -*- coding:utf-8 -*-# 

# 电脑内需要提取安装谷歌浏览器或者其他chromium内核的浏览器  比如 edge浏览器  qq浏览器  360浏览器


import time
from DrissionPage import Chromium
from loguru import logger

# 设置日志记录到文件
logger.add("JD_comment.log", format="{time} {message}")

# 初始化浏览器
browser = Chromium()

# 打开京东首页
main_tab = browser.new_tab('https://www.jd.com/')

# 获取搜索框并输入关键词
search_input = main_tab.ele('tag:input@@id=key')
search_input.input('小米手机')

# 点击搜索按钮
main_tab('tag:button@@aria-label=搜索').click()

# 获取搜索结果列表
search_results = main_tab.eles('t:li@@class=gl-item')

# 打印每个搜索结果的文本
# for result in search_results:
#     logger.info(result)

# 点击搜索结果中的第二个商品以打开商品详情页
product_detail_tab = search_results[1].ele('t:a').click.for_new_tab()
# 点击评论标签页
product_detail_tab.ele('@data-anchor=#comment').click()

# 获取并打印商品评论
def get_comments(tab):
    for comment in tab.eles('t:div@@class=comment-item'):
        # logger.info(comment)
        
        logger.info(comment('.comment-con').text)  # 记录评论内容
        if recomment:=comment.ele('.recomment',timeout=2):
            logger.error(recomment.text)
        
        time.sleep(2)

# 获取第一页评论并点击下一页
get_comments(product_detail_tab)
product_detail_tab.ele('t:a@@rel=2').click()

# 循环获取剩余页码的评论
for _ in range(4):
    get_comments(product_detail_tab)
    product_detail_tab.ele('下一页').click()
```

---

## 📦 截图

```python
# 对整页截图并保存
tab.get_screenshot(path='tmp', name='pic.jpg', full_page=True)
```

---

## 📂 文件下载

```python
from DrissionPage import Chromium

tab = Chromium().latest_tab
tab.set.download_path('save_path')  # 设置文件保存路径
tab.set.download_file_name('file_name')  # 设置重命名文件名
tab('t:a').click()  # 点击一个会触发下载的链接
tab.wait.download_begin()  # 等待下载开始
tab.wait.downloads_done()  # 等待下载结束
```

---

## 📤 文件上传

```python
# 设置要上传的文件路径
tab.set.upload_files('demo.txt')
# 点击触发文件选择框按钮
btn_ele.click()
# 等待路径填入
tab.wait.upload_paths_inputted()
```
---

## 📤 浏览器等待

```python
tab.wait(10)  # 等待10秒
```

---
## 📤 关闭浏览器

```python
browser.quit()
```
## 📤 关闭标签页
```python
tab.close()
```

---
## 📤 访问指定小红书页面，监听并下载评论json数据
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小红书评论数据下载脚本

功能：访问指定小红书页面，监听并下载评论json数据
"""

import json
import time
from DrissionPage import Chromium, ChromiumOptions
from loguru import logger

# 配置日志
logger.add("xiaohongshu_comment.log", format="{time} {level} {message}")

def download_xiaohongshu_comments(url: str, output_file: str):
    """
    下载小红书评论数据

    :param url: 小红书页面URL
    :param output_file: 输出文件路径
    """
    try:
        # 配置浏览器选项
        co = ChromiumOptions()
        co.headless(False)  # 显示浏览器窗口
        co.set_local_port('9222')  # 设置调试端口

        # 创建浏览器对象
        browser = Chromium(co)
        tab = browser.latest_tab

        # 监听网络请求
        logger.info("开始监听评论数据...")
        tab.listen.start('comment')  # 监听包含comment的请求
        logger.info(f"正在访问页面: {url}")
        tab.get(url)
        tab.eles(".title")[4].click()  # 点击视频

        # 等待足够时间获取数据
        time.sleep(4)

        # 获取监听到的数据
        data = tab.listen.wait()
        if not data:
            logger.error("未获取到评论数据")
            return

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data.response.body, f, ensure_ascii=False, indent=4)

        logger.success(f"评论数据已保存到: {output_file}")

    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
    finally:
        # 关闭浏览器
        if 'browser' in locals():
            browser.quit()

if __name__ == '__main__':
    # 配置参数
    target_url = 'https://www.xiaohongshu.com/explore/'
    output_path = "comments_data.json"
    # 执行下载
    download_xiaohongshu_comments(target_url, output_path)
```

---




## 🔗 官方资源

- GitHub 项目主页: [https://github.com/g1879/DrissionPage](https://github.com/g1879/DrissionPage)
---



> 本教程适合初学者快速上手，更多高级功能请参考官方文档。
https://drissionpage.cn/