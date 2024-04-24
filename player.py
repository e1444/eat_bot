import discord
from discord.ext import commands
from discord import app_commands

import audioop

from typing import Optional


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
    def __init__(self):
        self.voice: Optional[discord.VoiceClient] = None
        self.source: Optional[MultiSource] = None
        
    async def stop(self):
        if self.voice:
            await self.voice.disconnect()
            self.voice = None
        

class AudioPlayer:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.voice_states: dict[str, VoiceState] = dict()
        
    def get_voice_state(self, ctx: discord.Interaction):
        state = self.voice_states.get(ctx.guild_id)
        
        if not state:
            state = VoiceState()
            self.voice_states[ctx.guild_id] = state

        return state
    
    async def _is_joined(self, ctx):
        voice_state = self.get_voice_state(ctx)
        return bool(voice_state.voice)
    
    async def _join(self, ctx: discord.Interaction, *, channel: discord.VoiceChannel=None):
        voice_state = self.get_voice_state(ctx)
        
        if not channel and not ctx.user.voice:
            # await ctx.response.send_message('You are neither connected to a voice channel nor specified a channel to join.', ephemeral=True)
            return

        destination = channel or ctx.user.voice.channel
        
        if voice_state.voice:
            await voice_state.voice.move_to(destination)
            return
        else:
            voice_state.voice = await destination.connect()
            
        # await ctx.response.send_message(f'Connected to <#{destination.id}>')
    
    async def _leave(self, ctx: discord.Interaction, *, channel: discord.VoiceChannel=None):
        voice_state = self.get_voice_state(ctx)
        if not voice_state.voice:
            # return await ctx.send('Not connected to any voice channel.')
            pass
        
        await voice_state.stop()
        del self.voice_states[ctx.guild_id]
        
    async def _play(self, ctx: discord.Interaction, source: discord.AudioSource):
        voice_state = self.get_voice_state(ctx)
        
        if not voice_state.source or voice_state.source._done:
            voice_state.source = MultiSource([source])
            voice_state.voice.play(voice_state.source)
        else:
            voice_state.source.add_source(source)
        
        