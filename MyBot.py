import pdb
import time
import os

import requests
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import random
import setting


class Bot:
    def __init__(self, driverPath, url):
        """

        input params

        driverPath: path to chromedriver.exe

        url: url of a site to scrape

        example:

        bot = Bot(driverPath="./driver/chromedriver.exe",url="https://www.gowork.pl")

        """
        self.url = url
        # Chrome Driver Options.
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")

        # options.add_argument("--headless")    # Tried, but it won't pass cloudflare antibot
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument("--headless")    # Tried, but it won't pass cloudflare antibot
        options.add_argument("--disable-extensions")
        options.add_argument("--enable-javascript")
        options.add_argument("--disable-popup-blocking")

        self.bot = uc.Chrome(executable_path=driverPath, options=options)

    def passAntibotGetElementByClass(self, className):
        """

        this is for preventing action of anti-bot of cloudflare

        return:

        a element that contain class props with className if successful else None

        """
        action = webdriver.ActionChains(self.bot)
        self.bot.get(self.url)

        # add random delay to avoid anti-bot
        time_sleep_rand = random.randint(5, 10)
        time.sleep(time_sleep_rand)

        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        }

        # Oppen two tabs in order to bypass Cloudflare antibot protection.
        self.bot.execute_script('''window.open("$url");''')

        # add random delay to avoid anti-bot
        time_sleep_rand = random.randint(5, 10)
        time.sleep(time_sleep_rand)

        self.bot.switch_to.window(self.bot.window_handles[1])
        time_sleep_rand = random.randint(10, 15)
        time.sleep(time_sleep_rand)

        self.bot.close()
        self.bot.switch_to.window(self.bot.window_handles[0])

        # check if pass a antibot and take element for scraping.
        delay = 20
        element = None
        try:
            element = WebDriverWait(self.bot, 25).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, className))
            )
            print("Page is ready!")

        except TimeoutException:
            print("Loading took to much time!")

        return element

    def giveReview(self, element, user_nick, review_date):
        """

        input params:

        element: parent html element to find review data.

        user_nick: username

        review_date: date that gives review.

        return : void

        example:

        bot = Bot()

        element = bot.find_element_by_class_name("classname")

        bot.giveReview(element,"Andrzej", "05.10.2020 15:29")

        """
        delay = 25
        time.sleep(delay)

        # Parse all thread items.
        for thread_item in element.find_elements_by_class_name('thread-item'):
            thread_item_element = thread_item.text.split('\n')
            print(thread_item.text, "text")
            thread_data_id = thread_item.get_attribute('data-id')

            # Match thread item with user input <nickname> and <review_date>
            if (thread_item_element[0] == user_nick and thread_item_element[1] == review_date):
                print(thread_item_element[3][0:31])

                print("Please rate thread information...")
                user_review = input()
                # user_review = ':('

                # I know this code must be moved inside a function. Is closing the window that apears when mooving the cursor inside the page.
                close_button = element.find_element_by_xpath(
                    '//*[@id="dont-go-yet-modal"]/div/div/div[1]/button')
                if (close_button.is_displayed()):
                    ActionChains(self.bot).move_to_element(
                        close_button).click(close_button).perform()

                # Positive negative review scores.
                if user_review == ':)':
                    positive_review = thread_item.find_element_by_xpath(
                        '//*[@id="scroll%s"]/div[2]/div/div/footer/span[1]/a[1]' % thread_data_id)
                    if (positive_review.get_attribute('data-post-id') == thread_data_id and positive_review.is_displayed() and positive_review.is_enabled()):
                        ActionChains(self.bot).move_to_element(
                            positive_review).click(positive_review).perform()

                elif user_review == ':(':
                    negative_review = thread_item.find_element_by_xpath(
                        '//*[@id="scroll%s"]/div[2]/div/div/footer/span[1]/a[2]' % thread_data_id)
                    if (negative_review.get_attribute('data-post-id') == thread_data_id and negative_review.is_displayed() and negative_review.is_enabled()):
                        ActionChains(self.bot).move_to_element(
                            negative_review).click(negative_review).perform()

            else:
                close_button = element.find_element_by_xpath(
                    '//*[@id="dont-go-yet-modal"]/div/div/div[1]/button')
                if (close_button.is_displayed()):
                    ActionChains(self.bot).move_to_element(
                        close_button).click(close_button).perform()

                time.sleep(3)
                # Expand review trees, maybe the <nickname> and <review_data> compination is there.
                expand_replies = thread_item.find_element_by_class_name(
                    'thread-replies-%s' % thread_data_id)
                if expand_replies.is_displayed():
                    ActionChains(self.bot).move_to_element(
                        expand_replies).click(expand_replies).perform()

                review_replies_container_list = thread_item.find_element_by_class_name(
                    'review-replies-list__container')
                reviews = review_replies_container_list.find_elements_by_class_name(
                    'review')

                for review in reviews:
                    review_data_id = review.get_attribute('data-id')
                    review_element = review.text.split('\n')

                    if (review_element[0] == user_nick and review_element[1] == review_date):
                        print(review_element[5][0:31])

                        print("Please rate review information...")
                        user_review = input()
                        # user_review = ':)'

                        close_button = element.find_element_by_xpath(
                            '//*[@id="dont-go-yet-modal"]/div/div/div[1]/button')
                        if (close_button.is_displayed()):
                            ActionChains(self.bot).move_to_element(
                                close_button).click(close_button).perform()

                        time.sleep(2)
                        if user_review == ':)':
                            positive_review = thread_item.find_element_by_xpath(
                                '//*[@id="scroll%s"]/div[2]/div/div/footer/span[1]/a[1]' % review_data_id)
                            if (positive_review.get_attribute('data-post-id') == review_data_id and positive_review.is_displayed() and positive_review.is_enabled()):
                                ActionChains(self.bot).move_to_element(
                                    positive_review).click(positive_review).perform()

                        elif user_review == ':(':
                            negative_review = thread_item.find_element_by_xpath(
                                '//*[@id="scroll%s"]/div[2]/div/div/footer/span[1]/a[2]' % review_data_id)
                            if (negative_review.get_attribute('data-post-id') == review_data_id and negative_review.is_displayed() and negative_review.is_enabled()):
                                ActionChains(self.bot).move_to_element(
                                    negative_review).click(negative_review).perform()


if __name__ == "__main__":
    url = setting.url
    driverPath = setting.driverPath
    bot = Bot(driverPath=driverPath, url=url)
    element = bot.passAntibotGetElementByClass(className="active-tab-content")
    if element is None:
        print("no found element")
    else:
        print("Please insert user name...")
        user_nick = input()
        # user_nick = 'Daniel88', 'Andrzej', 'Byłem tam, uciekaj.'
        print("Please insert thread date...")
        review_date = input()
        # review_date = '29.10.2020 13:10', '05.10.2020 15:29', '01.06.2020 20:37'
        bot.giveReview(element, user_nick, review_date)
        # exit bot
        bot.bot.quit()
