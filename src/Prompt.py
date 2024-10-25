import os
from venv import logger

import discord
from discord import Message
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta, ThreadMessageCompleted


class Prompt:

    def __init__(self, client: OpenAI):
        self.client = client

    # start new conversation
    async def start_new_conversation(self) -> str:
        """start new conversation and return conversation id

        :param prompt: prompt to start conversation

        :return: conversation thread id"""

        thread = self.client.beta.threads.create()
        return thread.id

    # stop and delete conversation
    async def stop_conversation(self, conversation_id):
        """stop and delete conversation

        :param conversation_id: conversation id to stop"""

        await self.client.beta.threads.delete(thread_id=conversation_id)

    # ask ChatGPT
    async def ask(self, conversation_id: str, message: discord.Message, prompt: str) -> tuple[str, list[Message]]:
        """ask ChatGPT and return message and message obj list

        :param conversation_id: conversation id to ask
        :param message: discord message obj
        :param prompt: prompt to ask

        :return:
            message: message in one season
            message_obj_list: all discord message obj list"""

        async with message.channel.typing():
            message_obj_list = [message]  # all discord message obj list
            msg_all = ""  # all season message
            already_send_msg_len = 0 # already send message length

            self.client.beta.threads.messages.create(
                thread_id=conversation_id,
                role="user",
                content=prompt
            )

            stream = self.client.beta.threads.runs.create(
                thread_id=conversation_id,
                assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
                stream=True
            )

            for event in stream:
                # get message in stream
                if isinstance(event, ThreadMessageDelta):
                    value = event.data.delta.content[0].text.value
                    if value is not None:
                        msg_all += value

                # send message
                # if message is not empty and new message length is more than 10
                if msg_all != "" and (len(msg_all) - already_send_msg_len) > 10:
                    await message.edit(content=msg_all)
                    already_send_msg_len = len(msg_all)

                # if message is completed
                if isinstance(event, ThreadMessageCompleted):
                    await message.edit(content=msg_all)
                    logger.info(f"ChatGPT: {msg_all}")

            return msg_all, message_obj_list