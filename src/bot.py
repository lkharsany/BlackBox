import discord
from discord.ext import commands

import os

from dotenv.main import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='./')

bot.load_extension("cogs.BasicCog")

bot.run(TOKEN)