# Dynamic Discord Bot

## Introduction

- Interactive Discord Bot capable of performing various functions like generating memes, fetching the latest tweets, and engaging in conversations with a language model. 
- Features
  - Meme Generator: Get your daily dose of humor by generating memes based on your likings.
  - Twitter Fetcher: Stay updated with the trending #hashtags.
  - Chat with Language Model: Engage in conversations with a powerful language model for fun and informative interactions.

## Prerequisites

- Language: Python 3.8+
- Dependencies: see `requirements.txt`

## Setup
1. Clone the Repository: `https://github.com/2t2c/Dynamic-Discord-Bot.git`
2. Install Dependencies: `pip install requirements.txt`
3. Create a Discord Bot:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
   - Under the "Bot" tab, set the required permissions and then click "Add Bot" to create a bot user.
   - Generate/Reset your bot token and save it.
4. Add the bot to your server using authorization url and copy/save the server id.

## Environment Variables
- Discord Application Token: `AUTH_TOKEN`
- Server Id: `SERVER_ID`
- LLM os directory path: `LLM_PATH`
- Twitter email: `TWITTER_EMAIL`
- Twitter username: `TWITTER_USERNAME`
- Twitter password: `TWITTER_PASSWORD`

`Note:` It's recommended to save the credentials using cookies or user profile to "avoid suspicious" activity warnings from Twitter.

## How to run

- To run the discord client, run the following command: `python bot.py`

## Changing Large Language Model (LLM)
1. Go to [Hugging Face](https://huggingface.co/models) and search for the model of your choice.
2. Download it and copy the directory path and add it to the env. var. mentioned above. 
