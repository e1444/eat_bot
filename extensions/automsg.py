import discord
from discord.ext import commands
from discord import app_commands

from bot import Bot

import json
import requests

from constants import *

AUTOMSG_MSG_KEY = 'message'
AUTOMSG_CHID_KEY = 'channel_id'
AUTOMSG_PROCESSED_KEY = 'processed'
AUTOMSG_REQUESTER_KEY = 'requester'

class AutoMsgCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

        with open(AUTOMSG_PATH, 'r') as file:
            self.schedule: dict[str, dict] = json.load(file)
        
    @app_commands.command(
        name='schedule',
        description='Schedule an automsg'
    )
    async def schedule(self, ctx: discord.Interaction, *, message: str, user: discord.Member, channel: discord.TextChannel):
        obj = dict()
        obj[AUTOMSG_MSG_KEY] = message
        obj[AUTOMSG_CHID_KEY] = channel.id
        obj[AUTOMSG_REQUESTER_KEY] = ctx.user.id
        self.schedule[user.id] = obj
        
        with open(AUTOMSG_PATH, 'w') as file:
            json.dump(self.schedule, file)
                    
        await ctx.response.send_message('Message successfully scheduled')
        
    
    @commands.Cog.listener("on_message")
    async def automsg(self, message: discord.Message):
        if message.author.id not in self.schedule:
            return
        
        obj = self.schedule[message.author.id]
        
        if message.channel.id != obj[AUTOMSG_CHID_KEY]:
            return
        
        requester = self.bot.get_user(obj[AUTOMSG_REQUESTER_KEY])
        image_data = requests.get(requester.display_avatar.url).content
        webhook = await message.channel.create_webhook(name=requester.display_name + '_bot', avatar=image_data)
        
        await webhook.send(obj[AUTOMSG_MSG_KEY])
        await webhook.delete()
        
        self.schedule.pop(message.author.id)
        
        with open(AUTOMSG_PATH, 'w') as file:
            json.dump(self.schedule, file)
        
        
async def setup(bot: Bot):
    await bot.add_cog(AutoMsgCog(bot))