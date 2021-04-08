from discord.ext import commands


class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='CoolBot')
    async def cool_bot(self, ctx):
        await ctx.send('This bot is cool. :)')

    @commands.command(name='Scrum')
    @commands.has_role('SCRUM MASTER')
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

        Cheers = ["hi", "hello"]
        if message.content.lower() in Cheers:
            await message.channel.send('Hello there! {}'.format(message.author.mention))
            await self.bot.process_commands(message)

        if message.content.lower() == "ping":
            await message.channel.send('Pong!')
            await self.bot.process_commands(message)

    # CLEARS THE CHANNEL COMPLETELY ONLY A PERSON WITH ROLE "SCRUM MASTER" CAN USE IT
    @commands.command(name="Clear")
    @commands.has_role('SCRUM MASTER')
    async def clear(self, ctx):
        await ctx.channel.purge()

    # CLEARS THE CHANNEL BY A SELECTED AMOUNT OF MESSAGES. ANYONE CAN USE IT AT THE MOMENT
    @commands.command(name="Clear")
    async def clear(self, ctx, amount=2):
        await ctx.channel.purge(limit=amount)


def setup(bot):
    bot.add_cog(BasicCog(bot))
