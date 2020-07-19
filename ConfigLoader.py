import json
import random
from datetime import datetime

class ConfigLoader():

    def ReadConfig(self):
        self.hashtags = []
        self.comments = []

        with open("settings/settings.json") as jsonfile:
            data = json.load(jsonfile)
            for key, value in data.items():
                if key == "hashtags":
                    self.hashtags = value
                if key == "likestoday":
                    self.likestoday = int(value)
                if key == "commentstoday":
                    self.commentstoday = int(value)
                if key == "comments":
                    self.comments = value

    def RandomComment(self):
        return random.choice(self.comments)

    def RandomHashtag(self):
        return random.choice(self.hashtags)

    def ReadLikedPhotos(self):
        with open("settings/liked.json") as file:
            data = json.load(file)
        return data["liked"]

    def SaveLikedPhoto(self, link):
        with open("settings/liked.json") as oldfile:
            data = json.load(oldfile)
        data["liked"].append(link)
        with open("settings/liked.json", "w+") as newfile:
            json.dump(data, newfile, indent=4)

    def SaveCommentsPosted(self, link):
        with open("settings/comment.json") as oldfile:
            data = json.load(oldfile)
        data["comment"].append(link)
        with open("settings/comment.json", "w+") as newfile:
            json.dump(data, newfile, indent=4)

    def ReadCommentsPosted(self):
        with open("settings/comment.json") as file:
            data = json.load(file)
        return data["comment"]

    def ReadFollowedProfiles(self):
        with open("settings/followed.json") as file:
            data = json.load(file)

        profiles_followed = []
        profiles_to_unfollow = []

        for follow in data['follow'][:]:
            link = follow['link']
            timex = follow['timestamp']

            if self.check_time(timex) == True:
                profiles_to_unfollow.append(link)
            else:
                profiles_followed.append(link)

        return [profiles_followed, profiles_to_unfollow]

    def check_time(self, datex):
        followed_time = datetime.strptime(datex, "%Y-%m-%d %H:%M:%S")
        time_now = datetime.strptime(datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

        td_mins = int(
            round(abs((followed_time - time_now).total_seconds()) / 60))

        # 24 Stunden
        if (td_mins/60) >= 24:
            return True
        else:
            return False