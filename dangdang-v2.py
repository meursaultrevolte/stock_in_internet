import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import re
#from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from pandas import DataFrame
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import subprocess
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#driver.get不等待加载完毕
#desired_capabilities = DesiredCapabilities.CHROME
#desired_capabilities["pageLoadStrategy"] = "none"
options = Options()
#不显示log信息
options.add_argument('log-level=3')
#无头
options.add_argument('--headless')
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
#options.add_experimental_option("debuggerAddress", "127.0.0.1:9527")
driver = webdriver.Chrome(options=options)
driver.get("http://www.dangdang.com/")
time.sleep(2)
file = "条码.xls"
urls = data = pd.read_excel(file)
urls = urls.values.tolist()
for u in tqdm(urls):
    u = str(u[0])
    u1 = "https://search.dangdang.com/?key=" + u + "&act=input&filter=0%7C0%7C1%7C0%7C0%7C1%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0#J_tab"
    driver.get(u1)
    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'no_result')))
        print(u + "无货")
        data = [u, "无货"]
        df = pd.DataFrame(data).T
        df.to_csv('无货情况'+str(time.strftime('%Y-%m-%d',time.localtime(time.time())))+'.csv', header=False, mode='a', encoding='ANSI')
    except:
        print(u + "有货")
        pass
