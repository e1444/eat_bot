import os
from bot import Bot
from constants import *

from discord import app_commands
from llm_help import saladify

if __name__ == '__main__':
    bot = Bot()
        
    @bot.tree.context_menu(
        name='salad'
    )
    async def salad(interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message(saladify(message.content))
    
    bot.run(EAT_BOT_TOKEN)