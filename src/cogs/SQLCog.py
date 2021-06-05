import os
from datetime import datetime

import pymysql.cursors
import discord
from discord.ext import commands
from discord.utils import get, find
from sshtunnel import SSHTunnelForwarder
import pandas as pd

AskBrief = "Usage: Ask <question>\nAdds Question to the Database"
answeredBrief = "Usage: Answer <question id>\n Will then need to send your answer prefixed with  the \"answer:\" when " \
                "prompted \nRemoves Answered Question from Database "
WhoDesc = "Displays all Questions, Users and ID as an Embeded Message\n Only Users with  Allocated Roles Can Access " \
          "This Command "
AnsweredDesc = "Removes Answered Question from Database and adds It to the answered Table \n Only Users with " \
               "Allocated Roles Can Access This Command "

FAQBrief = "Creates a FAQ Channel with all previously answered questions"


class DBConnect:
    def __init__(self):
        self._username = os.getenv('db_username')
        self._password = os.getenv('db_password')
        self._ssh_host = os.getenv('ssh_host')
        self._database = os.getenv('database')

    def _ConnectServer(self):
        server = SSHTunnelForwarder(
            (self._ssh_host, 22),
            ssh_username=self._username,
            ssh_password=self._password,
            remote_bind_address=('127.0.0.1', 3306)
        )
        return server

    def open(self):
        self._Server = self._ConnectServer()
        self._Server.start()
        connection = pymysql.connect(
            host='127.0.0.1',
            user=self._username,
            password=self._password,
            database=self._database,
            port=self._Server.local_bind_port,
            cursorclass=pymysql.cursors.DictCursor)

        self.Connection = connection
        return self.Connection

    def close(self):
        self.Connection.close()
        self._Server.stop()


class TravisDBConnect:
    def __init__(self):
        self._username = "root"
        self._password = ""
        self._database = "testDB"

    def open(self):
        connection = pymysql.connect(
            host='127.0.0.1',
            user=self._username,
            password=self._password,
            database=self._database,
            port=3306,
            cursorclass=pymysql.cursors.DictCursor)

        self.Connection = connection
        return self.Connection

    def close(self):
        self.Connection.close()


def addQuestion(table, val, isBot):
    # tries to insert values into table.
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (username, question, question_date, question_time,channel) Values (%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def queryQuestions(table, isBot, Channel):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} WHERE channel =%s"""
        cur.execute(Q, (Channel,))
        result = cur.fetchall()
        Db.close()
        return result
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def getQuestionRow(table, ID, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:

        conn = Db.open()
        cur = conn.cursor()
        Q = f"""SELECT * FROM {table} WHERE id = %s"""
        cur.execute(Q, (ID,))

        result = cur.fetchone()
        Db.close()
        if result:
            return result
        else:
            return -1
    except Exception as e:
        print(e)
        Db.close()
        return -1


def addAnswer(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (asked_by, question, question_date, question_time, answered_by, answer, answer_date, answer_time,channel) Values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def delQuestion(table, ID, isBot, isLecture):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        if isLecture:
            Q = f"""DELETE FROM {table} WHERE question_id = %s """
        else:
            Q = f"""DELETE FROM {table} WHERE id = %s """
        cur.execute(Q, (ID,))
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def createQuestionEmbed(member, question, asked_date, asked_time, ID):
    asked_date = datetime.strptime(str(asked_date), '%Y-%m-%d').strftime('%d-%m-%y')
    embed = discord.Embed(color=0xff9999, title="", description=member.mention)
    embed.set_author(name=member.name, url=discord.Embed.Empty, icon_url=member.avatar_url)
    embed.add_field(name="Question Asked", value=question + "\n", inline=False)
    embed.add_field(name="Asked On", value=str(asked_date) + "\n" + str(asked_time) + "\n", inline=False)
    embed.set_footer(text=f"Question ID:  {str(ID)}")
    return embed


def queryAnswers(table, isBot, channel):
    try:
        if isBot:
            Db = TravisDBConnect()
        else:
            Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} where channel = %s"""
        cur.execute(Q, (channel,))
        result = cur.fetchall()
        return result
    except pymysql.err as err:
        print(err)
        return -1


