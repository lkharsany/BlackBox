import os
import sys

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='./')

# NEED TO RUN IT WITH ARGUEMENT -t for testing
if (len(sys.argv) - 1) != 0 and sys.argv[1] == "-t":
    from distest.patches import patch_target
    bot = patch_target(bot)


bot.load_extension("cogs.BasicCog")

bot.run(TOKEN)
