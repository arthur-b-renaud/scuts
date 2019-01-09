# -*- coding: utf-8 -*
import time, traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
from lxml import etree
from io import BytesIO
parser = etree.HTMLParser()
import os, time
import os.path as op
import pathlib
from PIL import Image
from urllib.parse import urlparse
import requests
import shutil
import imghdr
import gzip
import magic
import pandas as pd
import urllib3
import asyncio
from proxybroker import Broker
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def download_img(img_url, orig_img_path, shop_id="test", decode_content=False, debug=False):
    """Utility for reliably get an image, handling most weirdness from the net (ex. : images named ".jpg" that actually are JPEG.
    WARNING ! this won't work in Windows, because of the use of the "/tmp" directory

    :param img_url: The image url
    :param orig_img_path: The
    :param verbose:
    :param shop_id:
    :param decode_content:
    :param gzipped:
    :param debug:
    :return: The complete path of the Image downloaded or None
    """

    response = requests.get(img_url, stream=True, verify=False, headers=headers)
    response.raw.decode_content = decode_content

    tmp_file_path = '/tmp/' + shop_id + 'mhers_tmp_{}.imgtype'.format(abs(hash(img_url)))
    with open(tmp_file_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    if 'Content-Type' in response.headers:
        if 'text/html' in response.headers['Content-Type']:
            print("WARNING ! the url that has been called sends back html, with url : " + img_url)
            return None

    gzipped = False
    if debug:
        print(response.headers)

    if 'Content-Encoding' in response.headers:
        if 'gzip' in response.headers['Content-Encoding']:
            gzipped = True

    if gzipped:
        try:
            f = gzip.open(tmp_file_path, 'rb')
            file_content = f.read()
            with open(tmp_file_path, 'wb') as out_file:
                out_file.write(file_content)
            f.close()
        except:
            print('WARNING ! Falsely attributed to GZIP', img_url)

    if imghdr.what(tmp_file_path) is not None:
        if "webp" in magic.from_file(tmp_file_path, mime=True).lower():
            img_path = orig_img_path.split('.')[0] + '.png'
            im = Image.open(tmp_file_path).convert("RGB")
            im.save(img_path, "png")
            if not debug and op.exists(tmp_file_path):
                os.remove(tmp_file_path)
            return img_path

        img_path = orig_img_path.split('.')[0] + '.' + imghdr.what(tmp_file_path)
        shutil.copyfile(tmp_file_path, img_path)
        if not debug and op.exists(tmp_file_path):
            os.remove(tmp_file_path)
        return img_path

    elif "image" in magic.from_file(tmp_file_path, mime=True):
        img_path = orig_img_path.split('.')[0] + '.' + magic.from_file(tmp_file_path, mime=True).split('/')[-1]
        shutil.copyfile(tmp_file_path, img_path)
        if not debug and op.exists(tmp_file_path):
            os.remove(tmp_file_path)
        return img_path

    else:
        if debug:
            print("WARNING Img not downloaded: ", tmp_file_path, img_url, imghdr.what(tmp_file_path))
        return None


def clean_url(href, root_url):
    """
    A utility for scraping. Transforms a name into full-fledge url
    :param href:
    :param root_url:
    :return:
    """
    res = href
    if href.startswith('//'):
        assert root_url.split(':')[0].lower() in ('http', 'https')
        res = root_url.split(':')[0] + ':' + href
    elif href.startswith('/'):
        res = os.path.join(root_url, href[1:])
    elif href.startswith('./'):
        res = os.path.join(root_url, href[2:])
    elif href.startswith('../'):
        res = os.path.join(root_url, href[3:])
    if not res.startswith('http'):
        res = os.path.join(root_url, href)
    return res


class CustomDriver:
    """A driver that handles all the heavy-lifting for scraping and uses good practices
    """

    def __init__(self, headless=False, download_images=False, proxy_host=None, proxy_port=None, timeout=10,
                 firefox=False, user_agent=None):
        self.headless = headless
        self.driver = None
        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port) if proxy_port else None
        self.timeout = timeout
        self.download_images = download_images
        if not user_agent:
            self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
        else:
            self.user_agent = user_agent

        # Lazy-loading params
        self.firefox = firefox
        self.driver_exists = False
        self.proxies_list = []

        with open(os.path.join(os.path.dirname(__file__), 'ressources/jquery-1.9.1.min.js'), 'r') as jquery_js:
            self.jquery = jquery_js.read()  # read the jquery from a file

    def create_driver_if_needed(self):
        if not self.driver_exists:
            if self.firefox:
                self.init_driver_firefox()
            else:
                self.init_driver_chrome()
            self.driver_exists = True

    def get_new_proxies(self, countries=None):
        l = []
        async def show(proxies):
            while True:
                proxy = await proxies.get()
                l.append(proxy)
                if proxy is None:
                    break
                # print('Found proxy: %s' % proxy)

        proxies = asyncio.Queue()
        broker = Broker(proxies)
        tasks = asyncio.gather(
            broker.find(types=['HTTP', 'HTTPS'], countries=countries, limit=10),
            show(proxies))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)
        self.proxies_list.extend(l)
        self.proxies_list = [x for x in self.proxies_list if x]

    def init_driver_chrome(self, total_width=1600, total_height=900, userProfile=None):
        """ Inits a Chrome Driver
        :param total_width: size of the window
        :param total_height: size of the window
        :param userProfile: path to userProfile
        :return:
        """
        print('Initing Chrome Driver')
        chrome_options = Options()
        chrome_options.add_argument("user-agent=" + self.user_agent)
        options = webdriver.ChromeOptions()
        if userProfile:
            options.add_argument("user-data-dir={}".format(userProfile))
        options.add_experimental_option("excludeSwitches",
                                        ["ignore-certificate-errors", "safebrowsing-disable-download-protection",
                                         "safebrowsing-disable-auto-update", "disable-client-side-phishing-detection"])
        if self.headless:
            chrome_options.add_argument("--headless")
            # chrome_options.binary_location = '/usr/bin/google-chrome'

        if self.proxy_host and self.proxy_port:
            print("Using proxy", self.proxy_host + ':' + str(self.proxy_port))
            chrome_options.add_argument('--proxy-server=https://%s' % self.proxy_host + ':' + str(self.proxy_port))

        chrome_options.add_argument("--window-size={total_width},{total_height}".format(total_width=total_width, total_height=total_height))
        chrome_options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def init_driver_firefox(self, total_width=1600, total_height=900):
        """ Inits a FireFox Driver
        :param total_width: size of the window
        :param total_height: size of the window
        :param userProfile: path to userProfile
        :return:
        """
        options = Options()
        fp = FirefoxProfile()

        if self.headless:
            options.add_argument("--headless")

        if not self.download_images:
            fp.set_preference('permissions.default.image', 2)
            fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        if self.proxy_host and self.proxy_port:
            profile = webdriver.FirefoxProfile()
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", self.proxy_host)
            profile.set_preference("network.proxy.http_port", int(self.proxy_port))
            profile.set_preference("network.proxy.ssl", self.proxy_host)
            profile.set_preference("network.proxy.ssl_port", int(self.proxy_port))
            fp.update_preferences()
            self.driver = webdriver.Firefox(options=options, firefox_profile=profile)
        elif self.proxy_port or self.proxy_host:
            raise(Exception('If you want to use a proxy, please provide proxy_host and proxy_port'))
        else:
            self.driver = Firefox(options=options, firefox_profile=fp)
        self.driver.set_window_size(total_width, total_height)

    def __del__(self):
        # self.quit()
        pass

    def quit(self):
        self.driver_exists = False
        try:
            self.driver.quit()
        except Exception:
            pass

    def respawn(self, lazyload=True):
        """Recreates a driver if needed
        :param lazyload:
        :return:
        """
        self.quit()
        if not lazyload:
            self.create_driver_if_needed()
            self.driver_exists = False
        else:
            self.driver_exists = False

    def waitclick(self, xpath, center_button=True, ctrl=False, timeout=None, silent=False):
        try:
            timeout = timeout if timeout else self.timeout
            if center_button:
                element = self.driver.find_element_by_xpath(xpath)
                self.driver.execute_script(
                    "var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);"
                    + "var elementTop = arguments[0].getBoundingClientRect().top;"
                    + "window.scrollBy(0, elementTop-(viewPortHeight/2));", element)

            if not ctrl:
                ui.WebDriverWait(self.driver, timeout * 1).until(lambda browser: browser.find_elements_by_xpath(xpath))
                self.driver.find_element_by_xpath(xpath).click()
            else:
                ui.WebDriverWait(self.driver, self.timeout * 1).until(lambda browser: browser.find_elements_by_xpath(xpath))
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL)
                self.driver.find_element_by_xpath(xpath).click()
                actions.key_up(Keys.CONTROL)
                actions.perform()
        except Exception:
            if not silent:
                print('ERROR waitclick', xpath)
                print(traceback.format_exc())
            return False
        return True

    def text_input(self, text, xpath, enter=False, clear=True, timeout=2):
        timeout = timeout if timeout else self.timeout
        ui.WebDriverWait(self.driver, timeout).until(lambda browser: browser.find_elements_by_xpath(xpath))
        if clear:
            self.driver.find_element_by_xpath(xpath).clear()
        self.driver.find_element_by_xpath(xpath).send_keys(text)
        if enter:
            self.driver.find_element_by_xpath(xpath).send_keys(Keys.ENTER)

    def wait_for_xpath(self, xpath, timeout=None, is_enabled=False):
        timeout = timeout if timeout else self.timeout
        if is_enabled:
            try:
                ui.WebDriverWait(self.driver, timeout * 1).until(lambda browser: browser.find_elements_by_xpath(xpath).is_enabled())
                return True
            except:
                return False
        else:
            try:
                ui.WebDriverWait(self.driver, timeout * 1).until(lambda browser: browser.find_elements_by_xpath(xpath))
                return True
            except:
                return False

    def save_page(self, destination, scroll_to_bottom=False, get_inner_html=False):
        if scroll_to_bottom:
            self.scroll_to_bottom()
        if get_inner_html:
            page = self.driver.execute_script("return document.body.innerHTML")
        else:
            page = self.driver.page_source
        file_ = open(destination, 'w')
        file_.write(page)
        file_.close()

    def scroll_to_bottom(self, smooth_scroll_steps=2, next_button_click_xpath=None):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.smooth_scroll(smooth_scroll_steps)

            if next_button_click_xpath and self.wait_for_xpath(next_button_click_xpath, timeout=3):
                print('Clicking next', next_button_click_xpath)
                self.waitclick(next_button_click_xpath, timeout=3)

            # Wait to load page
            time.sleep(1.5)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def click_to_bottom(self, next_button_click_xpath):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.smooth_scroll()
            print("Sleeping", sleep(5))
            if self.wait_for_xpath(next_button_click_xpath, timeout=5):
                button_to_click = self.driver.find_element_by_xpath(next_button_click_xpath)
                action = ActionChains(self.driver)
                action.move_to_element(button_to_click).click().perform()
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def smooth_scroll(self, step=10, sleep_time=0.5):
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            for k in range(step):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*%s);" % ((k+1)/step))
                sleep(sleep_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            sleep(sleep_time*5)
            if new_height == last_height:
                break
            last_height = new_height

    def get(self, url, verbose=False):
        """Get the url in the driver. A local path is also valid
        :param url:
        :param verbose:
        :return:
        """
        assert type(url) == str

        # Lazy-loading
        self.create_driver_if_needed()

        if verbose:
            print("GET: ", url)

        if 'http' not in url and op.exists(url):
            # This is used to open local htmls
            html_path = url
            self.html_path = html_path
            self.f_uri = pathlib.Path(html_path).as_uri()
            self.driver.get(self.f_uri)

        elif 'http' in url:
            self.driver.get(url)

        else:
            raise Exception('Url does not exist : ' + url)
        return self

    def get_with_proxy(self, url, countries=None, verbose=False):
        """Get the url in the driver. A local path is also valid
        :param url:
        :param verbose:
        :return:
        """
        assert type(url) == str

        if not self.proxies_list:
            self.get_new_proxies(countries=countries)

        prox = self.proxies_list.pop()

        self.proxy_host = prox.host
        self.proxy_port = prox.port

        # Lazy-loading
        self.create_driver_if_needed()

        if verbose:
            print("GET: ", url, 'with proxy', prox)

        if 'http' not in url and op.exists(url):
            raise Exception('Proxied requests should not be made towards localhost')

        elif 'http' in url:
            from selenium.common.exceptions import TimeoutException, WebDriverException
            try:
                self.driver.set_page_load_timeout(self.timeout)
                self.driver.get(url)
            except TimeoutException as ex:
                self.quit()
                print("Exception has been thrown. " + str(ex))
                self.get_with_proxy(url, verbose=verbose)
            except WebDriverException as ex:
                self.quit()
                print("Exception has been thrown. " + str(ex))
                self.get_with_proxy(url, verbose=verbose)
        else:
            raise Exception('Url does not exist : ' + url)
        return self

    def check_exists_by_xpath(self, xpath):
        """Checks if a xpath exists in the current driver page
        :param xpath:
        :return:
        """
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        except Exception:
            print("check_exists_by_xpath error raised", traceback.format_exc())
            return False
        return True

    def fullpage_screenshot(self, dest_png_fpath, scroll=True, nb_pixels_to_scroll_per_second=2000,
                            scroll_wait=0.2, window_width=1100, verbose=False):
        """Screenshots the existing page
        :param dest_png_fpath: the path to the image to be screenshot
        :param nb_pixels_to_scroll_per_second:
        :param scroll_wait:
        :param window_width:
        :param verbose:
        :return:
        """
        # total_width = self.driver.execute_script("return document.body.offsetWidth")
        total_width = window_width
        self.driver.execute_script(self.jquery)  # active the jquery lib
        total_height = self.driver.execute_script("return $(document).height()")

        if verbose:
            print(total_width, total_height)
        scroll_steps = int(total_height / (nb_pixels_to_scroll_per_second * scroll_wait) + 0.5)
        if scroll:
            self.smooth_scroll(scroll_steps, scroll_wait)
        total_height = self.driver.execute_script("return $(document).height()")
        self.driver.execute_script("window.scrollTo(0,0);")

        if verbose:
            print(total_width, total_height)
        try:
            self.driver.set_window_size(total_width, total_height)
        except Exception:
            traceback.print_exc()
        self.driver.get_screenshot_as_file(dest_png_fpath)

    def get_largest_img_url(self, verbose=False):
        """Utility to "smartly" find the largest image in the DOM. For dev purpose only
        :param verbose:
        :return:
        """
        assert self.driver_exists
        l = self.driver.find_elements_by_xpath('//img')  # + self.driver.find_elements_by_xpath('//a[@href]')
        l.extend(self.driver.find_elements_by_xpath('//*[contains(@href, ".png")]'))
        l.extend(self.driver.find_elements_by_xpath('//*[contains(@href, ".jpg")]'))
        l.extend(self.driver.find_elements_by_xpath('//*[contains(@href, ".jpeg")]'))

        if len(l) > 1000:
            raise Exception('Too much elements to process')

        def is_img_url_candidate(s):
            if any(x in s.lower() for x in ['png', 'jpg', 'jpeg', 'gif']) and "/" in s:
                return True
            return False

        def get_img_area(fpath):
            if not fpath or not os.path.exists(fpath) or not "image" in magic.from_file(fpath, mime=True):
                return 0
            with Image.open(fpath) as img:
                width, height = img.size
            return width * height

        def get_real_img_size(url, page_url):
            if verbose:
                print('DOWNLOADING', url, page_url)
            root_url = 'https://' + urlparse(page_url).hostname
            fpath = download_img(clean_url(url, root_url), '/tmp/imgname')
            return get_img_area(fpath)

        elements = []
        for ix, el in enumerate(l):
            if verbose:
                print(el.tag_name, el.location, el.size)
            el_size = el.size
            el_location = el.location

            attrs = self.driver.execute_script(
                'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
                el)
            if verbose:
                print(attrs)
            for att_k, att_v in attrs.items():
                tmp = {'tag_name': el.tag_name, 'area': el_size['height'] * el_size['width'],
                       'width': el_size['width'], 'height': el_size['height'],
                       'x': el_location['x'], 'y': el_location['y'], 'has_alt': 'alt' in attrs,
                       'has_title': 'title' in attrs, 'attr_value': att_v,
                       'attr': att_k}
                elements.append(tmp)

        df = pd.DataFrame(elements)
        df['is_img_url'] = df['attr_value'].apply(
            lambda s: is_img_url_candidate(s) if s == s and type(s) == str else False)
        df = df[df['is_img_url']]
        dfimg = df[df['tag_name'] == "img"]
        dfnot_img = df[df['tag_name'] != "img"]
        dfnot_img['area'] = df['attr_value'].apply(lambda x: get_real_img_size(x, self.driver.current_url))
        df = dfimg.append(dfnot_img).reset_index()
        df.sort_values(by=['area'], ascending=[False], inplace=True)

        if verbose:
            df.to_excel('/tmp/test_get_largest_img_url.xlsx')
            # os.system('soffice /tmp/test_get_largest_img_url.xlsx')
            # print(l[1].tag_name, attrs)

        return {'img_url': df.iloc[0]['attr_value'], 'height': df.iloc[0]['height'], 'width': df.iloc[0]['width']}


if __name__ == '__main__':
    # if True:
    #     chromedriver = CustomDriver(headless=False)
    #     download_img()
    if True:
        driver = CustomDriver(firefox=True, timeout=40)
        driver.get_with_proxy('http://www.target.com', countries=['US'], verbose=True)

    if False:
        url = "http://api.ipify.org"
        proxy = "178.33.76.75:8080"
        chromedriver = CustomDriver(headless=False, proxy=proxy)
        chromedriver.get(url)
        time.sleep(2)
        chromedriver.save_page('/tmp/null.html')

    if False:
        # Prompted search text
        url = "https://www.sherry-lehmann.com/"
        text = "champagne"
        input_box_path = '//*[@id="search_box_id"]'
        waiting_xpath = "//div[@class='termsHeader']"
        destination = '/tmp/test_headless.html'
        chromedriver = CustomDriver(headless=False)
        chromedriver.get(url)
        chromedriver.text_input(text, input_box_path, clear=True)
        chromedriver.wait_for_xpath(waiting_xpath)
        chromedriver.save_page(destination)

    if False:
        url = "https://fd7-courses.leclercdrive.fr/magasin-159301-Blanc-Mesnil/recherche.aspx?TexteRecherche=whisky"
        destination = "/tmp/leclerc.html"
        chromedriver = CustomDriver(headless=True)
        chromedriver.get(url)
        time.sleep(5)
        chromedriver.save_page(destination)
        print(destination)

    if False:
        chromedriver = CustomDriver(headless=False)
        url = "https://www.boozebud.com/"
        kw = "champagne"
        input_box_xpath = '//*[@id="reactContent"]/div/div[2]/nav/nav/div[2]/div[1]/div[1]/input'
        chromedriver.get(url)
        chromedriver.text_input(kw, input_box_xpath, enter=True)
        time.sleep(15)

    if False:
        chromedriver = CustomDriver(headless=False)
        chromedriver.get('https://www.wine.com/list/wine/champagne-and-sparkling/7155-123/2?pagelength=100')
        # chromeself.driver.execute_script("window.scrollTo(0, 8*document.body.scrollHeight)/10;")
        chromedriver.save_page('/tmp/test.html', scroll_to_bottom=True)
        time.sleep(5)

    if False:
        cdriver = CustomDriver(firefox=True, proxy_host="151.80.140.233", proxy_port=54566, headless=True)
        cdriver.get("http://icanhazip.com/")
        print(cself.driver.page_source)

    if False:
        fpath = '/tmp/free-proxy-list.net.html'
        if not os.path.exists(fpath):
            cdriver = CustomDriver(firefox=True, proxy_host="151.80.140.233", proxy_port=54566, headless=True)
            cdriver.get("https://free-proxy-list.net/")
            cdriver.save_page(fpath, scroll_to_bottom=True)
        tree = etree.parse(open(fpath), parser=parser)
        for li in tree.xpath('//*[@id="proxylisttable"]//tr'):
            print(":".join(li.xpath('./td//text()')[:2]))

    if False:
        fpath = '/tmp/enfants_riches.html'
        cdriver = CustomDriver(firefox=True, proxy_host="52.15.102.68", proxy_port=3128, headless=False)
        cdriver.get("http://icanhazip.com/")
        sleep(2)
        print(cself.driver.page_source)
        cdriver.get('https://whatismyipaddress.com/fr/mon-ip')
        sleep(5)
        cdriver.get("https://www.ssense.com/en-fr/men/product/enfants-riches-deprimes/white-self-destructive-enfant-t-shirt/2676158")
        cdriver.save_page(fpath, scroll_to_bottom=True)
        sleep(100)
    if False:
        cdriver = CustomDriver(firefox=True, proxy_host="52.15.102.68", proxy_port=3128, headless=False)
        url = 'https://translate.google.fr/m/translate?hl=fr#ja/en/'
        cdriver.get(url)
        text = """B00FJSAWAQ;;感謝の風船セット ギフトセット　ウイスキーセット ハート風船付( ボウモア 43% 700ml(スコットランド）)メッセージカード付;;
                B00LA279LA;;誕生日祝い　名入れ彫刻　ジャックダニエル ブラック　デザインA　nck-jackdnl;;
                B00KBOE72W;;スミノフ ウォッカ 40° 750ml ［並行輸入品;;
                B00JZXK1SY;;ルーチェ グラッパ 40度 500ml 並行輸入品;;
                """
        cdriver.text_input(text, xpath='//textarea[@id="source"]')
        sleep(200)

    if False:
        cdriver = CustomDriver(headless=False)
        urls = ["https://www.goodygoody.com/Products/Products",
            "https://www.31dover.com/champagne/dom-perignon-rose-2005-champagne.html",
            "https://www.b-21.com/2013-Angulo-Innocenti-Malbec/productinfo/ARINML13AE/",
            "https://www.wallywine.com/macallan-30-year-sherry-oak-single-malt-scotch-whisky-750ml.html?nosto=nosto-page-category1",
            "https://www.davidjones.com/home-and-food/food-and-wine/wine-champagne-and-spirits/20463307/Dom-Perignon-Rose.html",
            "https://www.champagnedirect.co.uk/cat_lanson_champagne.cfm"]
        for ix, url in enumerate(urls):
            cdriver.get(url)
            cdriver.fullpage_screenshot('/tmp/screenshots_{n}.png'.format(n=ix))

    if False:
        cdriver = CustomDriver(headless=False)
        page_pdct_urls = ['https://www.31dover.com/champagne/armand-de-brignac-dynastie-champagne.html',
                           'https://www.astorwines.com/SearchResultsSingle.aspx?p=1&search=36734&searchtype=Contains',
                           'https://www.champagnedirect.co.uk/pd_lanson_black_20cl_polo_wimbledon_jacket.cfm',
                           'https://www.bevmo.com/catalog/product/view/id/11808',
                           'https://bws.com.au/product/158728/veuve-clicquot-la-grande-dame',
                           'https://www.decantalo.com/es/moet-chandon-brut-imperial.html']
        cdriver.get(page_pdct_urls[1])
        cdriver.get_largest_img_url(verbose=True)

        l = []
        for ix, page_pdct_url in enumerate(page_pdct_urls):
            cdriver.get(page_pdct_url)
            tmp = {'page_pdct_url': page_pdct_url}
            tmp.update(cdriver.get_largest_img_url())
            l.append(tmp)
        pd.DataFrame(l).to_excel('/tmp/test.xlsx')
        os.system('soffice /tmp/test.xlsx')
