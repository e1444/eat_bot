import discord
from discord.ext import commands
from discord import app_commands

import pandas as pd
import requests
import random

from llm_help import infomercialify, saladify, medenglishify, britify, pirateify

from constants import *

class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        jokes = pd.read_csv(JOKE_PATH)
        self.jokes = list(jokes['joke'])
            
        print('---\tMiscCog loaded\t\t---')
        
    @app_commands.command(
        name='bwrap',
        description="Make fun-sized bubble wrap"
    )
    async def bwrap(self, interaction: discord.Interaction):
        s = '||pop||\u200b' * 10 + '\n'
        s = s * 15
        embed = discord.Embed(title="Pop the bubble wrap", description=s)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(
        name='bigwrap',
        description="Make bubble wrap"
    )
    async def bigwrap(self, interaction: discord.Interaction):
        s = '# ' + '||pop||\u200b' * 10 + '\n'
        s = s * 15
        embed = discord.Embed(title="Pop the bubble wrap", description=s)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(
        name='joke',
        description="A jo(s)ke"
    )
    async def joke(self, interaction: discord.Interaction):
        joke = random.choice(self.jokes)
        await interaction.response.send_message(joke)
            
    @app_commands.command(
        name='snakewinning',
        description='SnakeWinning?'
    )
    async def snake(self, interaction: discord.Interaction):
        s = random.choice(['SnakeWin', 'SnakeLose'])
        await interaction.response.send_message(s)
            
    @app_commands.command(
        name='nuke',
        description='Boom'
    )
    async def nuke(self, interaction: discord.Interaction):
        s = random.choice(['BOOM', 'KABOOM', 'KABLOOEY'])
        await interaction.response.send_message(s)
            
    @app_commands.command(
        name='snakekill',
        description='In the name.'
    )
    async def snake(self, interaction: discord.Interaction):
        s = random.choice(['*SnakeDying*'])
        await interaction.response.send_message(s)
        
    @app_commands.command(
        name='minor',
        description='you. are. a minor'
    )
    async def minor(self, interaction: discord.Interaction):
        s = 'https://tenor.com/view/toy-story-you-are-a-toy-you-are-a-minor-minor-meme-gif-24627767'
        await interaction.response.send_message(s)
    
    @app_commands.command(
        name='clone',
        description='Clone'
    )
    async def impersonate(self, interaction: discord.Interaction, name: str, image_url: str, message: str):
        await interaction.response.send_message('Acknowledged')
        image_data = requests.get(image_url).content
        webhook = await interaction.channel.create_webhook(name=name, avatar=image_data)
        await webhook.send(message)
        await webhook.delete()
        
    @app_commands.command(
        name='sell',
        description='Sell it to me!'
    )
    async def sell(self, interaction: discord.Interaction, *, text: str):
        await interaction.response.send_message(infomercialify(text))
    
    @app_commands.command(
        name='accent',
        description='Translates a message into an accent'
    )
    @app_commands.choices(accent=[
        app_commands.Choice(name='salad', value='0'),
        app_commands.Choice(name='oldeng', value='1'),
        app_commands.Choice(name='brit', value='2'),
        app_commands.Choice(name='pirate', value='3')
    ])
    async def impersonate(self, interaction: discord.Interaction, accent: app_commands.Choice[str], message: str):
        await interaction.response.send_message('Acknowledged', ephemeral=True)
        user = interaction.user
        image_data = requests.get(user.display_avatar).content
        webhook = await interaction.channel.create_webhook(name=user.display_name, avatar=image_data)
        
        accent_fn = [saladify, medenglishify, britify, pirateify][int(accent.value)]
        await webhook.send(accent_fn(message))
        await webhook.delete()
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(MiscCog(bot), guilds=GUILDS)