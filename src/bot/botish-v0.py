import discord
from discord.ext import commands

from dotenv import load_dotenv
import os
load_dotenv()



TOKEN = os.getenv('TOKEN')
print(TOKEN)
