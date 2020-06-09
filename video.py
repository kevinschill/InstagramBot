from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import selenium

import os
import time
import random
import json
from datetime import date
from datetime import datetime

import login as LoginData
from ConfigLoader import Config
from fake_useragent import UserAgent


from selenium.webdriver.common.action_chains import ActionChains


useragent = UserAgent()
opts = Options()
opts.add_argument("user-agent={}".format(useragent.random))


class InstagramBot():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.browser = webdriver.Chrome(
            "./chromedriver.exe", chrome_options=opts)

        self.config = Config()

        self.liked_count = 0
        self.commented_count = 0

    def WaitForObject(self, type, string):
        return WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((type, string)))

    def WaitForObjects(self, type, string):
        return WebDriverWait(self.browser, 5).until(EC.presence_of_all_elements_located((type, string)))

    def login(self):
        self.browser.get("https://www.instagram.com/accounts/login")

        login_objects = self.WaitForObjects(
            By.CSS_SELECTOR, "input._2hvTZ.pexuQ.zyHYP")

        login_objects[0].send_keys(self.username)
        login_objects[1].send_keys(self.password)
        login_objects[1].send_keys(Keys.ENTER)

        self.WaitForObject(By.CLASS_NAME, "coreSpriteKeyhole")

        self.WaitForObject(By.CSS_SELECTOR, "button.sqdOP.yWX7d.y3zKF").click()

        self.WaitForObject(By.CSS_SELECTOR, "button.aOOlW.HoLwm").click()

    def check_like_amount(self, photo):
        try:
            hover = ActionChains(self.browser).move_to_element(photo).perform()
            likes = self.WaitForObject(By.CLASS_NAME, "-V_eO")

            return int(likes.text.replace(".", ""))
        except (selenium.common.exceptions.StaleElementReferenceException, selenium.common.exceptions.TimeoutException):
            print("TimeOut or Stale")
            return 0

    def collect_photos(self, hashtag):
        self.browser.get(f"https://www.instagram.com/explore/tags/{hashtag}/")

        self.browser.execute_script("window.scrollTo(0, 4000)")

        all_photos = self.WaitForObjects(
            By.CSS_SELECTOR, "div.v1Nh3.kIKUG._bz0w")

        all_links = []
        for photo in all_photos:
            #if self.check_like_amount(photo) > 500:
           #     print("More than 500 Likes ")
            link = photo.find_element_by_css_selector(
                    'a').get_attribute('href')
            all_links.append(link)
            #else:
               # print("smaller than 500 Likes... NUB :D")

        time.sleep(5)

        self.FilterLinks(all_links)

    def ReadLikedPhotos(self):
        with open("settings/liked.json") as file:
            data = json.load(file)
        return data["liked"]

    def FilterLinks(self, links):
        liked_photos = self.ReadLikedPhotos()
        self.filtered_links = []
        for link in links:
            if link in liked_photos:
                continue
            self.filtered_links.append(link)

    def SaveLikedPhoto(self, link):
        with open("settings/liked.json") as oldfile:
            data = json.load(oldfile)
        data["liked"].append(link)
        with open("settings/liked.json", "w+") as newfile:
            json.dump(data, newfile, indent=4)

    def write_comment(self):
        time.sleep(random.randint(3, 6))
        if self.commented_count < self.config.commentstoday:
            commentbox = self.WaitForObject(By.CLASS_NAME, "Ypffh")
            commentbox.click()
            commentbox = self.WaitForObject(By.CLASS_NAME, "Ypffh")
            commentbox.clear()
            commentbox.send_keys(self.config.RandomComment())
            commentbox.send_keys(Keys.ENTER)
            self.commented_count += 1
            time.sleep(random.randint(3, 5))

    def get_Profile(self):
        profile_link = self.WaitForObject(
            By.CLASS_NAME, "sqdOP.yWX7d._8A5w5.ZIAjV").get_attribute('href')

        return profile_link

    def follow_user(self, userprofile):
        if userprofile not in self.unfollow_no_time:
            self.browser.get(userprofile)
            self.WaitForObject(
                By.CLASS_NAME, "_5f5mN.jIbKX._6VtSN.yZn4P").click()

            with open("settings/followed.json") as oldfile:
                data = json.load(oldfile)
            data["follow"].append({
                "link": userprofile,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            with open("settings/followed.json", "w+") as newfile:
                json.dump(data, newfile, indent=4)

    def unfollow_users(self):
        with open("settings/followed.json") as file:
            data = json.load(file)

        self.unfollow_no_time = []
        self.unfollow_list = []
        for follow in data['follow'][:]:
            link = follow['link']
            timex = follow['timestamp']

            if self.check_time(timex) == True:
                self.unfollow_list.append(link)
                data['follow'].remove(follow)
            else:
                self.unfollow_no_time.append(link)

        for unfollow in self.unfollow_list:
            self.browser.get(unfollow)
            self.WaitForObject(
                By.CLASS_NAME, "_5f5mN.-fzfL._6VtSN.yZn4P").click()
            self.WaitForObject(By.CLASS_NAME, "aOOlW.-Cab_").click()

            time.sleep(random.randint(4, 20))

        with open("settings/followed.json", "w+") as newfile:
            json.dump(data, newfile, indent=4)

    def check_time(self, datex):
        followed_time = datetime.strptime(datex, "%Y-%m-%d %H:%M:%S")
        time_now = datetime.strptime(datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

        td_mins = int(
            round(abs((followed_time - time_now).total_seconds()) / 60))

        if (td_mins/60) >= 24:
            return True
        else:
            return False

    def like(self, photo):
        self.browser.get(photo)

        time.sleep(random.randint(2, 5))
        self.WaitForObject(
            By.CSS_SELECTOR, "[aria-label='Gefällt mir']").click()

        self.SaveLikedPhoto(photo)

    def BotRoutine(self, like=False, comments=False, follow_users=False, unfollow_users=False):
        for photo in self.filtered_links:
            if like:
                if self.liked_count < self.config.likestoday:
                    self.like(photo)

            if comments:
                self.write_comment()

            if follow_users:
                self.follow_user(self.get_Profile())

            if unfollow_users:
                self.unfollow_users()

            time.sleep(random.randint(10, 80))


Bot = InstagramBot(LoginData.Username(), LoginData.Password())

Bot.login()

Bot.unfollow_users()

Bot.collect_photos(Bot.config.RandomHashtag())

Bot.BotRoutine(like=True, comments=True,
               follow_users=True, unfollow_users=False)
