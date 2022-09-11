import praw
from PIL import Image, ImageEnhance, ImageFilter
import shutil
import requests
import pytesseract as ocr
import os
import time


#reddit api login, loaded from .env file

keyphrase = '/u/rareinsultbot'

insults = []
blacklist = ["reply", "replies", 0-9, "show more replies", "today", "Today", "yesterday", "PM", "ago", ":", "Reply", "{", "}", "↓", "↑"]

class bot():
        
    def __init__(self, **kwargs):
        self.BOT_DIR = os.path.dirname(os.path.realpath(__file__))+"/"
        
        self.images_dir = self.BOT_DIR+"tmp/images"
        
        self.recordsubmissions = True
        self.checksubmissions = True
        
        self.PostCount = -1
        
        self.reddit = praw.Reddit(client_id=os.environ['client_id'],
                     client_secret=os.environ['client_secret'],
                     username=os.environ['username'],
                     password=os.environ['password'],
                     user_agent=os.environ['user_agent']
                     )
        self.subreddit = self.reddit.subreddit('rareinsults')
        
        
        print("Bot initialized")
            
    def get_image(self, submission):
        if "imgur.com" in submission.url:
            if "/a/" in submission.url:
                return False
            else:
                url = submission.url+".jpg"
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    with open(self.images_dir+"/"+submission.id+".jpg", 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                    return True
                else:
                    return False
        elif "i.redd.it" in submission.url:
            url = submission.url
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(self.images_dir+"/"+submission.id+".jpg", 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                return True
            else:
                return False
        elif ".jpg" in submission.url:
            url = submission.url
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(self.images_dir+"/"+submission.id+".jpg", 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                return True
            else:
                return False
        elif ".png" in submission.url:
            url = submission.url
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(self.images_dir+"/"+submission.id+".png", 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                return True
            else:
                return False
        else:
            return False
        
    #measure the average time it takes to get an image from reddit using 5 images and return the average to avgdltime
    avgdltime = 0    
    def nettest(self, submission):
           start = time.clock()
           img = Image.open(self.images_dir+"/"+submission.id+".jpg")
           remote_img = submission.url if submission.url.endswith(".jpg") else submission.url+".jpg"
           r = requests.get(remote_img, stream=True)
           for i in range(5):
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(self.images_dir+"/"+submission.id+".jpg", 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
           end = time.clock()
           if i <= 5:
               self.avgdltime = (end-start)/5
               return True 
                   
    def filter_submissions(self):
        global submission
        if ("imgur.com" in submission.url) or ("i.redd.it" in submission.url):
            return True
        
        if ("/a" in submission.url):
            return False
        
        if (".jpg" in submission.url) or (".png" in submission.url):
            return True
        
        #filter files smaller than 80kb
        if (submission.url.endswith(".jpg") or submission.url.endswith(".png")) and (submission.url.startswith("http://") or submission.url.startswith("https://")):
            
        
        #check for duplicates
            if self.checksubmissions:
                for submission in self.subreddit.new(limit=1000):
                    if submission.url == submission.url:
                        return False
        return True

        
    def get_insult(self, submission):
        global img
        if ".jpg" in submission.url and self.avgdltime != 0:
            time.sleep(self.avgdltime)#wait for the image to download            
            if not os.path.isfile(self.images_dir+"/"+submission.id+".jpg"):
                time.sleep(5)
                neterr = input("There seems to be an issue with your network connection. Press r to retry, s to skip and q to exit.")
                if neterr == "r":
                    self.get_image(submission)
                elif neterr == "s":
                    return False
                elif neterr == "q":
                    exit()
            else:
                img = Image.open(self.images_dir+"/"+submission.id+".jpg")
                
        elif ".png" in submission.url and self.avgdltime != 0:
            time.sleep(self.avgdltime)
            if not os.path.isfile(self.images_dir+"/"+submission.id+".png"):
                time.sleep(5)
                neterr = input("There seems to be an issue with your network connection. Press r to retry, s to skip and q to exit.")
                if neterr == "r":
                    self.get_image(submission)
                elif neterr == "s":
                    return False
                elif neterr == "q":
                    exit()
            else:
                img = Image.open(self.images_dir+"/"+submission.id+".png")
        else:
            return False
        
        img = img.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)
        img = img.convert('1')
        img.save(self.images_dir+"/"+submission.id+".jpg")
        text = ocr.image_to_string(Image.open(self.images_dir+"/"+submission.id+".jpg"))
        text = text.splitlines()
        #if there are sentences in the text, concatenate them to a single line
        for line in text:
            if line in blacklist or line == "" or len(line) < 10:
                text.remove(line)
                #join the last line containing a dot with the lines above it until a line containing a dot is found. Then remove the text before the dot in the preceding line.
            if "." in line and line != text[-1]:
                text[text.index(line)+1] = line + " " + text[text.index(line)+1]
        insult = text[-1]
        return insult
        
    def write_insult(self, submission, insult):
            #check the insults.txt file for duplicates and remove them (if the file exists)
        if os.path.isfile(self.BOT_DIR+"insults.txt"):
            with open(self.BOT_DIR+"insults.txt", "r") as f:
                for line in f:
                    if insult in line:
                        return False
                    elif insult not in line or os.path.isfile(self.BOT_DIR+"insults.txt") == False:
                        with open(self.BOT_DIR+"insults.txt", "a") as f:
                            f.write(insult+"\n")
                            return True
                        
#execute the bot
bot = bot()
#run all functions
#fetch 3000 posts of all time from https://www.reddit.com/r/rareinsults/top/?sort=top&t=all and write them to submissions variable
submissions = bot.subreddit.top(limit=3000)

for submission in submissions:
    bot.get_image(submission)
    bot.filter_submissions()
    insults = bot.get_insult(submission)
    if insults != False:
        for insult in insults:
         bot.write_insult(submission, insult)
         #clean up the images directory
         os.remove(bot.images_dir+"/"+submission.id+".jpg")
            