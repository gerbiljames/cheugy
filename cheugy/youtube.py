import re

import pafy
from discord import FFmpegPCMAudio

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
sessions = {}


def find_channel(ctx):
    voice = ctx.author.voice
    if voice is not None:
        return voice.channel
    return None


def find_or_create_session(ctx):
    session = sessions.get(ctx.guild.id)

    if session is None:
        session = Session(guild=ctx.guild)
        sessions[ctx.guild.id] = session

    return session


async def play(url, ctx):

    try:
        channel = find_channel(ctx)

        session = find_or_create_session(ctx)

        await session.join_channel(ctx, channel)

        await session.play_stream(url)

    except ValueError as error:
        await ctx.send(str(error))


async def stop(ctx):
    find_or_create_session(ctx).stop_stream()


class Session:

    def __init__(self, guild):
        self.guild = guild
        self.voice_client = None

    async def join_channel(self, ctx, channel):

        if channel is None:
            raise ValueError("Nice try, but you're not in a voice channel.")

        if self.voice_client is None:
            self.voice_client = await channel.connect()
            await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
        else:
            await self.voice_client.move_to(channel)

    async def play_stream(self, url):

        if self.voice_client is None:
            raise ValueError("Voice client is None, something went a bit wrong.")

        self.stop_stream()

        source = self.get_audio_source(url)

        if source is None:
            raise ValueError("That's not a valid YouTube URL.")

        self.voice_client.play(source)

    def stop_stream(self):
        if self.voice_client is not None:
            self.voice_client.stop()

    def get_audio_source(self, url):
        video_ids = re.findall(r"watch\?v=(\S{11})", url)

        if len(video_ids) == 0:
            return None

        audio = pafy.new(video_ids[0]).getbestaudio()
        return FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
