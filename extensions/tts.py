import discord
from discord.ext import commands
from discord import app_commands
from bot import Bot

import asyncio
import audioop
from typing import Optional

import tts_request

YODA_SNAKE_WINNING_URL = 'https://storage.googleapis.com/vocodes-public/media/7/n/e/f/6/7nef61js0hbq9vvvv5666xbd29p44bfs/fakeyou_7nef61js0hbq9vvvv5666xbd29p44bfs.wav'

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

    
class TTSCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        
        print('---\tTTSCog loaded\t\t---')
        
    async def cog_app_command_error(self, ctx: discord.Interaction[discord.Client], error: app_commands.AppCommandError) -> None:
        await ctx.response.send_message('An error occurred: {}'.format(str(error)))
        
    @app_commands.command(
        name='tts',
        description='TTS a message'
    )
    async def tts(self, ctx: discord.Interaction, *, text: str):
        await ctx.response.defer()
        url = await tts_request.request_tts_url(text)
        source = TTSSource.create_source(ctx, url)
        
        if not await self.bot.audio_player._is_joined(ctx):
            await self.bot.audio_player._join(ctx)
            
        self.bot.audio_player._play(ctx, source)
        
        await ctx.followup.send(content='Message spoken')
        
    @app_commands.command(
        name='sample',
        description='play a sound'
    )
    async def test(self, ctx: discord.Interaction):
        await ctx.response.defer()
        url = YODA_SNAKE_WINNING_URL
        source = TTSSource.create_source(ctx, url)
        
        if not await self.bot.audio_player._is_joined(ctx):
            await self.bot.audio_player._join(ctx)
        
        await self.bot.audio_player._play(ctx, source)
        
        await ctx.followup.send(content='Acknowledged')
        
        
async def setup(bot: Bot):
    await bot.add_cog(TTSCog(bot))