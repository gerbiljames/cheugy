import asyncio

from discord import FFmpegPCMAudio
from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoPrivate, MembersOnly, VideoUnavailable
from .stream_queue import StreamQueue

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
sessions = {}

ok_emoji = "👌"


def find_channel(ctx):
    voice = ctx.author.voice
    if voice is not None:
        return voice.channel
    return None


def find_or_create_session(ctx, loop):

    print("Finding session...")

    session = sessions.get(ctx.guild.id)

    if session is None:
        print("Creating session...")
        session = Session(guild=ctx.guild, loop=loop)
        sessions[ctx.guild.id] = session

    return session


async def play(url, ctx, loop):

    print("Got play command for %s" % url)

    await ctx.response.defer(ephemeral=False)

    channel = find_channel(ctx)

    session = find_or_create_session(ctx, loop)

    try:
        await session.join_channel(ctx, channel)
    except ValueError:
        await ctx.respond("Nice try, but you're not in a voice channel.")

    session.clear_queue()

    source = await get_audio_source(url, ctx)

    if source:
        session.add_stream(source)
        await session.play_next()
        await ctx.respond("▶ Playing %s" % url)


async def stop(ctx, loop):

    print("Got stop command")

    session = find_or_create_session(ctx, loop)
    session.clear_queue()
    session.stop_stream()
    await ctx.respond("⏹ Stopping all playback")


async def pause_or_resume(ctx, loop):
    session = find_or_create_session(ctx, loop)

    if session.is_playing():
        session.pause_stream()
    else:
        session.resume_stream()

    await ctx.respond(ok_emoji)


async def resume(ctx, loop):
    session = find_or_create_session(ctx, loop)

    if not session.is_paused():
        await ctx.respond("🤦 You numpty! There's either already something playing or nothing to resume.")
        return

    find_or_create_session(ctx, loop).resume_stream()
    await ctx.respond(ok_emoji)


async def queue(url, ctx, loop):
    if not url:
        await ctx.respond("🤦 You didn't specify anything to add...")
        return

    session = find_or_create_session(ctx, loop)

    if session.is_playing():
        source = await get_audio_source(url, ctx)
        if source:
            session.add_stream(source)
            await ctx.respond(ok_emoji)
    else:
        await play(url, ctx, loop)


async def clear(ctx, loop):
    find_or_create_session(ctx, loop).clear_queue()
    await ctx.respond(ok_emoji)


async def repeat(ctx, loop):
    if find_or_create_session(ctx, loop).toggle_repeat():
        await ctx.respond("🔁 Repeat mode enabled. The current or next played song will repeat.")
    else:
        await ctx.respond("⛔ Repeat mode disabled.")


async def skip(ctx, loop):
    find_or_create_session(ctx, loop).stop_stream()
    await ctx.respond(ok_emoji)


async def status(ctx, loop):
    session = find_or_create_session(ctx, loop)

    response = ""

    if session.is_playing():
        response += "▶ The bot is playing"
    else:
        response += "⏹ The bot is not playing"

    response += "\n🚶 There are {} song(s) in the queue 🚶🚶🚶🚶".format(len(session.url_queue))

    if session.url_queue.repeat:
        response += "\n🔁 Repeat mode is enabled"
    else:
        response += "\n⛔ Repeat mode is disabled"

    await ctx.respond(response)


async def leave_channel_if_required(ctx, loop, before, after):
    await find_or_create_session(ctx, loop).leave_channel_if_required(before, after)


async def get_audio_source(url, ctx):
    audio = None

    print("Fetching audio source for %s" % url)

    try:
        audio = YouTube(url).streams.get_audio_only()
    except RegexMatchError:
        await ctx.respond("❓ That's not a valid YouTube URL")
    except VideoPrivate:
        await ctx.respond("⛔ That video is private")
    except MembersOnly:
        await ctx.respond("🚫 That video is members only")
    except VideoUnavailable:
        await ctx.respond("❓ That video does not exist")

    return audio


class Session:

    def __init__(self, guild, loop):
        self.guild = guild
        self.loop = loop
        self.voice_client = None
        self.url_queue = StreamQueue()

    async def join_channel(self, ctx, channel):

        if channel is None:
            raise ValueError()

        if self.voice_client is not None and channel.id == self.voice_client.channel.id:
            print("Already connected to channel {0} on {1}".format(channel, ctx.guild))
            return

        if self.voice_client is not None:
            await self.voice_client.disconnect()

        self.voice_client = await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

        print("Connected to channel {0} on {1}".format(channel, ctx.guild))

    async def play_stream(self, stream):

        print("Playing stream")

        if self.voice_client is None:
            raise ValueError("Voice client is None, something went a bit wrong.")

        if self.voice_client.is_playing():
            self.stop_stream()

        def after(error):

            if error:
                return

            coro = self.play_next()
            fut = asyncio.run_coroutine_threadsafe(coro, self.loop)

            try:
                fut.result()
            except:
                pass

        self.voice_client.play(stream, after=after)

    async def play_next(self):

        print("Playing next audio")

        next_stream = self.url_queue.next()

        if next_stream:
            await self.play_stream(FFmpegPCMAudio(next_stream.url, **FFMPEG_OPTIONS))
            return True

        return False

    async def leave_channel_if_required(self, before, after):
        if self.voice_client is None:
            return

        if before.channel is None:
            return

        if before.channel.id != self.voice_client.channel.id:
            return

        members = list(filter(lambda member: not member.bot, before.channel.members))

        if len(members) != 0:
            return

        await self.voice_client.disconnect()
        self.voice_client = None

        self.url_queue.clear()

        print("Left channel {0} on {1}".format(before.channel, before.channel.guild))

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

    def add_stream(self, stream):
        self.url_queue.add(stream)

    def toggle_repeat(self):
        self.url_queue.repeat = not self.url_queue.repeat
        return self.url_queue.repeat

    def clear_queue(self):
        self.url_queue.clear()
