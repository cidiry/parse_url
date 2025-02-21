import platform
import requests
from DrissionPage import ChromiumPage, ChromiumOptions
from loguru import logger

username = "18677334802"
password = "cidiry123"

def get_free_ip():
    # PROXY_EXTRACT_API = "https://api.douyadaili.com/proxy/?service=GetIp&authkey=B5mnCdblYycWKwByGEkx&num=1&lifetime=5&cstmfmt=%7Bip%7D%7Bport%7D"
    # http://18677334802:cidiry123@60.163.231.127:4591
    # proxy_ip = requests.get(PROXY_EXTRACT_API).text
    return "111.111.111.111:1234"

def switch_ip(browser, ip_port=None):
    proxy_tab = browser.new_tab()
    browser.get_tab(proxy_tab.tab_id)
    if ip_port:
        ip, port = ip_port.split(":")
        proxy_tab.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html#!/profile/proxy")
        proxy_tab.wait(2)
        proxy_tab.ele('x://input[@ng-model="proxyEditors[scheme].host"]').input(ip, clear=True)
        proxy_tab.wait(2)
        proxy_tab.ele('x://input[@ng-model="proxyEditors[scheme].port"]').input(port, clear=True)
        proxy_tab.wait(2)
        proxy_tab.ele('x://button[@title="Authentication"]').click()
        proxy_tab.wait(1)
        proxy_tab.ele('x://input[@placeholder="Username"]').input(username, clear=True)
        proxy_tab.wait(1)
        proxy_tab.ele('x://input[@placeholder="password"]').input(password, clear=True)
        proxy_tab.wait(1)
        proxy_tab.ele('x://button[@type="submit"]').click()
        proxy_tab.wait(1)
        proxy_tab.ele('x://a[@ng-click="applyOptions()"]').click()
        proxy_tab.wait(1)

        # \u63d0\u793a\u6846
        # txt = proxy_tab.handle_alert()
        # logger.info("\u63d0\u793a\u6846", txt)
        # proxy_tab.handle_alert(accept=False)
        proxy_tab.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/popup.html")
        proxy_tab.wait(1)
        proxy_tab.ele('x://a[contains(@title, "PROXY")]').click()
        proxy_tab.wait(2000)

    else:
        proxy_tab.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/popup.html")
        proxy_tab.wait(1)
        proxy_tab.ele('x://span[text()="[Direct]"]').click()
        proxy_tab.wait(2)

def init_browser():
    co = ChromiumOptions().set_paths(browser_path=r"/opt/google/chrome/google-chrome")
    # co.headless(True)
    co.set_argument('--no-sandbox')
    co.set_argument("--disable-gpu")
    co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

    co.set_timeouts(6, 6, 6)
    co.set_local_port(9211)
    return ChromiumPage(co)

def search(browser, keyword):
    search_tab = browser.new_tab()
    browser.get_tab(search_tab.tab_id)
    search_tab.get("https://www.baidu.com/")
    search_tab.ele('x://input[@id="kw"]').input(keyword, clear=True)
    search_tab.ele('x://input[@value="百度一下"]').click()
    search_tab.wait.ele_displayed('x://span[text()="百度为您找到以下结果"]')

    found = False
    page = 1
    while not found:
        logger.info(f"===========这是第{page}页=============")
        titles = search_tab.eles('xpath://h3/a/@href')
        for title in titles:
            title_text = title.text
            href = title.attr('href')
            logger.info(title.text)
            logger.info(href)
            if '百度百科' in title_text:
                logger.success(f"找到目标链接: {title.attr('href')}")
                found = True
                title.click()
                ids = browser.tab_ids
                logger.info(ids)
                tab_target = browser.get_tab(ids[0])
                tab_target.wait(5)
                tab_target.scroll.to_bottom()
                logger.success("已滚动到目标网址页面底部")
                tab_target.wait(5)
                tab_target.close()
                break

        if not found:
            next_button = search_tab.ele('x://a[text()="下一页 >"]')
            if next_button:
                next_button.scroll.to_see()
                next_button.click()
                search_tab.wait(3)
            else:
                logger.error("没有找到目标链接，且没有更多页面可翻")
                break
        page += 1

    search_tab.wait(3)
    search_tab.close()

def main():
    # 初始化浏览器
    browser = init_browser()
    ids = browser.tab_ids
    logger.info(ids)
    for id in ids:
        tab_id = browser.get_tab(id)

    # 创建用于请求网站的 Tab
    request_tab = browser.new_tab()

    # 重置 IP
    logger.info("重置 IP")
    switch_ip(browser)
    browser.get_tab(request_tab.tab_id)
    request_tab.get("https://tool.lu/ip/", retry=0)
    html_text = request_tab.ele('x://p[contains(text(), "你的外网IP地址是")]').text
    logger.success(f">>> 本机当前的 IP: {html_text}")

    for keyword in ["雷神", "雷神2", "雷神3"]:
        while True:
            ip = get_free_ip()
            logger.info(f"~~~ 切换 IP: {ip}")
            switch_ip(browser, ip)
            try:
                browser.get_tab(request_tab.tab_id)
                request_tab.refresh()
                html_text = request_tab.ele('x://p[contains(text(), "你的外网IP地址是")]').text
                if ip.split(":")[0] in html_text:
                    logger.success(f">>> 切换代理成功: {html_text}")
                    search(browser, keyword)
                    break
                else:
                    logger.error(f">>> 切换代理失败: {html_text}")
            except Exception as err:
                logger.error(f">>>> 切换代理失败: {err}")

    # 等待并关闭浏览器
    request_tab.wait(5)
    browser.quit()

# \u8fd0\u884c\u4e3b\u51fd\u6570
if __name__ == "__main__":
    main()