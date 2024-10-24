import logging
import os
import sqlite3

import discord
import redis.asyncio as redis
from discord.ext import commands
from dotenv import load_dotenv
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import (BusyLoadingError, ConnectionError, TimeoutError)
from openai import OpenAI

import openai
import DatabaseHelper
import share_var
from BotCmd import set_command
from BotEvent import set_event_lister


# starting bot
def start(bot_name="ChatGPT"):
    logging.basicConfig(level=logging.DEBUG)  # set logging level
    handler = logging.FileHandler(filename='../database/bot.log', encoding='utf-8', mode='w')  # create log file handler
    logging.info(f"{bot_name} Discord Bot is starting... (v2.0.0)")

    # create ChatGPT chatbot
    if os.getenv("OPENAI_API_KEY") is None:
        raise RuntimeError("OPENAI_API_KEY Not Set!")

    if os.getenv("OPENAI_BASE_URL") == "default" or os.getenv("OPENAI_BASE_URL") is None:
        share_var.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    else:
        share_var.openai_client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))
    logging.info(f"{bot_name} ChatGPT is connected.")

    # check Azure key
    if os.getenv("SPEECH_KEY") is None:
        raise RuntimeError("SPEECH_KEY Not Set!")
    if os.getenv("SPEECH_REGION") is None:
        raise RuntimeError("SPEECH_REGION Not Set!")

    # create mysql connection
    logging.info(f"{bot_name} Connecting to MySQL...")
    share_var.sql_conn = sqlite3.connect("../database/nekogpt_database.db")
    logging.info(f"{bot_name} MySQL is connected.")

    # check database update
    logging.info(f"{bot_name} Checking database update...")
    DatabaseHelper.database_helper(share_var.sql_conn, bot_name)

    # create intents
    intents = discord.Intents.default()
    intents.message_content = True

    # create redis connection
    logging.info(f"{bot_name} Connecting to Redis...")
    retry = Retry(ExponentialBackoff(), 3)
    share_var.redis_conn = redis.Redis(host='localhost', port=6379, db=0, retry=retry, retry_on_error=[ConnectionError, TimeoutError, BusyLoadingError], decode_responses=True)
    logging.info(f"{bot_name} Redis is connected.")

    client = commands.Bot(command_prefix="!", intents=intents)  # create bot
    set_event_lister(client, bot_name)  # set event listener
    set_command(client, bot_name)  # set command listener

    if os.getenv("DISCORD_TOKEN") is None:
        raise RuntimeError("DISCORD_TOKEN Not Set!")
    client.run(os.getenv("DISCORD_TOKEN"), log_handler=handler, log_level=logging.INFO)  # run bot


# run bot
if __name__ == "__main__":
    load_dotenv("../database/.env")  # load .env file
    start(os.getenv("BOT_NAME"))
