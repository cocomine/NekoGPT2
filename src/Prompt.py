import json
import os
import re
from typing import Dict
from venv import logger

import discord
from openai import AsyncOpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta, ThreadMessageCompleted


class Prompt:

    def __init__(self, client: AsyncOpenAI):
        self.client = client

    # start new conversation
    async def start_new_conversation(self) -> str:
        """start new conversation and return conversation id

        :param prompt: prompt to start conversation

        :return: conversation thread id"""

        thread = await self.client.beta.threads.create()
        return thread.id

    # stop and delete conversation
    async def stop_conversation(self, conversation_id):
        """stop and delete conversation

        :param conversation_id: conversation id to stop"""

        await self.client.beta.threads.delete(thread_id=conversation_id)

    # ask ChatGPT
    async def ask(self, conversation_id: str, message: discord.Message, prompt: str = "", *,
                  file_url_list=None) -> Dict[str, str] | None:
        """ask ChatGPT and return message and message obj list

        :param file_url_list: file url list to ask
        :param conversation_id: conversation id to ask
        :param message: discord message obj
        :param prompt: prompt to ask

        :return:
            message: message in one season
            message_obj_list: all discord message obj list"""

        # if file_url_list is None, set empty list
        if file_url_list is None:
            file_url_list = []

        async with message.channel.typing():
            # send prompt
            content = [{"type": "image_url", "image_url": {"url": url, "detail": "low"}} for url in file_url_list]
            prompt != "" and content.append({"type": "text", "text": prompt})
            await self.client.beta.threads.messages.create(
                thread_id=conversation_id,
                role="user",
                content=content,
            )

            # get message stream
            stream = await self.client.beta.threads.runs.create(
                thread_id=conversation_id,
                assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
                stream=True
            )

            # get message in stream
            msg_all = ""  # all season message
            already_send_msg_len = 0  # already send message length
            json_msg = None  # json message
            async for event in stream:
                # get message in stream
                if isinstance(event, ThreadMessageDelta):
                    value = event.data.delta.content[0].text.value
                    if value is not None:
                        msg_all += value

                # send message
                # if message is not empty and new message length is more than 10
                if msg_all != "" and (len(msg_all) - already_send_msg_len) > 20:
                    regex_result = re.search("^(.+)(\"normal_response\":\")(.[^\"}]*)(.*)$", msg_all)

                    # only send in case of normal_response
                    if regex_result and regex_result.group(3):
                        msg_tmp = regex_result.group(3)
                        await message.edit(content=msg_tmp)

                    already_send_msg_len = len(msg_all)

                # if message is completed
                if isinstance(event, ThreadMessageCompleted):
                    json_msg = json.loads(event.data.content[0].text.value)
                    await message.edit(content=json_msg["normal_response"])
                    logger.info(f"ChatGPT: {msg_all}")

            return json_msg

    # upload file
    async def upload_file(self, attachment: discord.Attachment) -> str:
        """
        Uploads a file to the assistant and returns the file ID.

        :param attachment: The Discord attachment object to be uploaded.
        :return: The ID of the uploaded file.
        """
        # read file buffer
        file_buffer = await attachment.read()

        # # create upload
        # uploads = await self.client.uploads.create(
        #     filename=attachment.filename,
        #     purpose="vision",
        #     mime_type=attachment.content_type,
        #     bytes=attachment.size
        # )
        #
        # # upload file part
        # parts_id: List[str] = []
        #
        # for i in range(0, len(file_buffer), 1024 * 1024): # 1MB
        #     await sleep(100)
        #     part = await self.client.uploads.parts.create(
        #         upload_id=uploads.id,
        #         data=file_buffer[i:i + 1024 * 1024]
        #     )
        #     parts_id.append(part.id)
        #
        # # complete upload
        # res = await self.client.uploads.complete(
        #     upload_id=uploads.id,
        #     part_ids=[part_id for part_id in parts_id],
        # )

        # upload file
        res = await self.client.files.create(
            purpose="vision",
            file=file_buffer
        )

        logger.info(f"File uploaded: {res.id}({attachment.size / 1024}KB)")
        return res.id

    # delete file
    async def delete_file(self, file_id: str):

        # delete file
        await self.client.files.delete(file_id=file_id)
        logger.info(f"File deleted: {file_id}")
