"""
Utils package for scraping websites and saving cookies
"""

# imports
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pickle


def check_exists_by_link_text(text, driver):
    try:
        driver.find_element(By.LINK_TEXT, text)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def dowload_images(urls, save_dir):
    """
    Method to download images and save locally

    :param:
        urls: list
        media urls
    :param:
        save_dir: string
        os directory path
    :return:
        None
    """
    for i, url_v in enumerate(urls):
        for j, url in enumerate(url_v):
            urlretrieve(url, save_dir + '/' + str(i + 1) + '_' + str(j + 1) + ".jpg")


def init_driver(headless=True, proxy=None, show_images=False, option=None, use_cookies=False, cookies_path=""):
    """
    Method to create an instance of Chrome webdriver
    """
    # options
    options = Options()

    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("user-data-dir=selenium")
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])  # remove warning
    # options.add_experimental_option("detach", True)  # keep window open

    if headless is True:
        options.add_argument('--disable-gpu')
        options.headless = True
    else:
        options.headless = False
    options.add_argument('log-level=3')
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)
    if show_images == False:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    if option is not None:
        options.add_argument(option)

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(100)

    # loading cookies
    if use_cookies:
        load_cookies(driver, path=cookies_path)

    return driver


def save_cookies(driver, path):
    """
    Method to save cookies for a website instance

    :param:
        driver: ChromeDriver
    :param:
        path: string
        cookies os directory path for saving
    :return:
        None
    """
    with open(f"{path}.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, path):
    """
    Method to load cookies for a website instance

    :param:
        driver: ChromeDriver
    :param:
        path: string
        cookies os directory path for loading
    :return:
        None
    """
    with open(path, 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)
    for cookie in cookies:
        driver.add_cookie(cookie)
