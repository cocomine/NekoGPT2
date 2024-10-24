from sqlite3 import Connection

from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
from openai import OpenAI
from redis.asyncio import Redis

sql_conn: Connection | PooledMySQLConnection | MySQLConnectionAbstract = None  # Database connection
redis_conn: Redis = None  # Redis connection
openai_client: OpenAI = None  # ChatGPT connection
