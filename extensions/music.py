import discord
from discord.ext import commands
from discord import app_commands

import yt_dlp as youtube_dl

import asyncio
import functools
import itertools
import math
import random

from bot import Bot

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: discord.Interaction, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.user
        self.channel = ctx.channel
        self.data = data
        self.volume = volume

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = int(data.get('duration'))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: discord.Interaction, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)
    
    def reset(self):
        discord.PCMVolumeTransformer.__init__(self, discord.FFmpegPCMAudio(self.data['url'], **self.FFMPEG_OPTIONS), self.volume)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        import time
        embed = (discord.Embed(title='Now playing',
                               description='```\n{0.source.title}\n```'.format(self),
                               color = 16202876)
                 .add_field(name='Progress', value=f'<t:{int(time.time()) + self.source.duration}:R>')
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 # .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class QueueManager:
    def __init__(self, bot: Bot, ctx: discord.Interaction):
        self.bot: Bot = bot
        self._ctx: discord.Interaction = ctx
        self._done = False

        self.current: Song = None
        self.next: asyncio.Event = asyncio.Event()
        self.songs: SongQueue = SongQueue()

        self._loop: bool = False
        self._volume: float = 1
        self.skip_votes: set = set()

        self.audio_player: asyncio.Task = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    def is_playing(self, ctx: discord.Interaction):
        return bool(self.current and self.bot.audio_player._is_playing(ctx))

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with asyncio.timeout(3):  # 3 minutes todo change back
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    # disconnect
                    self.bot.loop.create_task(self.leave())
                    self._done = True
                    return
                
            self.current.source.reset()
            await self.bot.audio_player._play(self._ctx, self.current.source, after=self.play_next_song)
            await self._ctx.channel.send(embed=self.current.create_embed())
            
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))
        self.next.set()

    def skip(self, ctx: discord.Interaction):
        if self.is_playing(ctx):
            self.bot.audio_player._stop(ctx)

    def stop(self):
        self.songs.clear()
        if self.is_playing(self._ctx):
            self.bot.audio_player._stop(self._ctx)
        self.next.set()

    async def leave(self):
        self.stop()
        await self.bot.audio_player._leave(self._ctx)


class MusicCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.queue_managers: dict[str, QueueManager] = {}
        
        print('---\tMusicCog loaded\t\t---')
    
    def get_queue_manager(self, ctx: discord.Interaction) -> QueueManager:
        qm = self.queue_managers.get(ctx.guild.id)
        
        if not qm or qm._done:
            qm = QueueManager(self.bot, ctx)
            self.queue_managers[ctx.guild.id] = qm

        return qm

    def cog_unload(self):
        for state in self.queue_managers.values():
            self.bot.loop.create_task(state.leave())

    async def cog_app_command_error(self, ctx: discord.Interaction[discord.Client], error: app_commands.AppCommandError) -> None:
        await ctx.response.send_message('An error occurred: {}'.format(str(error)))

    @app_commands.command(
        name='join',
        description='Joins your voice channel'
    )
    async def _join(self, ctx: discord.Interaction, *, channel: discord.VoiceChannel = None):
        destination = await self.bot.audio_player._join(ctx, channel=channel)
        await ctx.response.send_message(f'Connected to <#{destination.id}>')

    @app_commands.command(
        name='leave',
        description='Clears the queue and leaves the voice channel'
    )
    async def _leave(self, ctx: discord.Interaction):
        # todo clear queue
        await self.bot.audio_player._leave(ctx)
        await ctx.response.send_message(f'Left the voice channel.')

    @app_commands.command(
        name='current',
        description='Displays the currently playing song'
    )
    async def _now(self, ctx: discord.Interaction):
        qm = self.get_queue_manager(ctx)
        await ctx.response.send_message(embed=qm.current.create_embed())

    @app_commands.command(
        name='pause',
        description='Pause the music player'
    )
    async def _pause(self, ctx: discord.Interaction):
        self.bot.audio_player._pause(ctx)
        await ctx.response.send_message(f'Paused the music player.')

    @app_commands.command(
        name='resume',
        description='Resume the music player'
    )
    async def _resume(self, ctx: discord.Interaction):
        self.bot.audio_player._resume(ctx)
        await ctx.response.send_message(f'Resumed the music player.')

    @app_commands.command(
        name='stop',
        description='Stops the music player and clears the queue'
    )
    async def _stop(self, ctx: discord.Interaction):
        qm = self.get_queue_manager(ctx)
        qm.stop()
        
        await ctx.response.send_message(f'Stopped the music player.')

    @app_commands.command(
        name='skip',
        description='Skip the current song'
    )
    async def _skip(self, ctx: discord.Interaction):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        
        qm = self.get_queue_manager(ctx)
        if not qm.is_playing(ctx):
            return await ctx.send('Not playing any music currently.')
        
        qm.skip(ctx)
        await ctx.response.send_message(f'Skipped the current song.')

    @app_commands.command(
        name='queue',
        description='Show the player\'s queue'
    )
    async def _queue(self, ctx: discord.Interaction, *, page: int = 1):
        qm = self.get_queue_manager(ctx)
        if len(qm.songs) == 0:
            return await ctx.response.send_message('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(qm.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(qm.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(qm.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.response.send_message(embed=embed)

    @app_commands.command(
        name='shuffle',
        description='Shuffle the queue.'
    )
    async def _shuffle(self, ctx: discord.Interaction):
        qm = self.get_queue_manager(ctx)
        if len(qm.songs) == 0:
            return await ctx.response.send_message('Empty queue.')

        qm.songs.shuffle()
        return await ctx.response.send_message('Queue shuffled.')

    @app_commands.command(
        name='remove',
        description='Remove a song'
    )
    async def _remove(self, ctx: discord.Interaction, index: int):
        qm = self.get_queue_manager(ctx)
        if len(qm.songs) == 0:
            return await ctx.response.send_message('Empty queue.')
        name = str(qm.songs[index - 1].source)
        qm.songs.remove(index - 1)
        return await ctx.response.send_message(f'Removed {name}')

    @app_commands.command(
        name='loop',
        description='Toggle loop'
    )
    async def _loop(self, ctx: discord.Interaction):
        qm = self.get_queue_manager(ctx)
        if not qm.is_playing(ctx):
            return await ctx.response.send_message('Nothing being played at the moment.')

        qm.loop = not qm.loop
        if qm.loop:
            return await ctx.response.send_message(f'Looping {str(qm.current.source)}.')
        else:
            return await ctx.response.send_message('No longer looping.')

    @app_commands.command(
        name='play',
        description='Plays a song'
    )
    async def _play(self, ctx: discord.Interaction, *, search: str):
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not self.bot.audio_player._is_joined(ctx):
            await self.bot.audio_player._join(ctx)
            
        await ctx.response.defer()
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
        song = Song(source)
        qm = self.get_queue_manager(ctx)
        await qm.songs.put(song)
        
        await ctx.followup.send('Enqueued {}'.format(str(source)))

    
async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))