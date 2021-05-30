from discord.ext import commands
import asyncio


class ReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Detects when a reaction ia added to a message
    @commands.Cog.listener()
    @commands.cooldown(1,2)
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji
        print(message.content)
        print(emoji)

        await channel.send(f"{user.mention} reacted to message")

def setup(bot):
    bot.add_cog(ReactionCog(bot))
