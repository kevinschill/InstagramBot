import json
import random


class Config():
    def __init__(self):
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

    def Hashtags(self):
        return self.hashtags

    def Comments(self):
        return self.comments
