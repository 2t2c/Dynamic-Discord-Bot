"""
Web Scraper module for the bot
"""

# imports
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
import random
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from .utils import init_driver, check_exists_by_xpath, save_cookies
import csv
import logging

# fetch logger
logger = logging.getLogger("discord_bot_logger")

# fetching twitter login credentials
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")


class TwitterScraper:
    """
    Main class for scraping tweets from Twitter.
    """

    def __init__(self):
        self.email = TWITTER_EMAIL
        self.username = TWITTER_USERNAME
        self.password = TWITTER_PASSWORD
        self.save_tweets = False
        self.tweets = []

    def get_data(self, card, save_images=False, save_dir=None):
        """Extract data from tweet card"""
        image_links = []

        try:
            username = card.find_element(By.XPATH, './/span').text
        except:
            return

        try:
            handle = card.find_element(By.XPATH, './/span[contains(text(), "@")]').text
        except:
            return

        try:
            postdate = card.find_element(By.XPATH, './/time').get_attribute('datetime')
        except:
            return

        try:
            text = card.find_element(By.XPATH, './/div[2]/div[2]/div[1]').text
        except:
            text = ""

        try:
            embedded = card.find_element(By.XPATH, './/div[2]/div[2]/div[2]').text
        except:
            embedded = ""

        # text = comment + embedded

        try:
            reply_cont = card.find_element(By.XPATH, './/div[@data-testid="reply"]').text
        except:
            reply_cont = 0

        try:
            retweet_count = card.find_element(By.XPATH, './/div[@data-testid="retweet"]').text
        except:
            retweet_count = 0

        try:
            like_count = card.find_element(By.XPATH, './/div[@data-testid="like"]').text
        except:
            like_count = 0

        try:
            elements = card.find_elements(By.XPATH, './/div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/")]')
            for element in elements:
                image_links.append(element.get_attribute('src'))
        except:
            image_links = []

        # if save_images == True:
        #	for image_url in image_links:
        #		save_image(image_url, image_url, save_dir)
        # handle promoted tweets

        try:
            promoted = card.find_element(By.XPATH, './/div[2]/div[2]/[last()]//span').text == "Promoted"
        except:
            promoted = False
        if promoted:
            return

        # get a string of all emojis contained in the tweet
        try:
            emoji_tags = card.find_elements(By.XPATH, './/img[contains(@src, "emoji")]')
        except:
            return
        # list to store emojis
        emojis = []
        for tag in emoji_tags:
            try:
                filename = tag.get_attribute('src')
                emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
            except AttributeError:
                continue
            if emoji:
                emojis.append(emoji)
        emojis = ' '.join(emojis)

        # tweet url
        try:
            element = card.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
            tweet_url = element.get_attribute('href')
        except Exception as e:
            logger.error(f"Error in finding tweet url! - {e}")
            return

        tweet = (
            username, handle, postdate, text, embedded, emojis, reply_cont, retweet_count, like_count, image_links,
            tweet_url)

        return tweet

    def log_search_page(self, driver, lang, display_type, words,
                        to_account, from_account, mention_account,
                        hashtag, filter_replies, proximity, geocode,
                        minreplies, minlikes, minretweets):
        """Search for this query between since and until_local"""
        # format the <from_account>, <to_account> and <hash_tags>
        from_account = "(from%3A" + from_account + ")%20" if from_account is not None else ""
        to_account = "(to%3A" + to_account + ")%20" if to_account is not None else ""
        mention_account = "(%40" + mention_account + ")%20" if mention_account is not None else ""
        hash_tags = "(%23" + hashtag + ")%20" if hashtag is not None else ""

        if words is not None:
            if len(words) == 1:
                words = "(" + str(''.join(words)) + ")%20"
            else:
                words = "(" + str('%20OR%20'.join(words)) + ")%20"
        else:
            words = ""

        if lang is not None:
            lang = 'lang%3A' + lang
        else:
            lang = ""

        if display_type == "Latest" or display_type == "latest":
            display_type = "&f=live"
        elif display_type == "Image" or display_type == "image":
            display_type = "&f=image"
        else:
            display_type = ""

        # filter replies
        if filter_replies == True:
            filter_replies = "%20-filter%3Areplies"
        else:
            filter_replies = ""
        # geo
        if geocode is not None:
            geocode = "%20geocode%3A" + geocode
        else:
            geocode = ""
        # min number of replies
        if minreplies is not None:
            minreplies = "%20min_replies%3A" + str(minreplies)
        else:
            minreplies = ""
        # min number of likes
        if minlikes is not None:
            minlikes = "%20min_faves%3A" + str(minlikes)
        else:
            minlikes = ""
        # min number of retweets
        if minretweets is not None:
            minretweets = "%20min_retweets%3A" + str(minretweets)
        else:
            minretweets = ""

        # proximity
        if proximity == True:
            proximity = "&lf=on"  # at the end
        else:
            proximity = ""

        path = 'https://twitter.com/search?q=' + words + from_account + to_account + mention_account + hash_tags + lang + filter_replies + geocode + minreplies + minlikes + minretweets + '&src=typed_query' + display_type + proximity
        driver.get(path)

        return path

    def log_in(self, driver, wait=4):
        """
        Method to login into Twitter

        :param:
            driver: ChromeDriver
            to open the webpage and crawl the data
        :param:
            wait: int
            no. of seconds to wait/buffer
        :return:
            None
        """
        # opening login portal
        driver.get('https://twitter.com/i/flow/login')
        # locating xpaths
        email_xpath = '//input[@autocomplete="username"]'
        password_xpath = '//input[@autocomplete="current-password"]'
        username_xpath = '//input[@data-testid="ocfEnterTextTextInput"]'
        time.sleep(random.uniform(wait, wait + 1))

        # enter email
        email_el = driver.find_element(By.XPATH, email_xpath)
        time.sleep(random.uniform(wait, wait + 1))
        email_el.send_keys(self.email)
        time.sleep(random.uniform(wait, wait + 1))
        email_el.send_keys(Keys.RETURN)
        time.sleep(random.uniform(wait, wait + 1))
        # in case twitter spotted unusual login activity: enter your username
        if check_exists_by_xpath(username_xpath, driver):
            username_el = driver.find_element(By.XPATH, username_xpath)
            time.sleep(random.uniform(wait, wait + 1))
            username_el.send_keys(self.username)
            time.sleep(random.uniform(wait, wait + 1))
            username_el.send_keys(Keys.RETURN)
            time.sleep(random.uniform(wait, wait + 1))
        # enter password
        password_el = driver.find_element(By.XPATH, password_xpath)
        password_el.send_keys(self.password)
        time.sleep(random.uniform(wait, wait + 1))
        password_el.send_keys(Keys.RETURN)
        time.sleep(random.uniform(wait, wait + 1))

    def scrape(self, words=None, to_account=None, from_account=None, mention_account=None,
               lang=None, headless=True, limit=float("inf"), display_type="Top", resume=False, proxy=None,
               hashtag=None,
               show_images=False, save_images=False, save_dir="outputs", filter_replies=False, proximity=False,
               geocode=None, minreplies=None, minlikes=None, minretweets=None):
        """
        Method to scrape data from twitter using requests, starting from <since> until <until>. The program make a search between each <since> and <until_local>
        until it reaches the <until> date if it's given, else it stops at the actual date.

        return:
        data : df containing all tweets scraped with the associated features.
        save a csv file containing all tweets scraped with the associated features.
        """

        try:
            # header of csv
            header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis', 'Comments', 'Likes',
                      'Retweets', 'Image link', 'Tweet URL']
            # list that contains all data
            data = []
            # unique tweet ids
            tweet_ids = set()
            # write mode
            write_mode = 'w'
            # start scraping from <since> until <until>
            # add the <interval> to <since> to get <until_local> for the first refresh
            # until_local = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)
            # until_local = datetime.datetime.strptime(since, '%Y-%m-%d')
            # if <until>=None, set it to the actual date
            # if until is None:
            #     until = datetime.date.today().strftime("%Y-%m-%d")
            # set refresh at 0. we refresh the page for each <interval> of time.
            refresh = 0

            # file path
            path = "tweets.csv"
            if words:
                if type(words) == str:
                    words = words.split("//")
                path = save_dir + "/" + '_'.join(words) + '.csv'
            elif from_account:
                path = save_dir + "/" + from_account + '.csv'
            elif to_account:
                path = save_dir + "/" + to_account + '.csv'
            elif mention_account:
                path = save_dir + "/" + mention_account + '.csv'
            elif hashtag:
                path = save_dir + "/" + hashtag + '.csv'
            # create the save_dir if does-not-exists
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            # show images during scraping (for saving purpose)
            if save_images == True:
                show_images = True
            # initiate the driver
            driver = init_driver(headless, proxy, show_images)

            # logging in
            self.log_in(driver)
            save_cookies(driver, "twitter_cookies")
            time.sleep(15)

            # start scrapping tweets
            # open the file
            with open(path, write_mode, newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if write_mode == 'w':
                    # write the csv header
                    writer.writerow(header)
                # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
                # while until_local <= datetime.datetime.strptime(until, '%Y-%m-%d'):
                # number of scrolls
                scroll = 0
                # log search page between <since> and <until_local>
                search_path = self.log_search_page(driver=driver, words=words, to_account=to_account,
                                                   from_account=from_account, mention_account=mention_account,
                                                   hashtag=hashtag, lang=lang, display_type=display_type,
                                                   filter_replies=filter_replies, proximity=proximity, geocode=geocode,
                                                   minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)
                logger.info(search_path)
                refresh += 1
                last_position = driver.execute_script("return window.pageYOffset;")
                # keep scrolling or not
                scrolling = True
                # number of tweets parsed
                tweet_parsed = 0
                # buffer
                time.sleep(random.uniform(0.5, 1.5))
                # start scrolling and scrape tweets
                driver, data, writer, tweet_ids, scrolling, tweet_parsed, scroll, last_position = \
                    self.keep_scrolling(driver, data, writer, tweet_ids, scrolling, tweet_parsed, limit, scroll,
                                        last_position)

            self.tweets = pd.DataFrame(data,
                                       columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text',
                                                'Emojis',
                                                'Comments', 'Likes', 'Retweets', 'Image link', 'Tweet URL'])
            if self.save_tweets:
                data.to_csv("tweets.csv", index=False)

            return self.tweets.to_dict("records")
        except Exception as e:
            logger.error(f"Error in scraping Twitter! - {e}", exc_info=True)

    def keep_scrolling(self, driver, data, writer, tweet_ids, scrolling, tweet_parsed, limit, scroll, last_position,
                       save_images=False):
        """Method to scroll the Twitter feed for fresh tweets."""

        save_images_dir = "/images"
        if save_images == True:
            if not os.path.exists(save_images_dir):
                os.mkdir(save_images_dir)
        while scrolling and tweet_parsed < limit:
            time.sleep(random.uniform(0.5, 1.5))
            # get the card of tweets
            page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            for card in page_cards:
                tweet = self.get_data(card, save_images, save_images_dir)
                if tweet:
                    # check if the tweet is unique
                    tweet_id = ''.join(tweet[:-2])
                    if tweet_id not in tweet_ids:
                        tweet_ids.add(tweet_id)
                        data.append(tweet)
                        last_date = str(tweet[2])
                        writer.writerow(tweet)
                        tweet_parsed += 1
                        if tweet_parsed >= limit:
                            break
            scroll_attempt = 0
            while tweet_parsed < limit:
                # check scroll position
                scroll += 1
                time.sleep(random.uniform(0.5, 1.5))
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                curr_position = driver.execute_script("return window.pageYOffset;")
                if last_position == curr_position:
                    scroll_attempt += 1
                    # end of scroll region
                    if scroll_attempt >= 2:
                        scrolling = False
                        break
                    else:
                        time.sleep(random.uniform(0.5, 1.5))  # attempt another scroll
                else:
                    last_position = curr_position
                    break
        return driver, data, writer, tweet_ids, scrolling, tweet_parsed, scroll, last_position


