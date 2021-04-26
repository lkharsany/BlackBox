from discord.ext import commands
import asyncio

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='CoolBot')
    @commands.cooldown(1, 2)
    async def cool_bot(self, ctx):
        await ctx.send('This bot is cool. :)')

    @commands.command(name='Scrum')
    async def scrum(self, ctx):
        await ctx.send('Master')

    @commands.command(name='bye')
    async def shutdown(self, ctx):
        await ctx.send('Shutting Down')
        await asyncio.sleep(5)
        await self.bot.logout()

    # WILL DM THE PERSON WHO INVOKES THE COMMAND
    @commands.command(name="DM")
    @commands.cooldown(1, 2)
    async def poke(self, ctx):
        await ctx.send('DM sent')
        await ctx.author.send('beep boop!')

    # MONITORS ALL MESSAGES AND IF CERTAIN PHRASES ARE SAID IT WILL RESPOND.
    # CAN ONLY HAVE ONE LISTENERS (PER COG?)
    @commands.Cog.listener()
    @commands.cooldown(1, 2)
    async def on_message(self, message):
        if message.content.lower() == "hi":
            await message.channel.send('Hello there')
            await self.bot.process_commands(message)

        if message.content.lower() == "ping":
            await message.channel.send('Pong!')
            await self.bot.process_commands(message)

        if message.attachments:
            Blacklist = ["py", "java", "cpp", "html", "js", "c", ".txt", "jpg", "jpeg", "png", "svg"]
            filename = message.attachments[0].filename
            ext = filename.split(".")[-1]
            if ext in Blacklist:
                await asyncio.sleep(1)
                await message.delete()
                await message.channel.send("Attachment Deleted. \n Please refrain from sending images or code.")

    # CLEARS THE CHANNEL COMPLETELY ONLY A PERSON WITH ROLE "SCRUM MASTER" CAN USE IT
    @commands.command(name="Clear")
    @commands.cooldown(1, 2)
    async def clear(self, ctx):
        await ctx.channel.purge()


def setup(bot):
    bot.add_cog(BasicCog(bot))
