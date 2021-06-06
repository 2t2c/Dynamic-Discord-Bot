import discord
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import random
import re


user_agent = {"User-Agent": "Mozilla/5.0 "
                            "(Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/80.0.3987.163 Safari/537.36"}

options = webdriver.ChromeOptions()
options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
chrome_driver_binary = "C:/Users/<user_name>/Downloads/chromedriver.exe"
driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

# driver = webdriver.Chrome('C:/Users/<user_name>/Downloads/chromedriver')

# url = f'https://9gag.com/search?query={data}'
url1 = 'https://9gag.com/hot'

driver.get(url1)

print("Search URL:", url1, "\n")

SCROLL_PAUSE_TIME = 1

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
flag = 1
while (flag > 0):
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    flag = flag - 1
    print(flag)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# driver.execute_script('window.scrollTo(0, document.body.scrollHeight)',"")
# time.sleep(2)
source = driver.execute_script("return document.documentElement.outerHTML")
driver.quit()

soup = BeautifulSoup(source, "lxml")

# print(soup.prettify())

global TITLE, MEDIA, LINKS
TITLE = []
MEDIA = []
LINKS = []

for media in soup.findAll("div", class_="post-container"):
    # print(media.source,"\n")
    # try:
    #     print('Type: ', media.source.get('type'))
    #     print('Image: ', media.source.get('srcset'))
    #     print('Video: ',media.source.get('src'),"\n")
    # except:
    #     pass
    try:
        video = str(media.source.get('type'))
        video = video.split(";")[0]
        diff = str(media)

        if diff.find("post-text-container") > 1:
            flag = 1
        else:
            flag = 0

        image = media.source.get('type')
        # print(video, "\n")
        # print(image, "\n")
    except:
        pass

    if video == "video/mp4":
        # print(media.source.get("src"), "\n")
        try:
            video_link = media.source.get('src')
        except:
            pass

        if video_link not in LINKS:
            LINKS.append(video_link)
        else:
            pass

    if image == "image/webp" and flag == 1:
        # print(media.img.get("src"), "\n")
        try:
            image_link = media.source.get('srcset')
        except:
            pass

        if image_link not in LINKS:
            LINKS.append(image_link)
        else:
            pass

    else:
        pass

browser = webdriver.Chrome(r"C:\Users\<user_name>\Downloads\chromedriver.exe")

info = []

def instagram(text):
    username= str(text)
    browser.get('https://www.instagram.com/'+username+'/?hl=en')
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    source = browser.page_source
    data = BeautifulSoup(source, 'lxml')
    body = data.find('body')
    script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
    page_json = script.string.split(' = ', 1)[1].rstrip(';')
    data_json = json.loads(page_json)
    data_json = data_json['entry_data']['ProfilePage'][0]['graphql']['user']
    # print(data_json)

    # with open('profile_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(data_json, f, ensure_ascii=False, indent=4)

    result = {
        'username': data_json['username'],
        'full_name': data_json['full_name'],
        'biography': data_json['biography'],
        'external_url': data_json['external_url'],
        'followers_count': data_json['edge_followed_by']['count'],
        'following_count': data_json['edge_follow']['count'],
        'is_private': data_json['is_private'],
        'total_posts': data_json['edge_owner_to_timeline_media']['count'],
        'profile_picture': data_json['profile_pic_url_hd']
    }
    # for key,value in result.items():
    #     print(key,':',value)

    return result


client = discord.Client() # decorator to register an event
# client is our connection to Discord
token = '<unique_token_id>'
server_id = 123 #server_id

@client.event
# on_ready() event is called when the bot has finished logging in and setting things up
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
# on_message() event is called when the bot has received a message
async def on_message(message):
    s_id = client.get_guild(server_id)
    # ignore messages from ourselves
    channels = ['<channel_name>']
    if message.author == client.user:
        return
    # if str(message.channel) in channels:
    if message.content.startswith('!help'):
        embed = discord.Embed(title='Help for Bot', description='helping assistance')
        embed.add_field(name='!hello', value='Greets the members')
        embed.add_field(name='!users', value='Prints No. of members')
        embed.add_field(name='!9gag', value='Display Random Meme from 9Gag')
        embed.add_field(name='!look', value='Lookup people on Instagram')
        await message.channel.send(content=None, embed=embed)
    if message.content.startswith('!hello'):
        await message.channel.send('Hello Discord Members!')
    if message.content.startswith('!users'):
        await message.channel.send(f'Members : {s_id.member_count}')
    if message.content.startswith('!9gag'):
        await  message.channel.send(random.choice(LINKS))
    if message.content.startswith('!look-'):
        text = str(message.content)
        text = text.split(" ")[1]
        result = instagram(text)
        await  message.channel.send(str(result)[1:-1])

client.run(token)
