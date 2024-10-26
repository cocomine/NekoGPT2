import os
from sqlite3 import Connection

from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
from openai import OpenAI
from redis.asyncio import Redis

sql_conn: Connection | PooledMySQLConnection | MySQLConnectionAbstract  # Database connection
redis_conn: Redis  # Redis connection
openai_client: OpenAI  # ChatGPT connection
loading_emoji = os.getenv('DISCORD_CUSTOM_LOADING_EMOJI') if (
            os.getenv('DISCORD_CUSTOM_LOADING_EMOJI') is not None or os.getenv(
        'DISCORD_CUSTOM_LOADING_EMOJI') != "") else "🔄"  # Loading emoji

