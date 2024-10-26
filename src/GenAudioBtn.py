import discord.ui

import share_var


class GenAudioBtn(discord.ui.View):
    """
    Generating audio button
    Just a button that can't be clicked
    """
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Generating voice message...", style=discord.ButtonStyle.gray, emoji=share_var.loading_emoji, disabled=True)
    async def gen_audio(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