class NineGagScrapper:
    """
    Main class to scrape trending memes from 9gag
    """

    def __init__(self):
        self.memes = []
        self.buffer_time = 5
        self.scroll_count = 3
        self.scroll_pause_time = 2
        self.search_url = "https://9gag.com"
        self.headless = False

    def scrape_memes(self, search_query):
        """
        Method to scrape the memes given the search url

        :param:
            search_query: string
            meme title or 9gag section
        :return:
            memes: list
            media urls (image/video)
        """
        # initiate the driver
        driver = init_driver(headless=self.headless,
                             show_images=True)
        # searching sections or queries in 9gag
        if search_query:
            if search_query.lower() in ["top", "trending", "fresh"]:
                self.search_url += "/" + search_query
            else:
                self.search_url += f"/search?query={search_query}"
        # opening the 9gag page for scraping
        driver.get(self.search_url)
        time.sleep(self.buffer_time)

        # get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while (self.scroll_count > 0):
            # scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # wait to load page
            time.sleep(self.scroll_pause_time)
            self.scroll_count = self.scroll_count - 1

            # calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # driver.execute_script('window.scrollTo(0, document.body.scrollHeight)',"")
        source = driver.execute_script("return document.documentElement.outerHTML")
        driver.quit()
        soup = BeautifulSoup(source, "lxml")
        # iterating through the soup to extract meme html containers
        for media in soup.findAll("div", class_="post-container"):
            try:
                # extracting media hyperlinks from the soup object
                video_url = media.source.get("src")
                img_url = media.source.get("srcset")
                # saving media urls
                if video_url:
                    self.memes.append(video_url)
                if img_url:
                    self.memes.append(img_url)
            except:
                pass

        return self.memes


