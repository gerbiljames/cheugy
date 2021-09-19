import os
from discord.ext import commands
from dotenv import load_dotenv
from cheugy import youtube

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='~')


@bot.event
async def on_ready():
    print("Connected successfully as {0}".format(bot.user))


@bot.command()
async def play(ctx, arg=None):
    if arg is not None:
        await youtube.play(arg, ctx)
    else:
        await resume(ctx)


@bot.command()
async def p(ctx, arg=None):
    await play(ctx, arg)


@bot.command()
async def pause(ctx):
    await youtube.pause(ctx)


@bot.command()
async def resume(ctx):
    await youtube.resume(ctx)


@bot.command()
async def r(ctx):
    await resume(ctx)


@bot.command()
async def stop(ctx):
    await youtube.stop(ctx)


@bot.command()
async def s(ctx):
    await stop(ctx)

bot.run(TOKEN)
