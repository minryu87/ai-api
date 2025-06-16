from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests
import re

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-browser-side-navigation')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    driver = wd.Chrome(options=chrome_options)
    return driver

def scroll_page(driver):
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2.0)
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_page_height == last_page_height:
            break
        last_page_height = new_page_height
    return driver

def get_url_title_in_html_source(html_source, css_selector):
    titles, urls = [], []
    soup = BeautifulSoup(html_source, 'lxml')
    datas = soup.select(css_selector)
    for data in datas:
        title = data.text.replace('\n', '')
        url = "https://www.youtube.com" + data.get('href')
        titles.append(title)
        urls.append(url)
    return titles, urls

def get_channel_video_url_list(channel_url):
    driver = get_chrome_driver()
    driver.get(channel_url)
    driver = scroll_page(driver=driver)
    html_source = driver.page_source
    driver.quit()
    url_title_css_selector = "ytd-grid-video-renderer.style-scope.ytd-grid-renderer > div#dismissible > div#details > div#meta > h3.style-scope.ytd-grid-video-renderer > a#video-title"
    titles, urls = get_url_title_in_html_source(html_source=html_source, css_selector=url_title_css_selector)
    return titles, urls

def crawl_youtube_channel(channel_name: str):
    base_url = f"https://www.youtube.com/@{channel_name}"
    videos_url = f"{base_url}/videos"
    shorts_url = f"{base_url}/shorts"
    # 동영상 목록 크롤링
    titles, urls = get_channel_video_url_list(videos_url)
    # 결과 예시: 동영상 제목, url만 반환
    result = []
    for title, url in zip(titles, urls):
        result.append({"title": title, "url": url})
    return {
        "channel": channel_name,
        "videos": result,
        "videos_count": len(result)
    }
