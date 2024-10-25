import logging
import os
import sqlite3

import discord
import mysql.connector
import redis.asyncio as redis
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import (BusyLoadingError, ConnectionError, TimeoutError)

import DatabaseHelper
import share_var
from BotCmd import set_command
from BotEvent import set_event_lister
from Create_Assistant import create_assistant


# starting bot
def start(bot_name="ChatGPT"):
    logging.basicConfig(level=(logging.DEBUG if os.getenv('LOG_LEVEL') == "debug" else logging.INFO))  # set logging level
    handler = logging.FileHandler(filename='../database/bot.log', encoding='utf-8', mode='w')  # create log file handler
    logging.info(f"{bot_name} Discord Bot is starting... (v2.0.0)")

    # check openai key
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        raise RuntimeError("OPENAI_API_KEY Not Set!")

    # create openai client
    if os.getenv("OPENAI_BASE_URL") == "default" or os.getenv("OPENAI_BASE_URL") is None or os.getenv("OPENAI_BASE_URL") == "":
        share_var.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1")
    else:
        share_var.openai_client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))
    logging.info(f"{bot_name} ChatGPT is connected.")

    # check OPENAI_ASSISTANT_ID
    if os.getenv("OPENAI_ASSISTANT_ID") is None or os.getenv("OPENAI_ASSISTANT_ID") == "":
        create_assistant(share_var.openai_client)

    # check Azure key
    if os.getenv("SPEECH_KEY") is None or os.getenv("SPEECH_KEY") == "":
        raise RuntimeError("SPEECH_KEY Not Set!")
    if os.getenv("SPEECH_REGION") is None or os.getenv("SPEECH_REGION") == "":
        raise RuntimeError("SPEECH_REGION Not Set!")

    # create sql connection
    if os.getenv("SQL_DRIVER") == "sqlite3" or os.getenv("SQL_DRIVER") is None or os.getenv("SQL_DRIVER") == "":
        # create sqlite connection
        logging.info(f"{bot_name} Connecting to sqlite...")
        share_var.sql_conn = sqlite3.connect("../database/nekogpt_database.db")
        logging.info(f"{bot_name} sqlite is connected.")
    elif os.getenv("SQL_DRIVER") == "mysql":
        # create mysql connection
        logging.info(f"{bot_name} Connecting to MySQL...")
        share_var.sql_conn = mysql.connector.connect(host=os.getenv("MYSQL_HOST"), port=os.getenv("MYSQL_PORT"), user=os.getenv("MYSQL_USER"), password=os.getenv("MYSQL_PASSWORD"), database=os.getenv("MYSQL_DATABASE"))
        logging.info(f"{bot_name} MySQL is connected.")
    else:
        raise RuntimeError("SQL_DRIVER not support!")

    # check database update
    logging.info(f"{bot_name} Checking database update...")
    DatabaseHelper.database_helper(share_var.sql_conn, bot_name)

    # create intents
    intents = discord.Intents.default()
    intents.message_content = True

    # create redis connection
    logging.info(f"{bot_name} Connecting to Redis...")
    retry = Retry(ExponentialBackoff(), 3)
    share_var.redis_conn = redis.Redis(host='redis', port=6379, db=0, retry=retry, retry_on_error=[ConnectionError, TimeoutError, BusyLoadingError], decode_responses=True)
    logging.info(f"{bot_name} Redis is connected.")

    client = commands.Bot(command_prefix="!", intents=intents)  # create bot
    set_event_lister(client, bot_name)  # set event listener
    set_command(client, bot_name)  # set command listener

    if os.getenv("DISCORD_TOKEN") is None or os.getenv("DISCORD_TOKEN") == "":
        raise RuntimeError("DISCORD_TOKEN Not Set!")
    client.run(os.getenv("DISCORD_TOKEN"), log_handler=handler, log_level=logging.INFO)  # run bot


# run bot
if __name__ == "__main__":
    load_dotenv("../database/.env")  # load .env file
    start(os.getenv("BOT_NAME"))
