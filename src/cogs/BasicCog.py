from discord.ext import commands
import asyncio
import time

class BasicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Some Basic Commands"

    @commands.command(name='CoolBot', brief="Give it a try", description="Give it a try")
    @commands.cooldown(1, 2)
    async def cool_bot(self, ctx):
        await ctx.send('This bot is cool. :)')

    @commands.command(name='Scrum', brief="Give it a try", description="Give it a try")
    async def scrum(self, ctx):
        await ctx.send('Master')

    @commands.command(name='bye', hidden=True)
    async def shutdown(self, ctx):
        await ctx.send('Shutting Down...')
        await asyncio.sleep(3)
        await self.bot.logout()

    # WILL DM THE PERSON WHO INVOKES THE COMMAND
    @commands.command(name="DM", brief="Send a Direct Message to person who called it",
                      description="Send a Direct Message to person who called it")
    @commands.cooldown(1, 2)
    async def dm(self, ctx):
        if not ctx.author.bot:
            await ctx.author.send('BEEP BOOP!')
        await ctx.send('DM sent')

    # MONITORS ALL MESSAGES AND IF CERTAIN PHRASES ARE SAID IT WILL RESPOND.
    # CAN ONLY HAVE ONE LISTENERS (PER COG?)
    @commands.Cog.listener()
    @commands.cooldown(1, 2)
    async def on_message(self, message):
        if message.content.lower() == "hi":
            await message.channel.send('Hello there :)')
            await self.bot.process_commands(message)

        if message.content.lower() == "ping":
            await message.channel.send('Pong!')
            await self.bot.process_commands(message)

        if message.content == "ReactionsTestMessage":
            await message.add_reaction(emoji=u"\U0001F44D")
            await self.bot.process_commands(message)

        if message.attachments:
            Blacklist = ['c', 'html', 'jpeg', 'css', 'java', 'jpg', 'svg', '.txt', 'docx', 'js', 'py', 'ipynb', 'png',
                         'sql', 'h', 'pdf', 'txt', 'cpp']
            filename = message.attachments[0].filename
            ext = filename.split(".")[-1]
            if ext in Blacklist:
                await asyncio.sleep(1)
                await message.delete()
                await message.channel.send("Attachment Deleted. \n Please refrain from sending images or code on this "
                                           "channel.")

                if not message.author.bot:
                    await message.author.send('Please do not send code to the channel, if you need help DM one of the '
                                              'tutors or lecturers.')
                await self.bot.process_commands(message)

    # CLEARS THE CHANNEL COMPLETELY ONLY A PERSON WITH ROLE CAN USE IT
    @commands.command(name="Clear", brief="Clears Messages in Channel",
                      description="Delete x Amount of Messages in Channel \nOnly Users With an Allocated Role can use "
                                  "this Command")
    @commands.cooldown(1, 2)
    # @commands.has_role("")
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)


def setup(bot):
    bot.add_cog(BasicCog(bot))
