import discord.ui


class GenAudioErrorBtn(discord.ui.View):
    """
    Generating audio button
    Just a button that can't be clicked
    """
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Generating voice message Error", style=discord.ButtonStyle.red, emoji="❌", disabled=True)
    async def gen_audio_error(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
