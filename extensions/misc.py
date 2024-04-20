import discord
from discord.ext import commands
from discord import app_commands

import pandas as pd
import requests
import random

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
        name='clone',
        description='Clone'
    )
    async def impersonate(self, interaction: discord.Interaction, name:str, image_url: str, message: str):
        await interaction.response.send_message('Acknowledged')
        image_data = requests.get(image_url).content
        webhook = await interaction.channel.create_webhook(name=name, avatar=image_data)
        await webhook.send(message)
        await webhook.delete()
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(MiscCog(bot), guilds=GUILDS)