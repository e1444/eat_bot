import discord
from discord.ext import commands
from typing import *

from constants import *
from player import AudioPlayer

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.webhooks = True
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix='$', intents=intents)
        
        self.audio_player: AudioPlayer = AudioPlayer(self)
        
    async def setup_hook(self) -> Coroutine[Any, Any, None]:
        # load extensions
        for extension in EXTENSIONS:
            await self.load_extension(extension)
    
    async def on_ready(self):
        # sync commands to guilds
        for guild in GUILDS:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        
        # load opus
        import ctypes.util
        discord.opus.load_opus(ctypes.util.find_library('libopus'))
        
        # check if opus is loaded
        if discord.opus.is_loaded():
            print('Opus successfully loaded')
        else:
            raise Exception('Error loading opus')
        
        # log
        print(f'We have logged in as {self.user}')