import discord
from discord.ext import commands
from discord import app_commands

import wikipediaapi
import random
import requests
import json

from constants import *

SHARK_QUERY = 'List of sharks'

# Helpers
def generate_list_sharks(wiki):
    page = wiki.page(SHARK_QUERY)
    list_sect = page.section_by_title('Alphabetic sort').full_text
    
    return [x for x in str(list_sect).split('\n') if len(x) > 5]

def get_page(wiki, query):
    page = wiki.page(query)
    return page

def get_wiki_main_image(title):
    url = 'https://en.wikipedia.org/w/api.php'
    data = {
        'action' :'query',
        'format' : 'json',
        'formatversion' : 2,
        'prop' : 'pageimages|pageterms',
        'piprop' : 'original',
        'titles' : title
    }
    response = requests.get(url, data)
    json_data = json.loads(response.text)
    data = json_data['query']['pages'][0]
    
    return data['original']['source']  if 'original' in data else None

class SharkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.wiki = wikipediaapi.Wikipedia('eat_bot (erliangca@gmail.com)', 'en')  # 'en' for English Wikipedia, you can change it to other language codes if needed
        self.shark_list = generate_list_sharks(self.wiki)
        
        print('---\tSharkCog loaded\t\t---')
        
    @app_commands.command(
        name='shark',
        description="Random shark from Wikipedia"
    )
    async def send_shark(self, interaction: discord.Interaction):
        query = random.choice(self.shark_list)
        page = get_page(self.wiki, query)
        title = page.title
        body = page.summary[:2000]
        image_url = get_wiki_main_image(query)
        embed = discord.Embed(title=title, description=body)
        if image_url:
            embed.set_image(url=image_url)
            
        await interaction.response.send_message(embed=embed)
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(SharkCog(bot), guilds=GUILDS)