class WebScraper:
    """
    A simple web scraper for extracting and formatting content from a website.
    """

    def fetch_page(self, url):
        """
        Method to fetch the HTML content of the webpage.

        :param:
            url: string
            website to be scraped
        :return:
            str: HTML content of the webpage.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching the webpage: {e}")
            return None

    def clean_content(self, formatted_content):
        """
        Method to clean scraped website content

        :param:
            formatted_content: string
            processed and formmatted website content
        :return:
            cleaned_content: string
            cleaned and processed website content
        """
        # stripping and removing multiple new lines
        cleaned_content = "\n\n".join([line.strip() for line in formatted_content.splitlines() if line.strip()])

        return cleaned_content

    def scrape_content(self, url):
        """
        Scrape and format the content from the webpage.

        :param:
            url: string
            website to be scraped
        :return:
            str: Well-formatted content from the webpage.
        """
        # getting page contents
        page_content = self.fetch_page(url)
        if not page_content:
            return None

        # converting page content to soup object
        soup = BeautifulSoup(page_content, 'html.parser')

        # Example: Extracting all the text within <p> tags
        paragraphs = soup.find_all('p')

        formatted_content = ""
        for paragraph in paragraphs:
            formatted_content += paragraph.get_text() + '\n'

        # cleaning the scraped content
        cleaned_content = self.clean_content(formatted_content)

        return cleaned_content
