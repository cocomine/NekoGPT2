import logging
import sqlite3
from sqlite3 import Connection

import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection

from CursorWrapper import cursor_wrapper


def database_helper(db: Connection | PooledMySQLConnection | MySQLConnectionAbstract , bot_name: str):
    """
    Check database version and update if needed.
    :param db: database connection
    :param bot_name: bot name
    """

    # Initialize database
    def initializing():
        # Initialize database
        cursor2 = cursor_wrapper(db)
        logging.info(f"{bot_name} Initializing database...")

        cursor2.execute(
            "create table if not exists Guild(Guild_ID varchar(25) not null primary key, replyAt tinyint(1) default 1 not null)", [])
        cursor2.execute(
            "create table if not exists DM(User varchar(25) not null primary key, conversation varchar(35) not null)", [])
        cursor2.execute("""create table if not exists ReplyAt(
                    Guild_ID     varchar(25)             not null,
                    user         varchar(25)             not null,
                    conversation varchar(35)             null,
                    primary key (Guild_ID, user),
                    constraint ReplyAt_Guild_Guild_ID_fk
                        foreign key (Guild_ID) references Guild (Guild_ID)
                            on update cascade on delete cascade
                )""", [])
        cursor2.execute("""create table if not exists ReplyThis(
                    Guild_ID     varchar(25)             not null,
                    channel_ID   varchar(25)             not null,
                    conversation varchar(35)             null,
                    primary key (Guild_ID, channel_ID),
                    constraint ReplyThis_Guild_Guild_ID_fk
                        foreign key (Guild_ID) references Guild (Guild_ID)
                            on update cascade on delete cascade
                )""", [])
        cursor2.execute(
            "CREATE TABLE if not exists `setting` (`key` varchar(20) NOT NULL, `value` TEXT NOT NULL, PRIMARY KEY(`key`))", [])
        cursor2.execute("INSERT INTO setting (`key`, `value`) VALUES ('version', '0.4')", [])
        db.commit()

        logging.info(f"{bot_name} Database initialized.")

    try:
        cursor = cursor_wrapper(db)
        cursor.execute("SELECT value FROM setting WHERE `key` = 'version'") # check database version sql

        # check database version
        version = cursor.fetchone()
        if version is not None:
            if version[0] == "0.4":
                logging.info(f"{bot_name} Database is up to date.")
                return
    except mysql.connector.Error:
        initializing()
    except sqlite3.Error:
        initializing()

    # recheck update
    database_helper(db, bot_name)