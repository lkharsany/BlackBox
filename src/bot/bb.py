import discord
from discord.ext import commands
import nest_asyncio

TOKEN ='ODI3MTM3ODgzMzU3NzA4Mjg4.YGWqLg.Yur5_cEMfMTrQbtlhstHCle2rWU'


nest_asyncio.apply()

bot = commands.Bot(command_prefix='./')

@bot.event
async def on_ready():
    print('Pravesh is the OG')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('./matty'):
        await message.channel.send('taiga')
    if message.content.startswith('./scrum'):
        await message.channel.send('Master')
    if message.content.startswith('./pravesh'):
        await message.channel.send('the OG')
    if message.content.startswith('./TutorQ'):
        await message.channel.send('Your question will be added to the que')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount)


bot.run(TOKEN)
