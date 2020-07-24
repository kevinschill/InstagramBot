from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import selenium

from fake_useragent import UserAgent

import sys
import os
import time
import random
import json

from datetime import datetime

from ConfigLoader import ConfigLoader

class InstagramMain():
    def __init__(self, username, password):

        self.username = username
        self.password = password

        opts = selenium.webdriver.chrome.options.Options()
        #useragent = UserAgent()
        # opts.add_argument("user-agent={}".format(useragent.random))
        opts.add_argument('--disable-infobars')

        # Initialize webdriver OS Based..
        operation_system = sys.platform
        if operation_system == "win32":
            self.browser = webdriver.Chrome(
                os.getcwd() + "/webdrivers/win/chromedriver.exe", options=opts)

        elif operation_system == "darwin":
            self.browser = webdriver.Chrome(os.getcwd() + "/webdrivers/mac/chromedriver", options=opts)

        elif operation_system == "linux" or operation_system == "linux2":
            self.browser = webdriver.Chrome(os.getcwd() + "/webdrivers/linux/chromedriver", options=opts)

        self.mConfig = ConfigLoader()
        self.mConfig.ReadConfig()

        self.commented_posts_count = 0
        self.liked_posts_count = 0

    def WaitForObject(self, type, string):
        try:
            return selenium.webdriver.support.ui.WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((type, string)))
        except Exception as error:
            with open("errorlog.txt","a") as errorfile:
                finalmsg = "[{}] Message: {}\n".format(datetime.now().strftime("%d-%m-%Y / %H:%M:%S"),error)
                errorfile.write(finalmsg)
            return False

    def WaitForObjects(self, type, string):
        try:
            return selenium.webdriver.support.ui.WebDriverWait(self.browser, 5).until(EC.presence_of_all_elements_located((type, string)))
        except Exception as error:
            with open("errorlog.txt","a") as errorfile:
                finalmsg = "[{}] Message: {}\n".format(datetime.now().strftime("%d-%m-%Y / %H:%M:%S"),error)
                errorfile.write(finalmsg)
            return False

    def FindByCSSAndAttribute(self, mobject, css, attribute):
        try:
            return mobject.find_element_by_css_selector(css).get_attribute(attribute)
        except:
            return False

    def ClickObject(self,mObject):
        try:
            mObject.click()
            return True
        except Exception as error:
            with open("errorlog.txt","a") as errorfile:
                finalmsg = "[{}] Message: {}\n".format(datetime.now().strftime("%d-%m-%Y / %H:%M:%S"),error)
                errorfile.write(finalmsg)
            return False

    def login(self):
        self.browser.get("https://www.instagram.com/accounts/login")

        login_objects = self.WaitForObjects(
            By.CSS_SELECTOR, "input._2hvTZ.pexuQ.zyHYP")
        if login_objects != False:
            login_objects[0].send_keys(self.username)
            login_objects[1].send_keys(self.password)
            login_objects[1].send_keys(Keys.ENTER)

        time.sleep(3)

    '''
    Bot Functions
    '''

    def collect_photos_by_hashtag(self, hashtag):
        self.browser.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
        
        for n in range(1,8):
            self.browser.execute_script("window.scrollTo(0, {})".format(n*4000))
            time.sleep(1)

        all_photos = self.WaitForObjects(
            By.CSS_SELECTOR, "div.v1Nh3.kIKUG._bz0w")
        if all_photos != False:
            all_links = []
            for photo in all_photos:
                link = self.FindByCSSAndAttribute(photo, 'a', 'href')

                if link != False:
                    all_links.append(link)

            liked_photos = self.mConfig.ReadLikedPhotos()
            filtered_links = []
            for link in all_links:
                if link in liked_photos:
                    continue
                filtered_links.append(link)

            return filtered_links
        
        return False


    def like(self, photo):
        if self.liked_posts_count < self.mConfig.likestoday:
            self.browser.get(photo)

            time.sleep(random.randint(2, 5))

            like_photo = self.WaitForObject(
                By.CSS_SELECTOR, "[aria-label='Gefällt mir']")

            if like_photo != False:
                like_photo.click()
                self.mConfig.SaveLikedPhoto(photo)
                self.liked_posts_count += 1

    def get_Profile(self):
        profile_link = self.WaitForObject(
            By.CLASS_NAME, "sqdOP.yWX7d._8A5w5.ZIAjV")
        if profile_link != False:
            return profile_link.get_attribute('href')
        elif profile_link == False:
            return False

    def follow_user(self, userprofile):

        followed_pofiles_list, _ = self.mConfig.ReadFollowedProfiles()

        if userprofile not in followed_pofiles_list:
            self.browser.get(userprofile)

            follow_button = self.WaitForObject(
                By.CLASS_NAME, "_5f5mN.jIbKX._6VtSN.yZn4P")

            if follow_button != False:
                follow_button.click()

                with open("settings/followed.json") as oldfile:
                    data = json.load(oldfile)

                data["follow"].append({
                    "link": userprofile,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                with open("settings/followed.json", "w+") as newfile:
                    json.dump(data, newfile, indent=4)

    def unfollow_users(self):
        _, unfollow_list = self.mConfig.ReadFollowedProfiles()

        for unfollow in unfollow_list:
            self.browser.get(unfollow)

            unfollow_button = self.WaitForObject(
                By.CLASS_NAME, "_5f5mN.-fzfL._6VtSN.yZn4P")
            if unfollow_button != False:
                unfollow_button.click()

                unfollow_button2 = self.WaitForObject(
                    By.CLASS_NAME, "aOOlW.-Cab_")
                if unfollow_button2 != False:
                    unfollow_button2.click()

                    with open("settings/followed.json") as file:
                        data = json.load(file)

                        for follow in data['follow'][:]:
                            if follow['link'] == unfollow:
                                data['follow'].remove(follow)

                    with open("settings/followed.json", "w+") as newfile:
                        json.dump(data, newfile, indent=4)

            #time between each Unfollow => 4 to 20 Seconds
            time.sleep(random.randint(4, 20))
    
    
    def write_comment(self, link):

        if self.commented_posts_count < self.mConfig.commentstoday:
            commentbox = self.WaitForObject(By.CLASS_NAME, "Ypffh")
            if commentbox != False:
                commentbox.click()
                commentbox = self.WaitForObject(By.CLASS_NAME, "Ypffh")
                if commentbox != False:
                    commentbox.clear()
                    commentbox.send_keys(self.mConfig.RandomComment())
                    commentbox.send_keys(Keys.ENTER)

                    self.commented_posts_count  += 1
                    self.mConfig.SaveCommentsPosted(link)

    def write_comment_on_post(self,link,comment):
        self.browser.get(link)
        commentbox = self.WaitForObject(By.CLASS_NAME, "Ypffh")
        if commentbox != False:
            commentbox.click()
            commentbox = self.WaitForObject(By.CLASS_NAME, "Ypffh")
            if commentbox != False:
                commentbox.clear()
                commentbox.send_keys(comment)
                commentbox.send_keys(Keys.ENTER)

    def AcceptFollowers(self):
        self.browser.get("https://www.instagram.com/accounts/activity/?followRequests")

        anfragen = self.WaitForObjects(By.CLASS_NAME, "sqdOP.L3NKy.y3zKF")

        if anfragen != False:
            follow_buttons = []
            
            #wir filtern die bestätigen schnell
            for x in anfragen:
                if x.text == "Bestätigen" or x.text == "Accept":
                    follow_buttons.append(x)

            anfragen_count = 0

            for anfrage in follow_buttons:
                if self.ClickObject(anfrage) != False:
                    anfragen_count +=1
                    # Wait 1 Second between each Accept.    
                    time.sleep(1)

            print("{} neue Follower".format(anfragen_count))

    def comment_my_feed(self):
        self.browser.get("https://www.instagram.com/")

        check_btn = self.WaitForObject(By.CLASS_NAME,"aOOlW.HoLwm")
        if check_btn != False:
            check_btn.click()

        #load already commented posts
        already_commented_posts = []
        with open("settings/commentsfeed.json") as f:
            data = json.load(f)
            for x in data['feedcomment']:
                already_commented_posts.append(x)

        #scroll feed
        url_list = []
        for x in range(0,10):
            new_posts = self.WaitForObjects(By.CLASS_NAME,"c-Yi7")
            if new_posts != False:
                
                for post in new_posts:
                    url = post.get_attribute('href')
                    if url not in already_commented_posts:
                        url_list.append(url)
            self.browser.execute_script("window.scrollTo(0, {})".format(4000*x))
            time.sleep(2)

        url_list = list(dict.fromkeys(url_list))
        for url in url_list:
            self.write_comment_on_post(url,"Nice Job! :)")
            data['feedcomment'].append(url)

            with open("settings/commentsfeed.json", "w+") as newfile:
                json.dump(data, newfile, indent=4)
            time.sleep(2)    
        

        
        
        


        

    '''
    Not Finished ....
    '''


    def follow_followers_of_user(self, user):
        self.browser.get(
            "https://www.instagram.com/{}/following/".format(user))

        btn_abos = self.WaitForObjects(By.CLASS_NAME, "-nal3")
        if btn_abos != False:
            btn_abos[2].click()
        print("Sleep")
        time.sleep(2)
        self.browser.execute_script("window.scrollTo(0, 4000)")
        time.sleep(5)
        temp_buttons = self.WaitForObjects(By.CLASS_NAME, "sqdOP.L3NKy.y3zKF")
        print("buttons: ", len(temp_buttons))
        follow_users = []
        if temp_buttons != False:
            for button in temp_buttons:
                if button.text == "Folgen" or button.text == "Follow":
                    follow_users.append(button)

        for user in follow_users:
            user.click()
            time.sleep(0.5)