from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import re
import random

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService


def reOpenBrowser():
    options = FirefoxOptions()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
    ]
    # 強化指紋偽裝
    options.set_preference("general.useragent.override", random.choice(user_agents))
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("media.navigator.enabled", False)
    options.set_preference("media.peerconnection.enabled", False)
    options.set_preference("privacy.trackingprotection.enabled", True)
    options.set_preference("privacy.resistFingerprinting", True)
    # 建議不要啟用 headless
    driver = webdriver.Firefox(options=options)
    # 進一步移除 webdriver 屬性與指紋
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});"
        "Object.defineProperty(navigator, 'languages', {get: () => ['zh-TW', 'zh', 'en-US', 'en']});"
    )
    return driver


def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002700-\U000027bf"
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


def remove_punctuation(text):
    return re.sub(r"[^\w\s]", " ", text)


def random_human_scroll(driver):
    # 隨機滑動頁面，模擬人類行為
    total_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(random.randint(2, 5)):
        scroll_y = random.randint(0, total_height)
        driver.execute_script(f"window.scrollTo(0, {scroll_y});")
        time.sleep(random.uniform(0.5, 1.5))


def is_turnstile_page(soup):
    # 判斷是否遇到 Cloudflare Turnstile 驗證頁
    if soup.find("iframe", {"title": "Just a moment..."}):
        return True
    if soup.find("div", string=re.compile("Cloudflare")) and soup.find(
        "input", {"name": "cf-turnstile-response"}
    ):
        return True
    return False


# 初始化 Firefox driver
driver = reOpenBrowser()
with open("popular_list.json", "r", encoding="utf-8") as f:
    popular_list = json.load(f)

restart_every = 20
scroll_times = 3
count = 0
id = 1
for item in popular_list:

    title = item.get("title")
    link = item.get("link")
    print(f"Processing {title}...")
    driver.get(link)
    # time.sleep(random.uniform(2, 4))
    time.sleep(10000)
    random_human_scroll(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # turnstile偵測
    retry = 0
    while is_turnstile_page(soup) and retry < 3:
        print("偵測到 Cloudflare Turnstile，等待並重試...")
        time.sleep(random.uniform(10, 20))
        driver.refresh()
        time.sleep(random.uniform(2, 4))
        random_human_scroll(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        retry += 1

    time.sleep(3)
    for _ in range(scroll_times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 2))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    count += 1
    if count % restart_every == 0:
        print("重啟 driver 釋放資源")
        driver.quit()
        driver = reOpenBrowser()

    content_divs = soup.find_all(
        "div",
        class_="d_a5_22 d_eg_6y7mag d_s7_2o d_2l_f d_9w_25 d_mk_f7aqx6 d_mh_140cd6v d_mg_140cd6v w1n8s3eg",
    )
    href_list = []

    # 找到所有 class 為 d_bq_1s ... tqmqygc 的 span，然後在裡面找 a 標籤
    for span in soup.find_all(
        "span",
        class_="d_bq_1s d_xa_2b d_1lwy0fn_2s d_jmu8dv_1v d_2pznp0_l52nlx d_dlv3ej_7 tqmqygc",
    ):
        a_tag = span.find("a", class_="d_2nx2hs_8stvzk")
        if a_tag:
            href = a_tag.get("href")
            if href:
                href_list.append("https://www.dcard.tw" + href)
    print("所有的href:", len(href_list))

    for link in href_list[0:100]:

        driver.get(link)
        time.sleep(random.uniform(1, 2))
        random_human_scroll(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        retry = 0
        while is_turnstile_page(soup) and retry < 3:
            print("偵測到 Cloudflare Turnstile，等待並重試...")
            time.sleep(random.uniform(10, 20))
            driver.refresh()
            time.sleep(random.uniform(1, 2))
            random_human_scroll(driver)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            retry += 1

        span_texts = []
        # 抓取文章標題
        title_tag = soup.find(
            "h1",
            class_="d_xm_2v d_7v_5 d_hh_29 d_jm_1r d_d8_2s d_cn_31 d_gk_2n d_f6vyfi_2s d_178gzt7_23 d_8viy46_14e6m10 t17vlqzd",
        )
        if title_tag:
            titles = title_tag.get_text(strip=True)
            print("文章標題:", titles)
            # 只保留中文字，標點符號換空格
            text = re.sub(r"[^\u4e00-\u9fff]", " ", titles)
            text = re.sub(r"\s+", " ", text).strip()

            if text:
                span_texts.append(text)
                # print(text)
        else:
            print("找不到文章標題")
            time.sleep(1000)

        span_texts.append(" ")
        # 抓取指定 div 內的所有 span 文字
        target_div = soup.find("div", class_="d_xa_34 d_xj_2v c1ehvwc9")
        if target_div:
            spans = target_div.find_all("span")
            for span in spans:
                # 只保留中文字，標點符號換空格
                text = span.get_text()
                text = re.sub(r"[^\u4e00-\u9fff]", " ", text)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    span_texts.append(text)
                    # print(text)
        else:
            print("找不到指定span 文字的div")

        file_name = f"article_{id}.txt"

        with open(file_name, "a", encoding="utf-8") as f:
            for line in span_texts:
                f.write(line)
            f.write("\n")
    id += 1

# 關閉瀏覽器
driver.quit()
