import discord
from discord.ext import commands

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='CoolBot')
    async def cool_bot(self, ctx):
            await ctx.send('This bot is cool. :)')


    @commands.command(name='Scrum')
    async def cool_bot(self, ctx):
            await ctx.send('Master')



    @commands.Cog.listener()
    async def on_message(self,message):

        Cheers= [ "hi", "hello"]
        if message.content.lower() in Cheers:
            await message.channel.send('Hello there')
            await self.bot.process_commands(message)

        if message.content.lower() == "ping":
            await message.channel.send('Pong!')
            await self.bot.process_commands(message)


    @commands.command(name="Clear")
    async def clear(self, ctx):
        await ctx.channel.purge()







def setup(bot):
    bot.add_cog(BasicCog(bot))