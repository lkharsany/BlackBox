import discord
from discord.ext import commands
import csv
import pandas as pd
import asyncio


class ReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='Reactions', brief="send reactions", description="Sends a csv file with reactions data")
    @commands.cooldown(1, 2)
    async def cool_bot(self, ctx):
        await ctx.send("CSV", file=discord.File('/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv'))

    #Detects when a reaction ia added to a message
    @commands.Cog.listener()
    @commands.cooldown(1,2)
    async def on_raw_reaction_add(self, payload):

        Good = ['👍','💯','🙌','👏']
        Bad = ['👎','😭','😕']

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = str(payload.emoji)
        print(message.content)
        print(emoji)

        info = []
        info.append(message.id)
        info.append(message.content)
        if emoji in Good:
            info.append(1)
        else:
            info.append(0)

        if emoji in Bad:
            info.append(1)
        else:
            info.append(0)
        if emoji not in Good and emoji not in Bad:
            info.append(1)
        else:
            info.append(0)

        info.append(1)

        print('info:', info)

        '''
        temp_df = pd.DataFrame({"Message_ID":[info[0]],"Message":[info[1]],"Good_Reactions":[info[2]],
                                "Bad_Reactions:":[info[3]],"Other_reactions":[info[4]],
                                "Total_Reaction":[1]})
          #/ home / neeloufah / PycharmProjects / BlackBox / src / cogs

        print(temp_df)

        df = pd.read_csv("/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv")
        df.append(temp_df)
        print(df)
        '''
        with open('/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv') as f_r:
            reader = csv.reader(f_r.readlines(), delimiter=',')
        with open('/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv', 'w') as f:

            writer = csv.writer(f)
            exist = 0
            for row in reader:
                print(row)
                if (row[0] == str(message.id)):
                    if emoji in Good:
                        row[2] = int(row[2]) + 1
                        row[5] = int(row[5]) + 1
                        writer.writerow(row)

                    if emoji in Bad:
                        row[3] = int(row[3]) + 1
                        row[5] = int(row[5]) + 1
                        writer.writerow(row)

                    if emoji not in Good and emoji not in Bad:
                        row[4] = int(row[4]) + 1
                        row[5] = int(row[5]) + 1
                        writer.writerow(row)

                    exist = 1

                else:
                    writer.writerow(row)
            if(exist == 0):
                writer.writerow(info)

            f.close()



        #await channel.send("CSV", file=discord.File('/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv'))


       # await channel.send(f"{user.mention} reacted to message")
        await channel.send('Reaction has been added to message')

    @commands.Cog.listener()
    @commands.cooldown(1, 2)
    async def on_raw_reaction_remove(self, payload):

        Good = ['👍', '💯', '🙌', '👏']
        Bad = ['👎', '😭', '😕']

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = str(payload.emoji)
        print(message.content)
        print(emoji)

        '''
        temp_df = pd.DataFrame({"Message_ID":[info[0]],"Message":[info[1]],"Good_Reactions":[info[2]],
                                "Bad_Reactions:":[info[3]],"Other_reactions":[info[4]],
                                "Total_Reaction":[1]})
          #/ home / neeloufah / PycharmProjects / BlackBox / src / cogs

        print(temp_df)

        df = pd.read_csv("/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv")
        df.append(temp_df)
        print(df)
        '''
        with open('/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv') as f_r:
            reader = csv.reader(f_r.readlines(), delimiter=',')
        with open('/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv', 'w') as f:

            writer = csv.writer(f)
            for row in reader:
                print(row)
                if (row[0] == str(message.id)):
                    if emoji in Good:
                        row[2] = int(row[2]) - 1
                        row[5] = int(row[5]) - 1
                        writer.writerow(row)

                    if emoji in Bad:
                        row[3] = int(row[3]) - 1
                        row[5] = int(row[5]) - 1
                        writer.writerow(row)

                    if emoji not in Good and emoji not in Bad:
                        row[4] = int(row[4]) - 1
                        row[5] = int(row[5]) - 1
                        writer.writerow(row)


                else:
                    writer.writerow(row)

            f.close()

        # await channel.send("CSV", file=discord.File('/home/neeloufah/PycharmProjects/BlackBox/src/cogs/Reactions.csv'))

        #await channel.send(f"{user.mention} reacted to message")

        await channel.send('Reaction has been removed from message')

def setup(bot):
    bot.add_cog(ReactionCog(bot))
