from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import undetected_chromedriver as uc  # type: ignore

options = uc.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--headless=new")
options.add_argument("--incognito")
driver = uc.Chrome(options=options)


url = "https://www.dcard.tw/forum/popular"
driver.get(url)


# 使用 Selenium 模擬往下滑動以載入更多內容
scroll_times = 3
for _ in range(scroll_times):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
soup = BeautifulSoup(driver.page_source, "html.parser")

time.sleep(1)
popular_info_list = []
div = soup.find("div", class_="d_hk_5j0kmn d_2l_a l13ztl4h")
# print(div.prettify())
# time.sleep(10)
a_tags = div.find_all("a")
print(f"a_tags = {len(a_tags)}")
id = 1
for a_tag in a_tags:

    title_div = a_tag.find(
        "div", class_="d_gz_5t7tpg d_cn_1t d_xa_2b d_tx_2c d_lc_1u l18we7l8"
    )

    if title_div and a_tag.get("href"):
        data = {
            "id": id,
            "title": title_div.text.strip(),
            "link": "https://www.dcard.tw" + a_tag.get("href"),
        }
        popular_info_list.append(data)
    id += 1

print(len(popular_info_list))
with open("popular_list.json", "w", encoding="utf-8") as f:
    json.dump(popular_info_list, f, ensure_ascii=False, indent=2)
