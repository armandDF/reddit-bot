import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

import random
import json

""" === Overall functions === """


def wait_elem(driver, xpath, timeout):
    """
    Waits for an element to appear on the page
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath)))


""" === Proxy settings === """


def get_proxy_list():
    """
    Get a list of proxies from a file.
    """
    with open("./settings/proxies.txt", "r") as f:
        proxies = [li for li in f.read().split("\n") if li]
    return proxies


""" === Start the driver === """


def start_driver(proxy=True, headless=False):
    """
    Runs the driver with the intended settings
    """
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-data-dir=D:/Fiverr/commandes/chellemelly/driver_session")
    exec_path = './driver/chromedriver.exe'

    # Changable options
    if proxy:
        proxy = random.choice(get_proxy_list())
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": proxy,
            "ftpProxy": proxy,
            "sslProxy": proxy,
            "proxyType": "MANUAL",

        }
        webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True

    if headless:
        options.add_argument("--headless")

    # Run and open httpbin
    driver = webdriver.Chrome(
        executable_path=exec_path, chrome_options=options)
    # driver.get("http://httpbin.org/ip")
    return driver


""" === Login === """


def retrieve_cred():
    """
    Retrieves the login and password from the login.txt file
    """
    with open("./settings/login.txt", "r") as f:
        username, passwd = f.read().split("\n")
    return username, passwd


def wait_login(driver):
    """
    Waits for the login to be completed
    """
    wait_elem(driver, "//div[@role='navigation']", 10)
    return driver


def login(driver):
    """
    Logs in to the website
    """
    username, passwd = retrieve_cred()

    driver.get("https://www.reddit.com/login")

    try:
        wait_elem(driver, "//input[@id='loginUsername']",
                  10).send_keys(username)
    except selenium.common.exceptions.TimeoutException:
        wait_login(driver)
        return driver

    driver.find_element_by_xpath(
        "//input[@id='loginPassword']").send_keys(passwd)
    driver.find_element_by_xpath(
        "//button[@type='submit']").click()

    return wait_login(driver)


""" === Subreddits === """


def get_subreddits():
    """
    If scraping is enabled then scrape to get them, otherwise
    retrieve them from the subreddits.txt file
    """
    with open("./settings/subreddits.txt", "r") as f:
        sub_reddits = [li for li in f.read().split("\n") if li]
    return sub_reddits


""" === Posting === """


def open_post_menu(driver, sub_reddit, timeout=10):
    """
    Opens the page corresponding to the given sub_reddit
    """
    driver.get(f"https://www.reddit.com/{sub_reddit}/submit")
    try:
        Alert(driver).accept()  # if there is an alert
    except selenium.common.exceptions.NoAlertPresentException:
        pass  # no alerts
    wait_elem(driver, "//textarea[@placeholder='Title']", timeout)
    return driver


def get_msg_info():
    """
    Opens the appropriate files and chooses a random title
    Returns random title, post_link and comment_link
    """
    with open("./settings/post_titles.txt", "r") as f:
        titles = [li for li in f.read().split("\n") if li]
    title = random.choice(titles)

    with open("./settings/static_content.json", "r") as f:
        data = json.load(f)
    post_link = data["post_link"]
    comment_link = data["comment_body"]

    return title, post_link, comment_link


def write_link_message(driver, title, post_link, timeout=10):
    """
    Writes the title, content, url, and url title
    """
    try:
        wait_elem(
            driver, "//i[contains(@class, 'icon-link_post') and not(@disabled)]", timeout).click()
    except selenium.common.exceptions.TimeoutException:
        return False

    wait_elem(
        driver, "//textarea[@placeholder='Title']", timeout).send_keys(title)
    wait_elem(
        driver, "//textarea[@placeholder='Url']", timeout).send_keys(post_link)
    return True


def upload_file(driver, title, file_path, timeout=10):
    """
    Writes the title and uploads the file to the page
    """
    try:
        wait_elem(
            driver, "//i[contains(@class, 'icon-image_post') and not(@disabled)]", timeout).click()
    except selenium.common.exceptions.TimeoutException:
        return False

    wait_elem(
        driver, "//textarea[@placeholder='Title']", timeout).send_keys(title)
    wait_elem(
        driver, "//input[@type='file']", timeout).send_keys(file_path)

    wait_elem(
        driver, "//div[contains(text(), 'Uploading')]", timeout)

    try:
        while wait_elem(driver, "//div[contains(text(), 'Uploading')]", 1):
            pass
    except selenium.common.exceptions.TimeoutException:
        pass  # Upload finished

    return True


def message_options(driver, is_oc, is_spoiler, is_nsfw, is_flair, timeout=10):
    """
    Clicks on options that are True and available on that subreddit
    Picks a random flair if selected
    """
    if is_oc:
        try:
            driver.find_element(
                by=By.XPATH, value="//button[@aria-label='Mark this post as Original Content [OC]']").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
    if is_spoiler:
        try:
            driver.find_element(
                by=By.XPATH, value="//button[@aria-label='Mark as a spoiler']").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
    if is_nsfw:
        try:
            driver.find_element(
                by=By.XPATH, value="//button[@aria-label='Mark as Not Safe For Work']").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
    if is_flair:
        try:
            driver.find_element(
                by=By.XPATH, value="//button[@aria-label='Add flair']").click()
            all_flairs = driver.find_elements(
                by=By.XPATH, value="//div[@aria-checked='false' and @role='radio']")

            flair = random.choice(all_flairs)
            flair.click()
            try:
                wait_elem(
                    driver, "//div[text()='Error: text or emoji is required']", 1)
                wait_elem(
                    driver, "//button[contains(@class, 'qYzY57HWQ8W424hj3s10-')]", 1).click()

            except selenium.common.exceptions.TimeoutException:  # custom tag not required, click apply
                wait_elem(
                    driver, "//button[text()='Apply' and not(@disabled)]", timeout).click()

        except selenium.common.exceptions.NoSuchElementException:
            pass
    return driver


def click_post(driver, timeout=10):
    """
    Clicks on post
    """
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Post' and contains(@class, '_2iuoyPiKHN3kfOoeIQalDT') and not(@disabled)]")))
    element.click()
    return driver


def comment(driver, comment_text, timeout=10):
    """
    Waits for message to be published, then adds the comment link
    """
    wait_elem(
        driver, "//div[@role='textbox']", timeout).send_keys(comment_text)

    try:
        wait_elem(
            driver, "//*[text()='Accept all']", 1).click()
    except selenium.common.exceptions.TimeoutException:
        pass

    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Comment' and not(@disabled)]")))
    element.click()
    return driver


""" === Main === """


def post_msg_comment(driver, sub_reddit, file_path, timeout=10, **kwargs):
    """
    Retrieves information from the file, then goes to a random subreddit and posts the message
    Then comments with the information from the file too
    Returns any known error as text
    """
    timeout = kwargs.get("timeout", timeout)
    is_valid_subreddit = False  # some subreddits don't accept text posts
    while not is_valid_subreddit:
        # - Opens a random subreddit - #
        driver = open_post_menu(driver, sub_reddit, timeout=timeout)

        # - Retrieves information from the file - #
        title, post_link, comment_link = get_msg_info()

        # - Writes the message - #
        if not file_path:
            if write_link_message(driver, title, post_link, timeout=timeout):
                is_valid_subreddit = True
        else:
            if upload_file(driver, title, file_path, timeout=timeout):
                is_valid_subreddit = True

    # - Add the correct options - #
    is_oc, is_spoiler, is_nsfw, is_flair = [
        kwargs[key] for key in ("is_oc", "is_spoiler", "is_nsfw", "is_flair")]
    driver = message_options(driver, is_oc=is_oc, is_spoiler=is_spoiler,
                             is_nsfw=is_nsfw, is_flair=is_flair, timeout=timeout)

    # - Posts the message - #
    try:
        driver = click_post(driver, timeout=timeout)
    except selenium.common.exceptions.TimeoutException:
        print("Unable to post message")
        return False

    # - Comment on the message - #
    try:
        driver = comment(driver, comment_link, timeout=timeout)
    except selenium.common.exceptions.TimeoutException:
        print("Unable to comment on message")
        return False
    return True
