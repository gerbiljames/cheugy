import os
import typing

import discord
from dotenv import load_dotenv
from cheugy import youtube

load_dotenv()
TOKEN = os.getenv('TOKEN')
DEBUG_GUILDS = os.getenv('DEBUG_GUILDS')

bot = discord.Bot(debug_guilds=DEBUG_GUILDS.split(',') if DEBUG_GUILDS else None)


@bot.event
async def on_ready():
    print("Connected successfully as {0}".format(bot.user))


@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        return

    await youtube.leave_channel_if_required(member, bot.loop, before, after)


@bot.slash_command(name="play", description="Plays a Youtube URL")
async def play(ctx, url: typing.Optional[str] = None):
    if url is not None:
        await youtube.play(url, ctx, bot.loop)
    else:
        await resume(ctx)


@bot.slash_command(name="pause", description="Pause the current audio")
async def pause(ctx):
    await youtube.pause_or_resume(ctx, bot.loop)


@bot.slash_command(name="resume", description="Resume the current audio")
async def resume(ctx):
    await youtube.resume(ctx, bot.loop)


@bot.slash_command(name="stop", description="Stops the current audio")
async def stop(ctx):
    await youtube.stop(ctx, bot.loop)


@bot.slash_command(name="queue", description="Adds a Youtube URL to the queue")
async def queue(ctx, url: str):
    await youtube.queue(url, ctx, bot.loop)


@bot.slash_command(name="clear", description="Clears the queue")
async def clear(ctx):
    await youtube.stop(ctx, bot.loop)
    await youtube.clear(ctx, bot.loop)


@bot.slash_command(name="skip", description="Skips the current audio")
async def skip(ctx):
    await youtube.skip(ctx, bot.loop)


@bot.slash_command(name="status", description="Informs on the bot status")
async def status(ctx):
    await youtube.status(ctx, bot.loop)


@bot.slash_command(name="repeat", description="Toggles repeat mode")
async def repeat(ctx, url: typing.Optional[str] = None):
    if url is not None:
        await youtube.play(url, ctx, bot.loop)
    await youtube.repeat(ctx, bot.loop)

bot.run(TOKEN)
