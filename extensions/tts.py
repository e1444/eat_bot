import discord
from discord.ext import commands
from discord import app_commands

import asyncio

import tts_request

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
    
    
class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: discord.Interaction):
        self.bot = bot
        self._ctx = ctx
        self.voice = None

    
class TTSCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        
        print('---\tTTSCog loaded\t\t---')
        
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
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(TTSCog(bot))