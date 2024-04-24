import discord
from discord.ext import commands
from discord import app_commands

import asyncio
import audioop
from typing import Optional

import tts_request

YODA_SNAKE_WINNING_URL = 'https://storage.googleapis.com/vocodes-public/media/7/n/e/f/6/7nef61js0hbq9vvvv5666xbd29p44bfs/fakeyou_7nef61js0hbq9vvvv5666xbd29p44bfs.wav'

LIST = tts_request.request_list()

class TTSSource(discord.PCMVolumeTransformer):
    FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
    
    def __init__(self, ctx: discord.Interaction, source: discord.FFmpegPCMAudio, *, url: str, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.user
        self.channel = ctx.channel
        self.url = url
    
    @classmethod
    def create_source(cls, ctx: discord.Interaction, url: str):
        return cls(ctx, discord.FFmpegPCMAudio(url, **cls.FFMPEG_OPTIONS), url=url)
    
    
class MultiSource(discord.AudioSource):
    def __init__(self, sources: list[discord.AudioSource], *, volume: float = 1):
        self.sources: discord.AudioSource = sources
        self._volume: float = volume
        self._done: bool = False
        
    @property
    def volume(self) -> float:
        """Retrieves or sets the volume as a floating point percentage (e.g. ``1.0`` for 100%)."""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(value, 0.0)
        
    def add_source(self, new_source: discord.AudioSource):
        self.sources.append(new_source)

    def cleanup(self) -> None:
        for source in self.sources:
            source.cleanup()

    def read(self) -> bytes:
        ret = None
        
        for source in self.sources:
            aret = source.read()
            if aret:
                if ret:
                    ret = audioop.add(ret, aret, 2)
                else:
                    ret = aret
        
        if ret:
            return audioop.mul(ret, 2, min(self._volume, 2.0))
        else:   
            self._done = True
            return b''
    
    
class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: discord.Interaction):
        self.bot: commands.Bot = bot
        self._ctx: discord.Interaction = ctx
        self.voice: Optional[discord.VoiceClient] = None
        self.source: Optional[MultiSource] = None

    
class TTSCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        
        print('---\tTTSCog loaded\t\t---')
        
    async def cog_app_command_error(self, ctx: discord.Interaction[discord.Client], error: app_commands.AppCommandError) -> None:
        await ctx.response.send_message('An error occurred: {}'.format(str(error)))
        
    def get_voice_state(self, ctx: discord.Interaction):
        state = self.voice_states.get(ctx.guild_id)
        
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild_id] = state

        return state
        
    @app_commands.command(
        name='join',
        description='Join a voice channel'
    )
    async def summon(self, ctx: discord.Interaction, *, channel: discord.VoiceChannel=None):
        voice_state = self.get_voice_state(ctx)
        
        if not channel and not ctx.user.voice:
            await ctx.response.send_message('You are neither connected to a voice channel nor specified a channel to join.', ephemeral=True)

        destination = channel or ctx.user.voice.channel
        
        if voice_state.voice:
            await voice_state.voice.move_to(destination)
            return
        else:
            voice_state.voice = await destination.connect()
            
        await ctx.response.send_message(f'Connected to <#{destination.id}>')
        
    @app_commands.command(
        name='tts',
        description='TTS a message'
    )
    async def tts(self, ctx: discord.Interaction, *, text: str):
        await ctx.response.defer()
        url = await tts_request.request_tts_url(text)
        source = TTSSource.create_source(ctx, url)
        voice_state = self.get_voice_state(ctx)
        voice_state.voice.play(source)
        
        await ctx.followup.send(content='Message spoken')
        
    # @app_commands.command(
    #     name='sample',
    #     description='play a sound'
    # )
    # async def test(self, ctx: discord.Interaction):
    #     await ctx.response.defer()
    #     url = YODA_SNAKE_WINNING_URL
    #     source = TTSSource.create_source(ctx, url)
    #     voice_state = self.get_voice_state(ctx)
        
    #     if not voice_state.source or voice_state.source._done:
    #         voice_state.source = MultiSource([source])
    #         voice_state.voice.play(voice_state.source)
    #     else:
    #         voice_state.source.add_source(source)
        
    #     await ctx.followup.send(content='Acknowledged')
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(TTSCog(bot))