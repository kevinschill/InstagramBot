from InstagramMain import InstagramMain
import json
import time
import random
#Initialize Bot

bot = InstagramMain("UserName","Password")
bot.login()


while True:
    collected_photos = bot.collect_photos_by_hashtag(bot.mConfig.RandomHashtag())

    if collected_photos != False:
        for post in collected_photos:

            bot.like(post)

            time.sleep(random.randint(8,35))

            bot.write_comment(post)

            time.sleep(random.randint(8,35))

           # Follow user from Photo open
           # bot.follow_user(bot.get_Profile())


    # Accept alle Followers Requests
    # bot.AcceptFollowers()

    # Unfollow Users
    # bot.unfollow_users()
