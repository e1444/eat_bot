import discord
from discord.ext import commands
from discord import app_commands

import json
from nltk.corpus import wordnet

import random
import re

from constants import *

def ansi_rarity(snake: str):
    i = snake.count('S')
    if i == 2:
        return C_WHITE
    elif i == 3:
        return C_BLUE
    elif i == 4:
        return C_YELLOW
    elif i >= 5:
        return C_RED

def hex_rarity(snake: str):
    i = snake.count('S')
    if i == 2:
        return 0xFFFFFF
    elif i == 3:
        return 0x5555FF
    elif i == 4:
        return 0xFFFF55
    else:
        return 0xFF5555
    
def snakeify(s: str):
    s = s.split('_')
    s = [x.capitalize() for x in s]
    s = ''.join(s)
    s = 'Snake' + s
    return s

class SnakeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        with open(SG_PATH, 'r') as file:
            self.snake_inv = json.load(file)
            
        all_words = wordnet.words()

        # Filter words that start with 's'
        self.s_words = [word for word in all_words if word.startswith('s')]
        
        print('---\tSnakeCog loaded\t\t---')
        
    @app_commands.command(
        name='snakerandom',
        description='SnakeSandom'
    )
    async def snake_random(self, interaction: discord.Interaction):
        word = str(random.choice(self.s_words))
        snake = snakeify(word)

        class ButtonView(discord.ui.View):
            def __init__(self, author, word, snake_inv):
                self.author = author
                self.word = word
                self.snake = snakeify(word)
                self.snake_inv = snake_inv
                super().__init__()
                
            @discord.ui.button(label="Add", style=discord.ButtonStyle.gray)
            async def add(self, int: discord.Interaction, button: discord.Button):
                if int.user.id != self.author.id:
                    await int.response.send_message('No touching other snakes', ephemeral=True)
                    return
                
                await int.response.defer()
                button.disabled = True
                
                user_id = str(self.author.id)
                
                if user_id not in self.snake_inv:
                    self.snake_inv[user_id] = list()
                    
                self.snake_inv[user_id].append(self.word)
                
                with open(SG_PATH, 'w') as file:
                    json.dump(self.snake_inv, file)
                
                await int.edit_original_response(view=self)
                    
            @discord.ui.button(label="Define", style=discord.ButtonStyle.gray)
            async def define(self, int: discord.Interaction, button: discord.Button):
                synsets = wordnet.synsets(self.word)
                if synsets:
                    s = ''
                    for synset in synsets:
                        s += f'{self.snake}: {synset.definition()}\n'
                    await int.response.send_message(s, ephemeral=True)
                else:
                    s = 'No definition found'
                    await int.response.send_message(s, ephemeral=True)
                    
        embed = discord.Embed(title='New Snake', description=snake)
        embed.colour = discord.Colour(hex_rarity(snake))
                
        await interaction.response.send_message(embed=embed, view=ButtonView(interaction.user, word, self.snake_inv))
            
    @app_commands.command(
        name='snakeinventory',
        description='Check out your snakes'
    )
    async def snake_inventory(self, interaction: discord.Interaction, member: discord.Member=None):
        user = member or interaction.user
        user_id = str(user.id)
            
        if user_id not in self.snake_inv:
            self.snake_inv[user_id] = list()
            
        s = '```ansi\n'
        i = 1
        for word in self.snake_inv[user_id][:50]:
            snake = snakeify(word)
            col = ansi_rarity(snake)
            s += f'{i}.    '[:5] + f'{col}{snake}{C_END}' + '\n'
            i += 1
        s += '```'
        
        pages = -(len(self.snake_inv[user_id]) // -50) # ceil division
            
        embed = discord.Embed(title="Inventory", description=s)
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        
        class Dropdown(discord.ui.Select):
            def __init__(self, author, snake_inv):
                self.author = author
                self.snake_inv = snake_inv
                
                # Set the options that will be presented inside the dropdown
                options = list()
                for i in range(pages):
                    options.append(discord.SelectOption(label=str(i + 1), description=f'{50 * i + 1}-{50 * (i + 1)}'))

                # The placeholder is what will be shown when no option is chosen
                # The min and max values indicate we can only pick one of the three options
                # The options parameter defines the dropdown options. We defined this above
                super().__init__(placeholder='Select page', min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                # Use the interaction object to send a response message containing
                # the user's favourite colour or choice. The self object refers to the
                # Select object, and the values attribute gets a list of the user's
                # selected options. We only want the first one.
                if interaction.user.id != self.author.id:
                    await interaction.response.send_message('No touching other snakes', ephemeral=True)
                    return
                
                page_start = (int(self.values[0]) - 1) * 50
            
                s = '```ansi\n'
                i = page_start + 1
                for word in self.snake_inv[user_id][page_start:page_start + 50]:
                    snake = snakeify(word)
                    col = ansi_rarity(snake)
                    s += f'{i}.    '[:5] + f'{col}{snake}{C_END}' + '\n'
                    i += 1
                s += '```'
                
                embed = discord.Embed(title="Inventory", description=s)
                embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
                
                await interaction.response.edit_message(embed=embed)

        class DropdownView(discord.ui.View):
            def __init__(self, author, snake_inv):
                super().__init__()

                # Adds the dropdown to our view object.
                self.add_item(Dropdown(author, snake_inv))
        
        view = DropdownView(interaction.user, self.snake_inv)
        
        await interaction.response.send_message(embed=embed, view=view)
            
    @app_commands.command(
        name='snakeremove',
        description='Remove a Snake'
    )
    async def snake_remove(self, interaction: discord.Interaction, index: int):
        index -= 1
        user_id = str(interaction.user.id)
        if user_id not in self.snake_inv:
            self.snake_inv[user_id] = list()
            
        if 0 > index >= len(self.snake_inv[user_id]):
            await interaction.response.send_message(f'Invalid index.')
            return
        
        word = self.snake_inv[user_id][index]
        self.snake_inv[user_id].pop(index)
                
        with open(SG_PATH, 'w') as file:
            json.dump(self.snake_inv, file)
            
        await interaction.response.send_message(f'Removed {index + 1}: {snakeify(word)}.')
            
    @app_commands.command(
        name='snakeflaunt',
        description='Flaunt that snake!'
    )
    async def snake_flaunt(self, interaction: discord.Interaction, index: int):
        user = interaction.user
        user_id = str(user.id)
        
        index -= 1
        
        if user_id not in self.snake_inv:
            self.snake_inv[user_id] = list()
            
        if 0 > index >= len(self.snake_inv[user_id]):
            await interaction.response.send_message(f'Invalid index.')
            return
        
        word = self.snake_inv[user_id][index]
        desc = ''
        
        synsets = wordnet.synsets(word)
        
        if synsets:
            i = 0
            for synset in synsets:
                desc += f'{i}. {synset.definition()}\n'
                i += 1    
        
        snake = snakeify(word)
        embed = discord.Embed(title=snake, description=desc)
        embed.colour = discord.Colour(hex_rarity(snake))
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
                
        await interaction.response.send_message(embed=embed)
            
            
async def setup(bot: commands.Bot):
    await bot.add_cog(SnakeCog(bot), guilds=GUILDS)
