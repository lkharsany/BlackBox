import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')



bot = commands.Bot(command_prefix='!')

bot.load_extension("cogs.BasicCog")

bot.run(TOKEN)