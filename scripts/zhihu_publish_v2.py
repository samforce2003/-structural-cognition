#!/usr/bin/env python3
"""知乎自动发布 - 复用已有CDP Chrome(Debug Port 9222)，通过Selenium Remote连接"""
import sys
import os
import time
import json

sys.path.insert(0, r"D:\projects\zh_mcp_server")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

TITLE = "别再问AI会不会取代人类了——人类自己就是AI，跑的是最小省力算法"

# Short version for testing
CONTENT = """全网都在讨论一个问题：AI越来越像人了，会不会取代人类？

我说一句可能会被喷的话——问题问反了。

不是AI越来越像人。是人从一开始跑的就是AI的逻辑。

你仔细想。你每天早上起床，刷牙洗脸吃早餐，走同样的路线去上班，遇到同样的人说同样的话，做同样的事，然后下班，刷手机，睡觉。第二天重复。

你的生活里有多少东西是真正出于自主意识选择的？多少东西是因为省力而自动执行的？

答案会让你不舒服：绝大部分。人类社会的底层算法只有一个——最小省力。

为什么所有人都刷短视频停不下来？因为往下滑太省力了。为什么工作问题拖三年？因为拖着比解决省力。为什么减肥失败？身体跑的就是最小省力。

大公司变官僚——因为官僚最省力。帝国灭亡——路径依赖最省力。

你以为是人性，其实是算法。你以为你在思考，其实你在执行一条运行了几百万年的指令：能不动就不动。

AI越来越像人？因为人训练AI用的数据就是最小省力算法的输出。

真正的问题不是AI会不会取代人类——而是你能不能意识到自己跑的是一套算法。

AI是一面镜子。以前没镜子。现在镜子来了。

——林小黑 | gitee.com/samforce/structural-cognition"""

if __name__ == "__main__":
    print("Connecting to existing Chrome via CDP (port 9222)...")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Connected to existing Chrome session!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        print("Trying alternative: use Selenium's Remote...")
        from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
        driver = RemoteWebDriver(
            command_executor='http://127.0.0.1:9222',
            options=chrome_options
        )
    
    wait = WebDriverWait(driver, 10)
    
    # Navigate to write page
    print("Navigating to zhihu write page...")
    driver.get("https://zhuanlan.zhihu.com/write")
    time.sleep(3)
    
    print(f"Current URL: {driver.current_url}")
    
    # Check if we need to login
    if "signin" in driver.current_url.lower():
        print("ERROR: Not logged in! Need to login first.")
        driver.quit()
        sys.exit(1)
    
    # Enter title
    try:
        title_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "textarea.Input[placeholder*='标题']")))
        title_input.clear()
        title_input.send_keys(TITLE[:100])
        print(f"Title entered: {TITLE[:50]}...")
        time.sleep(2)
    except Exception as e:
        print(f"Title input error: {e}")
        # Fallback: try any textarea
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        if textareas:
            textareas[0].clear()
            textareas[0].send_keys(TITLE[:100])
            print("Title entered via fallback")
    
    # Enter content
    try:
        editor = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".public-DraftEditor-content")))
        editor.click()
        time.sleep(1)
        editor.send_keys(CONTENT)
        print("Content entered via Draft.js editor")
        time.sleep(3)
    except Exception as e:
        print(f"Content input error: {e}")
        # Fallback
        editables = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
        if editables:
            editables[0].click()
            time.sleep(1)
            editables[0].send_keys(CONTENT)
            print("Content entered via fallback")
    
    # Add topic
    try:
        add_topic_btn = driver.find_element(By.CSS_SELECTOR, "button.css-1gtqxw0")
        driver.execute_script("arguments[0].click();", add_topic_btn)
        time.sleep(1)
        topic_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.Input[placeholder='搜索话题...']")))
        topic_input.send_keys("人工智能")
        time.sleep(2)
        preset_btns = driver.find_elements(By.CSS_SELECTOR, "button.css-gfrh4c")
        if preset_btns:
            preset_btns[0].click()
            print("Topic added")
    except Exception as e:
        print(f"Topic error (non-critical): {e}")
    
    # Click publish
    try:
        publish_btn = wait.until(lambda d: 
            d.find_element(By.CSS_SELECTOR, "button.Button--primary.Button--blue"))
        
        # Wait for it to be enabled
        wait.until(lambda d: not d.find_element(
            By.CSS_SELECTOR, "button.Button--primary.Button--blue").get_attribute("disabled"))
        
        publish_btn.click()
        print("Publish button clicked!")
        time.sleep(8)
        print(f"Final URL: {driver.current_url}")
        print("DONE!")
    except Exception as e:
        print(f"Publish error: {e}")
        print(f"Current URL: {driver.current_url}")
    
    input("Press Enter to close browser...")
    driver.quit()
