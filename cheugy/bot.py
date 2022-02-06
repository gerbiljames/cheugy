import os
from discord.ext import commands
from dotenv import load_dotenv
from cheugy import youtube

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='~', case_insensitive=True)


@bot.event
async def on_ready():
    print("Connected successfully as {0}".format(bot.user))


@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        return

    await youtube.leave_channel_if_required(member, bot.loop, before, after)


@bot.command()
async def play(ctx, arg=None):
    if arg is not None:
        await youtube.play(arg, ctx, bot.loop)
    else:
        await resume(ctx)


@bot.command()
async def p(ctx, arg=None):
    await play(ctx, arg)


@bot.command()
async def pause(ctx):
    await youtube.pause_or_resume(ctx, bot.loop)


@bot.command()
async def resume(ctx):
    await youtube.resume(ctx, bot.loop)


@bot.command()
async def r(ctx):
    await resume(ctx)


@bot.command()
async def stop(ctx):
    await youtube.stop(ctx, bot.loop)


@bot.command()
async def s(ctx):
    await stop(ctx)


@bot.command()
async def queue(ctx, arg=None):
    await youtube.queue(arg, ctx, bot.loop)


@bot.command()
async def clear(ctx):
    await youtube.stop(ctx, bot.loop)
    await youtube.clear(ctx, bot.loop)


@bot.command()
async def skip(ctx):
    await youtube.skip(ctx, bot.loop)


@bot.command()
async def status(ctx):
    await youtube.status(ctx, bot.loop)


@bot.command()
async def repeat(ctx, arg=None):
    if arg is not None:
        await youtube.play(arg, ctx, bot.loop)
    await youtube.repeat(ctx, bot.loop)

bot.run(TOKEN)
