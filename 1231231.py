import requests
from DrissionPage import ChromiumPage, ChromiumOptions
from loguru import logger

logger.add("/root/cdy/log/app.log", rotation="00:00")

username = "LVH5EDJG"
password = "09424B9B270A"

def get_free_ip():
    PROXY_EXTRACT_API = "https://overseas.proxy.qg.net/get?key=LVH5EDJG&num=1&area=&isp=&format=txt&seq=\r\n&distinct=false"
    proxy_ip = requests.get(PROXY_EXTRACT_API).text
    return proxy_ip

def switch_ip(browser, ip_port=None):
    proxy_tab = browser.new_tab()
    browser.get_tab(proxy_tab.tab_id)
    if ip_port:
        ip, port = ip_port.split(":")
        proxy_tab.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/options.html#!/profile/proxy")
        proxy_tab.wait(2)
        proxy_tab.actions.click('x://input[@ng-model="proxyEditors[scheme].host"]', times=3).input(ip)
        proxy_tab.wait(2)
        proxy_tab.actions.click('x://input[@ng-model="proxyEditors[scheme].port"]', times=3).input(port)
        proxy_tab.wait(2)
        proxy_tab.ele('x://button[@title="Authentication"]').click()
        proxy_tab.wait(1)
        proxy_tab.actions.click('x://input[@placeholder="Username"]', times=3).input(username)
        proxy_tab.wait(1)
        proxy_tab.actions.click('x://input[@name="password"]', times=3).input(password)
        proxy_tab.wait(1)
        proxy_tab.ele('x://button[@type="submit"]').click()
        proxy_tab.wait(1)
        proxy_tab.ele('x://a[@ng-click="applyOptions()"]').click()
        proxy_tab.wait(1)

        proxy_tab.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/popup.html")
        proxy_tab.wait(1)
        proxy_tab.ele('x://a[contains(@title, "PROXY")]').click()
        proxy_tab.wait(2)

    else:
        proxy_tab.get("chrome-extension://padekgcemlokbadohgkifijomclgjgif/popup.html")
        proxy_tab.wait(1)
        proxy_tab.ele('x://span[contains(text(), "[Direct]")]').click()
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
    search_tab.get("https://www.google.com/")
    search_tab.ele('x://textarea[@class="gLFyf"]').input(keyword, clear=True)
    search_tab.ele('x://input[@class="gNO89b"]').click()
    search_tab.wait.ele_displayed('x://div[@role="navigation"]')

    found = False
    page = 1
    while not found:
        if page == 10:
            logger.error(f"已经翻页10页，未找到{keyword}。")
            break
        logger.info(f"===========这是第{page}页=============")
        a_tags = search_tab.eles('x://a[@class="zReHs"]')
        for a_tag in a_tags:
            href = a_tag.attr('href')
            title_text = a_tag.ele('x://h3/text()').text
            logger.info(title_text)
            logger.info(href)
            if 'com' in href:
                logger.success(f"找到目标链接: {href}")
                found = True
                a_tag.click()
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
            next_button = search_tab.ele('x://span[text()="Next"]')
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
    # \u521d\u59cb\u5316\u6d4f\u89c8\u5668
    browser = init_browser()
    ids = browser.tab_ids
    logger.info(ids)
    for id in ids:
        tab_id = browser.get_tab(id)

    # \u521b\u5efa\u7528\u4e8e\u8bf7\u6c42\u7f51\u7ad9\u7684 Tab
    request_tab = browser.new_tab()

    # \u91cd\u7f6e IP
    logger.info("重置 IP")
    switch_ip(browser)
    browser.get_tab(request_tab.tab_id)
    request_tab.get("https://tool.lu/ip/", retry=3)
    html_text = request_tab.ele('x://p[contains(text(), "\u4f60\u7684\u5916\u7f51IP\u5730\u5740\u662f")]').text
    logger.success(f">>> \u672c\u673a\u5f53\u524d\u7684 IP: {html_text}")

    for keyword in ["hi-pev", "轮椅", "租赁"]:
        while True:
            ip = get_free_ip()
            logger.info(f"~~~ \u5207\u6362 IP: {ip}")
            switch_ip(browser, ip)
            try:
                browser.get_tab(request_tab.tab_id)
                request_tab.refresh()
                html_text = request_tab.ele('x://p[contains(text(), "\u4f60\u7684\u5916\u7f51IP\u5730\u5740\u662f")]').text
                # browser.wait(1000)
                if ip.split(":")[0] in html_text:
                    logger.success(f">>> \u5207\u6362\u4ee3\u7406\u6210\u529f: {html_text}")
                    search(browser, keyword)
                    break
                else:
                    logger.error(f">>> \u5207\u6362\u4ee3\u7406\u5931\u8d25: {html_text}")
            except Exception as err:
                logger.error(f">>>> \u5207\u6362\u4ee3\u7406\u5931\u8d25: {err}")

    # \u7b49\u5f85\u5e76\u5173\u95ed\u6d4f\u89c8\u5668
    request_tab.wait(5)
    browser.quit()

# \u8fd0\u884c\u4e3b\u51fd\u6570
if __name__ == "__main__":
    main()
