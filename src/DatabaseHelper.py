import logging
import sqlite3
from sqlite3 import Connection

import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection


def database_helper(db: Connection | PooledMySQLConnection | MySQLConnectionAbstract , bot_name: str):
    """
    Check database version and update if needed.
    :param db: database connection
    :param bot_name: bot name
    """
    cursor = db.cursor()

    # Initialize database
    def initializing():
        # Initialize database
        logging.info(f"{bot_name} Initializing database...")

        cursor.execute(
            "create table if not exists Guild(Guild_ID char(25) not null primary key, replyAt tinyint(1) default 1 not null)")
        cursor.execute(
            "create table if not exists DM(User char(25) not null primary key, conversation char(30) not null)")
        cursor.execute("""create table if not exists ReplyAt(
                    Guild_ID     char(25)             not null,
                    user         char(25)             not null,
                    conversation char(30)             null,
                    primary key (Guild_ID, user),
                    constraint ReplyAt_Guild_Guild_ID_fk
                        foreign key (Guild_ID) references Guild (Guild_ID)
                            on update cascade on delete cascade
                )""")
        cursor.execute("""create table if not exists ReplyThis(
                    Guild_ID     char(25)             not null,
                    channel_ID   char(25)             not null,
                    conversation char(30)             null,
                    primary key (Guild_ID, channel_ID),
                    constraint ReplyThis_Guild_Guild_ID_fk
                        foreign key (Guild_ID) references Guild (Guild_ID)
                            on update cascade on delete cascade
                )""")
        cursor.execute(
            "CREATE TABLE if not exists `setting` (`key` varchar(20) NOT NULL, `value` TEXT NOT NULL, PRIMARY KEY(`key`))")
        cursor.execute("INSERT INTO setting (`key`, `value`) VALUES ('version', '0.4')")
        db.commit()

        logging.info(f"{bot_name} Database initialized.")

    try:
        cursor.execute("SELECT value FROM setting WHERE `key` = 'version'") # check database version sql
    except mysql.connector.Error:
        initializing()
    except sqlite3.Error:
        initializing()

    # check database version
    version = cursor.fetchone()
    if version is not None:
        if version[0] == "0.4":
            logging.info(f"{bot_name} Database is up to date.")
            return

    # recheck update
    database_helper(db, bot_name)
