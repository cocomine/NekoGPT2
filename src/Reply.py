import asyncio
import logging
import os
from os.path import exists

import discord
from discord import Color, Forbidden
from discord.ext import commands

import Mp3ToMp4
import share_var
from CursorWrapper import cursor_wrapper
from GenAudioBtn import GenAudioBtn
from GenAudioErrorBtn import GenAudioErrorBtn
from Prompt import Prompt
from ReGenBtn import ReGenBtn
from STT import STT
from TTS import TTS


class Reply:
    replying_dm = []  # in replying dm user list
    replying_mention = []  # in replying mention user list
    replying_channel = []  # in replying channel list

    def __init__(self, client: commands.Bot):
        """
        Handle reply message
        :param client: Discord Bot Client
        """
        self.r = share_var.redis_conn
        self.db = share_var.sql_conn
        self.prompt = Prompt(share_var.openai_client)
        self.client = client
        self.stt = STT(os.environ["SPEECH_KEY"], os.environ["SPEECH_REGION"])
        self.tts = TTS(os.environ["SPEECH_KEY"], os.environ["SPEECH_REGION"])
        self.loading_emoji = share_var.loading_emoji

    # Generate reply
    async def reply(self, message: discord.Message, conversation: str, msg: discord.Message) -> list[discord.Message]:
        """
        Generate reply
        :param message:  Discord Message Object (ask)
        :param conversation: Conversation ID
        :param msg: Discord Message Object

        :return: Message Object List
        """
        ask = message.content
        # check if message is voice message
        if ask == "" and message.attachments[0] is not None:
            attachments = message.attachments[0]

            if attachments.is_voice_message():
                # convert voice message to text
                ask = await self.stt.speech_to_text(await attachments.read())
                logging.info(f"Voice message {message.author}: {ask}")

                # show original text
                embed = discord.Embed(title=f"Detected content", description=ask,
                                      color=Color.blue(),
                                      type="article")
                embed.set_author(name=f"{message.author}", icon_url=message.author.avatar.url)
                await msg.edit(content=self.loading_emoji, embed=embed)

        # reply
        reply_json = await self.prompt.ask(conversation, msg, ask)

        # convert reply to voice message
        if reply_json is not None:
            # add Generating voice message button
            btn = GenAudioBtn()
            await msg.edit(view=btn)

            # convert text to voice message
            await self.tts.text_to_speech_file(reply_json, f"voice-message_{conversation}.mp3")

            # convert voice message to mp4
            Mp3ToMp4.convert(f"voice-message_{conversation}.mp3", f"voice-message_{conversation}.mp4")

            # upload voice message to discord
            if exists(f"voice-message_{conversation}.mp4") :
                with open(f"voice-message_{conversation}.mp4", "rb") as file:
                    await msg.edit(attachments=[discord.File(file, filename=f"voice-message_{conversation}.mp4")])

                # remove mp4
                os.remove(f"voice-message_{conversation}.mp4")

                # remove Generating voice message button
                await msg.edit(view=None)
            else:
                btn = GenAudioErrorBtn()
                await msg.edit(view=btn)

        await message.add_reaction("✅")  # add check mark

        return [msg]  # return message obj list

    # DM
    async def dm(self, message: discord.Message):
        """
        Handle DM message
        :param message: Discord Message Object
        """
        cursor = cursor_wrapper(self.db)


        # check if bot is replying
        try:
            self.replying_dm.index(message.author.id)
        except ValueError:
            self.replying_dm.append(message.author.id)  # set is replying
        else:
            # is replying
            await message.reply(
                content="⛔ In progress on the previous reply, please wait for moment.")
            return

        try:
            # add loading reaction
            await message.remove_reaction("✅", self.client.user)
            await message.add_reaction(self.loading_emoji)
            msg = await message.reply(self.loading_emoji)

            # check if conversation is started?
            conversation = await self.r.hget("DM", str(message.author.id))
            if conversation is None:
                cursor.execute("SELECT conversation FROM DM WHERE User = %s", (message.author.id,))
                result = cursor.fetchone()

                # start conversation if not started
                if result is None:
                    conversation = await self.prompt.start_new_conversation()
                    cursor.execute("INSERT INTO DM (User, conversation) VALUES (%s, %s)",
                                   (str(message.author.id), str(conversation)))
                    self.db.commit()
                    await asyncio.sleep(1)
                else:
                    conversation = result[0]

                await self.r.hset("DM", str(message.author.id), conversation)  # add into redis

            # reply message
            message_obj_list = await self.reply(message, conversation, msg)
            msg = message_obj_list[-1]

            # add regenerate button
            async def callback():
                await self.dm(message)

            btn = ReGenBtn(callback, message_obj_list)
            await msg.edit(view=btn)

        except Exception as e:
            logging.error(e)
            # add error reaction
            await message.add_reaction("❌")
            await message.reply("🔥 Oh no! Something went wrong. Please try again later.")

        finally:
            # set is not replying
            self.replying_dm.remove(message.author.id)

            # remove loading reaction
            await message.remove_reaction(self.loading_emoji, self.client.user)

    # @mention bot
    async def mention(self, message: discord.Message):
        """
        Handle @mention message
        :param message: Discord Message Object
        """
        cursor = cursor_wrapper(self.db)

        # check replyAt is enabled
        result = await (self.r.hget("Guild.replyAt", str(message.guild.id)))
        if result is None:
            cursor.execute("SELECT * FROM Guild WHERE Guild_ID = %s AND replyAt = TRUE", (message.guild.id,))
            result = cursor.fetchone()
            await self.r.hset("Guild.replyAt", str(message.guild.id), ("0" if result is None else "1"))

        # is not enabled
        if result is None or result == "0":
            await message.reply("🚫 Sorry, This server is not enabled **@mention** feature.")
            return

        # check if bot is replying
        try:
            self.replying_mention.index(message.author.id)
        except ValueError:
            self.replying_mention.append(message.author.id)  # set is replying
        else:
            # is replying
            await message.reply(
                content="⛔ In progress on the previous reply, please wait for moment.")
            return

        try:
            # add loading reaction
            await message.add_reaction(self.loading_emoji)
            msg = await message.reply(self.loading_emoji)

            # check if conversation is started?
            conversation = await self.r.hget("ReplyAt", f"{message.guild.id}.{message.author.id}")
            logging.info(conversation)
            if conversation is None:
                cursor.execute("SELECT conversation FROM ReplyAt WHERE Guild_ID = %s AND user = %s",
                               (message.guild.id, message.author.id))
                result = cursor.fetchone()

                # start conversation if not started
                if result is None:
                    conversation = await self.prompt.start_new_conversation()
                    cursor.execute("INSERT INTO ReplyAt (Guild_ID, user, conversation) VALUES (%s, %s, %s)",
                                   (message.guild.id, message.author.id, conversation))
                    self.db.commit()
                    await asyncio.sleep(1)
                else:
                    conversation = result[0]

                await self.r.hset("ReplyAt", f"{message.guild.id}.{message.author.id}", conversation)  # add into redis

            # reply message
            message_obj_list = await self.reply(message, conversation, msg)
            msg = message_obj_list[len(message_obj_list) - 1]

            # add regenerate button
            async def callback():
                await self.dm(message)

            btn = ReGenBtn(callback, message_obj_list)
            await msg.edit(view=btn)

        except Exception as e:
            logging.error(e)

            # add error reaction
            await message.add_reaction("❌")
            if isinstance(e, Forbidden):
                await message.reply("🔥 Sorry, I can't reply message in this channel. "
                                    f"Please check my permission. Details: `{Forbidden}`")
            else:
                await message.reply("🔥 Oh no! Something went wrong. Please try again later.")

        finally:
            # set is not replying
            self.replying_mention.remove(message.author.id)

            # remove loading reaction
            await message.remove_reaction(self.loading_emoji, self.client.user)

    # channel message
    async def channel(self, message: discord.Message):
        """
        Handle channel message
        :param message: Discord Message Object
        """
        cursor = cursor_wrapper(self.db)

        # get conversation
        conversation = await self.r.hget("ReplyThis", f"{message.guild.id}.{message.channel.id}")
        if conversation is None:
            cursor.execute("SELECT conversation FROM ReplyThis WHERE Guild_ID = %s AND channel_ID = %s",
                       (message.guild.id, message.channel.id))
            result = cursor.fetchone()
            conversation = result[0] if result is not None else None
            if conversation is not None:
                await self.r.hset("ReplyThis", f"{message.guild.id}.{message.channel.id}", conversation)

        # check have conversation
        if conversation is not None:
            # check if bot is replying
            try:
                self.replying_channel.index((message.guild.id, message.channel.id))
            except ValueError:
                self.replying_channel.append((message.guild.id, message.channel.id))  # set is replying
            else:
                # is replying
                await message.reply(
                    content="⛔ In progress on the previous reply, please wait for moment.")
                return

            try:
                # add loading reaction
                await message.remove_reaction("✅", self.client.user)
                await message.add_reaction(self.loading_emoji)
                msg = await message.reply(self.loading_emoji)

                # reply message
                message_obj_list = await self.reply(message, conversation, msg)
                msg = message_obj_list[len(message_obj_list) - 1]

                # add regenerate button
                async def callback():
                    await self.dm(message)

                btn = ReGenBtn(callback, message_obj_list)
                await msg.edit(view=btn)

            except Exception as e:
                logging.error(e)

                # add error reaction
                await message.add_reaction("❌")
                if isinstance(e, Forbidden):
                    await message.channel.send("🚫 Sorry, I can't reply message in this channel. "
                                               f"Please check my permission. Details: `{Forbidden}`")
                else:
                    await message.channel.send("🔥 Oh no! Something went wrong. Please try again later.")

            finally:
                # set is not replying
                self.replying_channel.remove((message.guild.id, message.channel.id))

                # remove loading reaction
                await message.remove_reaction(self.loading_emoji, self.client.user)
