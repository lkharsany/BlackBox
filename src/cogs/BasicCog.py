from discord.ext import commands


class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='CoolBot')
    async def cool_bot(self, ctx):
        await ctx.send('This bot is cool. :)')

    @commands.command(name='Scrum')
    async def master(self, ctx):
        await ctx.send('Master')

    # WILL DM THE PERSON WHO INVOKES THE COMMAND
    @commands.command(name="DM")
    async def poke(self, ctx):
        await ctx.send('DM sent')
        await ctx.author.send('beep boop!')

    # MONITORS ALL MESSAGES AND IF CERTAIN PHRASES ARE SAID IT WILL RESPOND.
    # CAN ONLY HAVE ONE LISTENERS (PER COG?)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == "hi":
            await message.channel.send('Hello there')
            await self.bot.process_commands(message)

        if message.content.lower() == "ping":
            await message.channel.send('Pong!')
            await self.bot.process_commands(message)

    # CLEARS THE CHANNEL COMPLETELY ONLY A PERSON WITH ROLE "SCRUM MASTER" CAN USE IT
    @commands.command(name="Clear")
    @commands.has_role('scrum master')
    async def clear(self, ctx):
        await ctx.channel.purge()


def setup(bot):
    bot.add_cog(BasicCog(bot))
