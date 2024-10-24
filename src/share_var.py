from sqlite3 import Connection

from redis.asyncio import Redis
from openai import OpenAI

sql_conn: Connection = None  # Database connection
redis_conn: Redis = None  # Redis connection
openai_client: OpenAI = None  # ChatGPT connection
