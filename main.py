import os
from bot import Bot
from constants import *

from discord import app_commands
from llm_help import saladify, medenglishify, britify, pirateify, jkify, brainrotify, psychoanalyse

if __name__ == '__main__':
    bot = Bot()
        
    # @bot.tree.context_menu(
    #     name='salad'
    # )
    # async def salad(interaction: discord.Interaction, message: discord.Message):
    #     if not message.content:
    #         await interaction.response.send_message('Error: Empty text', ephemeral=True)
    #     await interaction.response.send_message(saladify(message.content))
        
    @bot.tree.context_menu(
        name='oldeng'
    )
    async def medenglish(interaction: discord.Interaction, message: discord.Message):
        if not message.content:
            await interaction.response.send_message('Error: Empty text', ephemeral=True)
        await interaction.response.send_message(medenglishify(message.content))
        
    # @bot.tree.context_menu(
    #     name='brit'
    # )
    # async def brit(interaction: discord.Interaction, message: discord.Message):
    #     if not message.content:
    #         await interaction.response.send_message('Error: Empty text', ephemeral=True)
    #     await interaction.response.send_message(britify(message.content))
        
    @bot.tree.context_menu(
        name='snakechan'
    )
    async def jk(interaction: discord.Interaction, message: discord.Message):
        if not message.content:
            await interaction.response.send_message('Error: Empty text', ephemeral=True)
        await interaction.response.send_message(jkify(message.content))
        
    # @bot.tree.context_menu(
    #     name='pirate'
    # )
    # async def pirate(interaction: discord.Interaction, message: discord.Message):
    #     if not message.content:
    #         await interaction.response.send_message('Error: Empty text', ephemeral=True)
    #     await interaction.response.send_message(pirateify(message.content))
        
    @bot.tree.context_menu(
        name='brainrot'
    )
    async def pirate(interaction: discord.Interaction, message: discord.Message):
        if not message.content:
            await interaction.response.send_message('Error: Empty text', ephemeral=True)
        await interaction.response.send_message(brainrotify(message.content))
        
    @bot.tree.context_menu(
        name='freud'
    )
    async def freud(interaction: discord.Interaction, message: discord.Message):
        if not message.content:
            await interaction.response.send_message('Error: Empty text', ephemeral=True)
        await interaction.response.send_message('Acknowledged', ephemeral=True)
        with open('assets/freud.png', 'rb') as f:
            # Read the image file as bytes
            image_bytes = f.read()
        webhook = await interaction.channel.create_webhook(name='Sigmund Freud', avatar=image_bytes)
        await webhook.send(psychoanalyse(message.content))
        await webhook.delete()
        
    @bot.tree.context_menu(
        name='delbotmsg'
    )
    async def salad(interaction: discord.Interaction, message: discord.Message):
        if not message.author.id == EAT_BOT_ID:
            await interaction.response.send_message('Error: Message not from bot', ephemeral=True)
        await message.delete()
        await interaction.response.send_message('Message successfully deleted', ephemeral=True)  
    
    bot.run(EAT_BOT_TOKEN)