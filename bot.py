"""
Main Discord App Bot client
"""

# imports
import os
import sys
import discord
from code.scraper import TwitterScraper, NineGagScrapper
import random
from code.llm import LLM
# for logging
import logging
from pythonjsonlogger import jsonlogger

# Set up the logger
# define the formatter
formatter = jsonlogger.JsonFormatter(reserved_attrs=["created", "levelno", "msecs", "msg", "args",
                                                     "relativeCreated", "exc_info", "exc_text", "stack_info"],
                                     fmt="%(asctime)s %(levelname)s %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S",
                                     rename_fields={"asctime": "time", "levelname": "level"})
json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(formatter)
# create logger
logger = logging.getLogger('discord_bot_logger')
# clearing previous handlers if any
if (logger.handlers):
    logger.handlers.clear()

logger.addHandler(json_handler)
# logging messages are not passed to the handlers of ancestor loggers
logger.propagate = False
# set the level
logger.setLevel(logging.INFO)

# fetching discord auth token and server id
AUTH_TOKEN = os.getenv("AUTH_TOKEN", 'NzI5NjgxMTMwOTU3MTc2OTEz.Gz9KOr.JA579o_4I-TDSHBAx3JXhYqhZC94KugsxtoxYs')
SERVER_ID = os.getenv("SERVER_ID", 1155191250211831991)

class DiscordClient(discord.Client):
    """
    Main class for handling Discord real-time events
    """
    async def on_ready(self):
        logger.info('Logged on as:', self.user)

    async def on_message(self, message):
        try:
            s_id = client.get_guild(SERVER_ID)
            logger.info(message)
            if message.author == client.user:
                return
            # helper message for using the bot
            if message.content.startswith('!help'):
                embed = discord.Embed(title='Help for Bot', description='helping assistance')
                embed.add_field(name='!hello', value='Greets the members.')
                embed.add_field(name='!ask', value='Ask anything!')
                embed.add_field(name='!summarize', value='Summarize a website!')
                embed.add_field(name='!users', value='Display total no. of members.')
                embed.add_field(name='!hashtag', value='Displays trending tweets for the given hashtag.')
                embed.add_field(name='!9gag', value='Display Random Meme from 9Gag. Search using 1. top, 2. trending, 3. fresh, 4. custom search')
                await message.channel.send(content=None, embed=embed)
            # simple discord callouts
            if message.content.startswith('!hello'):
                await message.channel.send(f'Hello @{message.author}. How are you? :smile:')
            if message.content.startswith('!users'):
                await message.channel.send(f'Members: {s_id.member_count}')
            # chatting with LLM
            if message.content.startswith('!ask'):
                response = llm_obj.generate(message.content.strip(),
                                            action="chat")
                await message.channel.send(response)
            # summarize content for a given website
            if message.content.startswith('!summarize'):
                response = llm_obj.generate(message.content.strip(),
                                            action="summary")
                await message.channel.send(response)
            # scraping trending tweets from X
            if message.content.startswith('!hashtag'):
                twitter_obj = TwitterScraper()
                hashtag = message.content.replace("!hashtag", "").strip()
                # scraping tweets
                tweets = twitter_obj.scrape(hashtag=hashtag,
                                            headless=False, limit=5)
                # send each tweet to the server
                for tweet in tweets:
                    await  message.channel.send(random.choice(tweet))
            # scraping memes from 9gag
            if message.content.startswith('!9gag'):
                search_query = message.content.replace("!9gag", "").strip()
                # scraping memes
                nine_gag_obj = NineGagScrapper()
                memes = nine_gag_obj.scrape_memes(search_query)
                # sending random meme from the list
                await message.channel.send(random.choice(memes))
        except Exception as e:
            logger.error(e, exc_info=True)

# setting intents for the bot
intents = discord.Intents.all()
intents.message_content = True
# creating LLM and Discord client instances
llm_obj = LLM()
client = DiscordClient(intents=intents)
# running the client
client.run(AUTH_TOKEN)