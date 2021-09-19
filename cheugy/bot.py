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
async def play(ctx, arg):
    await youtube.play(arg, ctx)


@bot.command()
async def p(ctx, arg):
    await youtube.play(arg, ctx)


@bot.command()
async def stop(ctx):
    await youtube.stop(ctx)


@bot.command()
async def s(ctx):
    await youtube.stop(ctx)

bot.run(TOKEN)