def createAnswerEmbed(ans_member, question, answer):
    embed = discord.Embed(color=0xff9999, title="", description="")
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=answer, inline=False)
    embed.set_footer(text=f"Answered By: {ans_member.name}")
    return embed


def addReferredQuestions(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (asked_by, question_id, question, question_date, question_time, referred_by, channel) Values (%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1

    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def getReferredQuestionRow(table, ID, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:

        conn = Db.open()
        cur = conn.cursor()
        Q = f"""SELECT * FROM {table} WHERE question_id = %s"""
        cur.execute(Q, (ID,))

        result = cur.fetchone()
        Db.close()
        if result:
            return result
        else:
            return -1
    except Exception as e:
        print(e)
        Db.close()
        return -1


def addReaction(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()

        Q = f"""SELECT count(*) FROM {table} WHERE message_id = %s"""
        cur.execute(Q, val[0])

        doesMsgExist = cur.fetchone()
        doesMsgExist = doesMsgExist.get('count(*)')

        if (doesMsgExist > 0):

            if (val[3] == 1):
                Q = f"""UPDATE {table} SET good_reaction = good_reaction + 1, total_reaction = total_reaction + 1 WHERE message_id = %s """
                cur.execute(Q, val[0])
            if (val[4] == 1):
                Q = f"""UPDATE {table} SET bad_reaction = bad_reaction + 1, total_reaction = total_reaction + 1 WHERE message_id = %s """
                cur.execute(Q, val[0])
            if (val[5] == 1):
                Q = f"""UPDATE {table} SET other_reaction = other_reaction + 1, total_reaction = total_reaction + 1 WHERE message_id = %s """
                cur.execute(Q, val[0])
        else:
            Q = f"""INSERT INTO {table} (message_id, message, author, good_reaction, bad_reaction, other_reaction, total_reaction,guild) Values (%s,%s,%s,%s,%s,%s,%s,%s)"""
            print(val[7])
            cur.execute(Q, val)

        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def removeReaction(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()

        if (val[1] == 0):
            Q = f"""UPDATE {table} SET good_reaction = good_reaction - 1, total_reaction = total_reaction - 1 WHERE message_id = %s """
            cur.execute(Q, val[0])
        if (val[1] == 1):
            Q = f"""UPDATE {table} SET bad_reaction = bad_reaction - 1, total_reaction = total_reaction - 1 WHERE message_id = %s """
            cur.execute(Q, val[0])
        if (val[1] == 2):
            Q = f"""UPDATE {table} SET other_reaction = other_reaction - 1, total_reaction = total_reaction - 1 WHERE message_id = %s """
            cur.execute(Q, val[0])

        conn.commit()
        Db.close()
        return 1

    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def getReactionCSV(table, isBot, guild_ID):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} where guild = %s"""
        cur.execute(Q, (guild_ID,))
        result = cur.fetchall()
        Db.close()

        return result

    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


class SQLCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Commands to Add, Display and Remove Questions from a Database"

    # Ask command
    @commands.command(brief=AskBrief, description="Adds Question to the Database", usage="<question>", name='Ask')
    @commands.cooldown(1, 2)
    async def Ask(self, ctx, *, message):
        guild = ctx.guild.id
        user = ctx.message.author.id
        curr_date = datetime.now().strftime('%Y-%m-%d')
        curr_time = datetime.now().strftime('%H:%M:%S')
        val = (user, message, curr_date, curr_time, guild)
        # used to "override" the table that the question is added to for testing purposes
        isBot = True
        if not ctx.message.author.bot:
            table = "DiscordQuestions"
            isBot = False
        else:
            table = "TestDiscordQuestions"

        code = addQuestion(table, val, isBot)
        if code == 1:
            await ctx.send('Question Added')

    # Who command
    @commands.command(brief="Displays All Questions", description=WhoDesc, name='Who')
    @commands.cooldown(1, 2)
    # @commands.has_role("")
    async def Who(self, ctx, *, message=None):
        guild = ctx.guild.id
        # used to "override" the table that the question is added to for testing purposes
        isBot = True
        if not ctx.author.bot:
            table = "DiscordQuestions"
            isBot = False
        else:
            table = "TestDiscordQuestions"
        result = queryQuestions(table, isBot, guild)
        if result != -1:
            if len(result) > 0:
                for r in result:
                    ID = r['id']
                    user_id = int(r["username"])
                    question = r["question"]
                    asked_date = r["question_date"]
                    asked_time = r["question_time"]
                    channel = r["channel"]
                    member = await ctx.bot.fetch_user(user_id)
                    embed = createQuestionEmbed(member, question, asked_date, asked_time, ID)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("No Open Questions. Nice!")

    @commands.cooldown(1, 2)
    @commands.command(brief=answeredBrief, description=AnsweredDesc, usage="<question id>", name='Answer')
    # @commands.has_role("")
    async def waitForReply(self, ctx, *, message):
        guild = ctx.guild.id
        ansID = message
        if ansID.isdigit():
            ansID = int(ansID)
            isBot = True
            if not ctx.author.bot:
                ansTable = "DiscordAnswers"
                qTable = "DiscordQuestions"
                isBot = False
            else:
                ansTable = "TestDiscordAnswers"
                qTable = "TestDiscordQuestions"

            result = getQuestionRow(qTable, ansID, isBot)

            if result != -1:
                ID = result['id']
                asked_by = int(result["username"])
                question = result["question"]
                asked_date = result["question_date"]
                asked_time = result["question_time"]

                member = await ctx.bot.fetch_user(asked_by)
                embed = createQuestionEmbed(member, question, asked_date, asked_time, ID)

                await ctx.send(embed=embed)
                await ctx.send(f"What's the answer? Begin with the phrase \"answer: \"")

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author and "answer" in m.content.lower()

                msg = await self.bot.wait_for("message", check=check)
                if msg:
                    ans_by = int(msg.author.id)
                    answer = msg.content.split(" ", 1)[1]
                    curr_date = datetime.now().strftime('%Y-%m-%d')
                    curr_time = datetime.now().strftime('%H:%M:%S')
                    if not isBot:
                        asked_member = await ctx.bot.fetch_user(asked_by)
                        answered_member = await ctx.bot.fetch_user(ans_by)
                        await asked_member.send(f"You asked: {question}  \n Answer: {answer}  \n"
                                                f" Answered by:{answered_member.mention}")

                    val = (asked_by, question, asked_date, asked_time, ans_by, answer, curr_date, curr_time, guild)
                    code = addAnswer(ansTable, val, isBot)
                    if code == 1:
                        delCode = delQuestion(qTable, ID, isBot, False)
                        if delCode == 1:
                            await ctx.send("Question has been Answered")

                            if not isBot:
                                await ctx.invoke(self.bot.get_command('FAQ'), isBot=isBot)
        else:
            await ctx.send("Not a Valid Question ID")

    @commands.command(brief=FAQBrief, description=FAQBrief, name='FAQ')
    # @commands.has_role("")
    async def createChannel(self, ctx, *, isBot=True):
        guild = ctx.guild
        if not ctx.author.bot:
            table = "DiscordAnswers"
            isBot = False
            channel_name = "faq"
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: discord.PermissionOverwrite(send_messages=True),
            }
        else:
            table = "TestDiscordAnswers"
            channel_name = "test faq"
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=False),
                guild.me: discord.PermissionOverwrite(send_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True)
            }

        channel = get(guild.text_channels, name=channel_name)
        if channel:
            oldMessages = await channel.history(limit=200).flatten()
            for msg in oldMessages:
                await msg.delete()
        else:
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        result = queryAnswers(table, isBot, guild.id)
        if result != -1:
            if len(result) > 0:
                for r in result:
                    ID = r['id']
                    asked_by = int(r["asked_by"])
                    question = r["question"]

                    ans_by = int(r["answered_by"])
                    answer = r["answer"]

                    asked_member = await ctx.bot.fetch_user(asked_by)
                    answered_member = await ctx.bot.fetch_user(ans_by)
                    embed = createAnswerEmbed(answered_member, question, answer)
                    if not isBot:
                        await channel.send(embed=embed)
            else:
                await channel.send("Ask Some Stuff")
        if isBot:
            await ctx.send("FAQ Channel Created")
        else:
            await ctx.send("Updating FAQ")

    @commands.command(name='DELFAQ')
    # @commands.has_role("")
    async def delChannel(self, ctx):
        if not ctx.author.bot:
            channel_name = "faq"
        else:
            channel_name = "test-faq"
        guild = ctx.guild

        channel = get(guild.text_channels, name=channel_name)
        if channel:
            await channel.delete()
            await ctx.send("FAQ Channel Deleted")

    @commands.command(name='Refer')
    # @commands.has_role("")
    async def referQuestion(self, ctx, *, message):
        guild = ctx.guild.id
        author = ctx.author
        ansID = message
        roleName = "sudo dev."
        if ansID.isdigit():
            ansID = int(ansID)
            isBot = True

            if not ctx.author.bot:
                qTable = "DiscordQuestions"
                rTable = "LecturerQuestions"
                isBot = False
            else:
                qTable = "TestDiscordQuestions"
                rTable = "TestLecturerQuestions"
            role = find(lambda r: r.name == roleName, ctx.guild.roles)
            lecturer = None

            for user in ctx.guild.members:
                if role in user.roles:
                    lecturer = user

            if lecturer is not None:
                result = getQuestionRow(qTable, ansID, isBot)
                if result != -1:
                    ID = result['id']
                    asked_by = int(result["username"])
                    question = result["question"]
                    asked_date = result["question_date"]
                    asked_time = result["question_time"]

                    member = await ctx.bot.fetch_user(asked_by)
                    embed = createQuestionEmbed(member, question, asked_date, asked_time, ID)
                    embed.add_field(name="Referred By", value=author.name, inline=False)
                    embed.add_field(name="Server", value=ctx.guild.name, inline=False)
                    val = (asked_by, ansID, question, asked_date, asked_time, author.id, guild)
                    code = addReferredQuestions(rTable, val, isBot)
                    if code == 1:
                        if not isBot:
                            await lecturer.send(embed=embed)
                            await lecturer.send("Use Command \'./Lecturer\' <question id>")
                        await ctx.send("Message Sent to Lecturer")


        else:
            await ctx.send("Not a Valid Question ID")

    @commands.cooldown(1, 2)
    @commands.command(name='Lecturer')
    async def lecturer(self, ctx, *, message):
        ansID = message
        if ansID.isdigit():
            ansID = int(ansID)
            isBot = True
            if not ctx.author.bot:
                ansTable = "DiscordAnswers"
                qTable = "DiscordQuestions"
                rTable = "LecturerQuestions"
                isBot = False
            else:
                ansTable = "TestDiscordAnswers"
                qTable = "TestDiscordQuestions"
                rTable = "TestLecturerQuestions"

            result = getReferredQuestionRow(rTable, ansID, isBot)

            if result != -1:
                ID = result['question_id']
                asked_by = int(result["asked_by"])
                question = result["question"]
                asked_date = result["question_date"]
                asked_time = result["question_time"]
                referred_by = result["referred_by"]
                channel = result["channel"]

                ask_member = await ctx.bot.fetch_user(asked_by)
                refer_member = await ctx.bot.fetch_user(referred_by)

                embed = discord.Embed(color=0xff9999, title="", description=ask_member.mention)
                embed.set_author(name=ask_member.name, url=discord.Embed.Empty, icon_url=ask_member.avatar_url)
                embed.add_field(name="Question Asked", value=question + "\n", inline=False)

                await ctx.send(embed=embed)
                await ctx.send(f"What's the answer? Begin with the phrase \"answer: \"")

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author and "answer" in m.content.lower()

                msg = await self.bot.wait_for("message", check=check)
                if msg:
                    ans_by = int(msg.author.id)
                    answer = msg.content.split(" ", 1)[1]
                    curr_date = datetime.now().strftime('%Y-%m-%d')
                    curr_time = datetime.now().strftime('%H:%M:%S')
                    if not isBot:
                        ask_embed = discord.Embed(color=0xff9999, title="", description="Answer")
                        ask_embed.set_author(name=ctx.author.name, url=discord.Embed.Empty,
                                             icon_url=ask_member.avatar_url)
                        ask_embed.add_field(name="Question Asked", value=question, inline=False)
                        ask_embed.add_field(name="Answer", value=answer, inline=False)

                        r_embed = discord.Embed(color=0xff9999, title="", description="Answer")
                        r_embed.set_author(name=ctx.author.name, url=discord.Embed.Empty,
                                           icon_url=ask_member.avatar_url)
                        r_embed.add_field(name="Question Referred", value=question, inline=False)
                        r_embed.add_field(name="Answer", value=answer, inline=False)
                        if not isBot:
                            await ask_member.send(embed=ask_embed)
                            await refer_member.send(embed=r_embed)
                    val = (asked_by, question, asked_date, asked_time, ans_by, answer, curr_date, curr_time, channel)

                    code = addAnswer(ansTable, val, isBot)
                    if code == 1:
                        delCode = delQuestion(qTable, ID, isBot, False)
                        if delCode == 1:
                            rDelCode = delQuestion(rTable, ID, isBot, True)
                            if rDelCode == 1:
                                await ctx.send("Question has been Answered")

        else:
            await ctx.send("Not a Valid Question ID")

    @commands.command(name='ReactionStats', brief="send reactions", description="Sends a csv file with reactions data")
    @commands.cooldown(1, 2)
    async def reactionCSV(self, ctx):
        guild = ctx.guild.id

        isBot = True

        if not ctx.author.bot:
            table = "DiscordReactions"
            isBot = False
        else:
            table = "TestDiscordReactions"

        result = getReactionCSV(table, isBot, guild)

        if result != -1:

            df = pd.DataFrame.from_dict(result)

            df.drop(["id", 'message_id', 'guild'], axis=1, inplace=True)
            usernames = df["author"]
            for i in range(len(usernames)):
                member = await ctx.bot.fetch_user(usernames[i])
                name = member.display_name
                to_replace = usernames[i]
                df.replace(to_replace, name, inplace=True)

            if not isBot:
                file_path = r"../src/csv/Reactions_Stats.csv"
                df.to_csv(file_path, index=False)
                await ctx.author.send(file=discord.File(file_path))

            else:
                print(df)
                file_path = r"src/csv/TestReactions_Stats.csv"
                df.to_csv(file_path, index=False)

                with open('src/csv/RStatsComparison.csv', 'r') as t1, open('src/csv/TestReactions_Stats.csv',
                                                                           'r') as t2:
                    fileOne = t1.readlines()
                    fileTwo = t2.readlines()

                    print(fileOne)
                    print(fileTwo)

            await ctx.send("Reactions Stats file sent.")

        else:
            await ctx.send("An error has occurred")

    # Detects when a reaction ia added to a message
    @commands.Cog.listener()
    @commands.cooldown(1, 2)
    async def on_raw_reaction_add(self, payload):

        Good = ['👍', '💯', '🙌', '👏']
        Bad = ['👎', '😭', '😕']

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        #user = await self.bot.fetch_user(payload.user_id)
        emoji = str(payload.emoji)

        guild = payload.guild_id

        info = [message.id, message.content, message.author.id]
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

        member = payload.member

        isBot = True

        if not member.bot:
            table = "DiscordReactions"
            isBot = False
        else:
            table = "TestDiscordReactions"

        info.append(guild)
        code = addReaction(table, info, isBot)

        '''
        if(code == 1):
            await channel.send('Reaction has been added to message')
        '''

    @commands.Cog.listener()
    @commands.cooldown(1, 2)
    async def on_raw_reaction_remove(self, payload):

        Good = ['👍', '💯', '🙌', '👏']
        Bad = ['👎', '😭', '😕']

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        emoji = str(payload.emoji)

        if emoji in Good:
            val = (message.id, 0)
        elif emoji in Bad:
            val = (message.id, 1)
        else:
            val = (message.id, 2)

        isBot = True

        if not user.bot:
            table = "DiscordReactions"
            isBot = False
        else:
            table = "TestDiscordReactions"

        code = removeReaction(table, val, isBot)
        '''
        if (code == 1):
            await channel.send('Reaction has been removed from message')
        '''


def setup(bot):
    bot.add_cog(SQLCog(bot))
