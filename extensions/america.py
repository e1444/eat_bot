import discord
from discord.ext import commands
from discord import app_commands

import json
import random

from constants import *

class AmericaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        with open(DEBT_PATH, 'r') as file:
            self.debt = json.load(file)
            
        print('---\tAmericanCog loaded\t---')
        
    @app_commands.command(
        name='freedom',
        description='Free yourself from this mortal coil'
    )
    async def freedom(self, interaction: discord.Interaction):
        guild = interaction.guild
        members = guild.members
        target = random.choice(members)
        
        bill = random.randrange(1000 * 100, 100000 * 100) / 100
        
        await interaction.response.send_message(f'Oh no! <@{target.id}> has gotten into a terrible accident (caused by you). They have to pay ${bill:.2f} in medical fees now.', allowed_mentions=discord.AllowedMentions(users=False))
        
        if str(target.id) not in self.debt:
            self.debt[str(target.id)] = 0
            
        self.debt[str(target.id)] += bill
        with open(DEBT_PATH, 'w') as file:
            json.dump(self.debt, file)
        
    @app_commands.command(
        name='debt',
        description='How (not) rich are you?'
    )
    async def debt(self, interaction: discord.Interaction):
        if str(interaction.user.id) not in self.debt:
            self.debt[str(interaction.user.id)] = 0
            
        curr_debt = self.debt[str(interaction.user.id)]
        await interaction.response.send_message(f'You are currently ${curr_debt:.2f} in debt.')
        
    @app_commands.command(
        name='debtlb',
        description='Who\'s the number one American?'
    )
    async def debt_lb(self, interaction: discord.Interaction):
        l = sorted(dict(self.debt).items(), reverse=True, key=lambda x: x[1])
        s = ''
        i = 1
        
        for k, v in l:
            s += f'{i}: <@{k}>: {v:.2f}\n'
            i += 1
            
        embed = discord.Embed(title="Leaderboard", description=s)
        
        await interaction.response.send_message(embed=embed)
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(AmericaCog(bot), guilds=GUILDS)