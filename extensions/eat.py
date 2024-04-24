import discord
from discord.ext import commands
from discord import app_commands

import pandas as pd
import json
import re
import random
import asyncio
import time

from nltk.corpus import wordnet
import image_help

from constants import *
from llm_help import random_encounter_script

# ignored channels
IGNORE_CHS = [1222219765049851964]
        
# preprocessing
remove_quote = re.compile(r'^>')
special_c_pattern = re.compile(r'[\*\_`]')
link_pattern = re.compile(r'\[(.*?)\]\(https://.*?\)')
link_bracket_pattern = re.compile(r'\]\(')
double_star_pattern = re.compile(r'\*\*\*\*')
start_link_pattern = re.compile(r'^https://')

def preprocess(s):
    s = re.sub(remove_quote, '', s)
    s = re.sub(special_c_pattern, '', s)
    s = re.sub(link_pattern, r'\1', s)
    s = re.sub(link_bracket_pattern, ']\u200b(', s)
    s = re.sub(start_link_pattern, 'https://\u200a', s)
    return s

# helpers
def generate_punc(length):
    characters = ['?', '!']
    return ''.join(random.choice(characters) for _ in range(length))

def get_word_pos(word):
    synsets = wordnet.synsets(word)
    return [synset.pos() for synset in synsets]

class EatCog(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        with open(COUNTER_PATH, 'r') as file:
            self.counter = json.load(file)

        # on message patterns
        self.eat_pattern = re.compile(r'(e\s*a\s*t[!?]*)', re.IGNORECASE)
        self.damn_pattern = re.compile(r'(damn)', re.IGNORECASE)

        with open(COUNTER_PATH, 'r') as file:
            self.counter = json.load(file)
            
        all_words = wordnet.words()
        self.nouns = [word for word in all_words if wordnet.NOUN in get_word_pos(word)]
        
        self.time = dict()
        
        print('---\tEatCog loaded\t\t---')
        
    @app_commands.command(
        name="count",
        description="Print counts"
    )
    async def count(self, interaction: discord.Interaction):
        eat_count = self.counter['eat_count']
        beaver_count = self.counter['beaver_count']
        await interaction.response.send_message(f'\# "eat" spotted: {eat_count}\n\# "damn" spotted: {beaver_count}')
        
    @commands.Cog.listener("on_message")
    async def eat(self, message: discord.Message):
        if message.author.bot == True:
            return
        
        if message.channel.id in IGNORE_CHS:
            return
        
        s = preprocess(message.content)
        
        if re.search(self.eat_pattern, s):
            self.counter['eat_count'] += len(re.findall(self.eat_pattern, s))
            with open(COUNTER_PATH, 'w') as file:
                json.dump(self.counter, file)
                
            s = re.sub(self.eat_pattern, lambda x: f'**{x.group().upper()}{generate_punc(4)}**', s)
            
            await message.channel.send(s)
        
    @commands.Cog.listener("on_message")
    async def damn(self, message):
        if message.author == self.bot.user:
            return
        
        if message.channel.id in IGNORE_CHS:
            return
        
        s = preprocess(message.content)
        
        if re.search(self.damn_pattern, s):
            self.counter['beaver_count'] += len(re.findall(self.damn_pattern, s))
            with open(COUNTER_PATH, 'w') as file:
                json.dump(self.counter, file)
                
            s = re.sub(self.damn_pattern, lambda x: f'**{x.group()}**', s)
            s = re.sub(double_star_pattern, '', s)
            s = re.sub(r'\n', '\n> ', s)
            s = f'> {s}\nbeavers be like'
            
            await message.channel.send(s)
        
    @commands.Cog.listener("on_message")
    async def rand_eat(self, message: discord.Message):
        if not message.guild:
            return
        
        if message.channel.id in IGNORE_CHS:
            return
        
        last_called = 0
        if message.guild.id in self.time:
            last_called = self.time[message.guild.id]
            
        if random.random() < 1 / RANDOM_ENCOUNTER_PERIOD and time.time() > last_called + 5 * 60:
            self.time[message.guild.id] = time.time()
            
            name = None
            image_url = None
            image_bytes = None
            
            tries = 0
            while image_bytes == None:
                name = random.choice(self.nouns)
                    
                image_url = image_help.search_images(name)
                if image_url:
                    image_bytes = image_help.download_image(image_url)
                    
                tries += 1
                if tries > 10:
                    return
                
            
            name = name.split('_')
            name = ' '.join([x.capitalize() for x in name])
            webhook = await message.channel.create_webhook(name=name, avatar=image_bytes)
            
            script = random_encounter_script(name)
            
            persons = {
                '@p1': message.channel,
                '@p2': webhook
                }
            for line in script:
                await persons[line[0]].send(line[1])
                wait = line[1].count(' ') / 5
                await asyncio.sleep(wait)
                
            await webhook.delete()
        
    @app_commands.command(
        name="encounter",
        description="Creates an encounter"
    )
    async def force_encounter(self, interaction: discord.Interaction, noun: str=None):
        await interaction.response.defer()
        
        name = None
        image_url = None
        image_bytes = None
        
        tries = 0
        while image_bytes == None:
            name = noun or random.choice(self.nouns)
                
            try:
                image_url = image_help.search_images(name)
                if image_url:
                    image_bytes = image_help.download_image(image_url)
            except Exception as e:
                print(e)
                await interaction.followup.send(content='Failed')
                return
                
            tries += 1
            if tries > 10:
                await interaction.followup.send(content='Failed')
                return
                
        
        name = name.split('_')
        name = ' '.join([x.capitalize() for x in name])
        webhook = await interaction.channel.create_webhook(name=name, avatar=image_bytes)
        
        script = random_encounter_script(name)
        
        await interaction.followup.send(content='Encounter created')
        
        persons = {
            '@p1': interaction.channel,
            '@p2': webhook
            }
        for line in script:
            await persons[line[0]].send(line[1])
            wait = line[1].count(' ') / 5
            await asyncio.sleep(wait)
        
        await webhook.delete()
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(EatCog(bot), guilds=GUILDS)