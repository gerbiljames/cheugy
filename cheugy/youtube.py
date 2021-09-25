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


async def pause_or_resume(ctx):
    session = find_or_create_session(ctx)

    if session.is_playing():
        session.pause_stream()
    else:
        session.resume_stream()


async def resume(ctx):
    session = find_or_create_session(ctx)

    if not session.is_paused():
        await ctx.send("You numpty! There's either already something playing or nothing to resume.")
        return

    find_or_create_session(ctx).resume_stream()


class Session:

    def __init__(self, guild):
        self.guild = guild
        self.voice_client = None

    async def join_channel(self, ctx, channel):

        if channel is None:
            raise ValueError("Nice try, but you're not in a voice channel.")

        if self.voice_client is not None and channel.id == self.voice_client.channel.id:
            print("Already connected to channel {0} on {1}".format(channel, ctx.guild))
            return

        if self.voice_client is not None:
            await self.voice_client.disconnect()

        self.voice_client = await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

        print("Connected to channel {0} on {1}".format(channel, ctx.guild))

    async def play_stream(self, url):

        if self.voice_client is None:
            raise ValueError("Voice client is None, something went a bit wrong.")

        self.stop_stream()

        source = self.get_audio_source(url)

        if source is None:
            raise ValueError("That's not a valid YouTube URL.")

        self.voice_client.play(source)

        print("Playing {0}".format(url))

    def pause_stream(self):
        if self.voice_client is not None:
            self.voice_client.pause()

    def resume_stream(self):
        if self.voice_client is not None:
            self.voice_client.resume()

    def stop_stream(self):
        if self.voice_client is not None:
            self.voice_client.stop()

    def is_playing(self):
        if self.voice_client is not None:
            return self.voice_client.is_playing()
        else:
            return False

    def is_paused(self):
        if self.voice_client is not None:
            return self.voice_client.is_paused()
        else:
            return False

    def get_audio_source(self, url):
        video_ids = re.findall(r"watch\?v=(\S{11})", url)

        if len(video_ids) == 0:
            return None

        audio = pafy.new(video_ids[0]).getbestaudio()
        return FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
