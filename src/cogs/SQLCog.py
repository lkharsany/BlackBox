import os
from datetime import datetime
from typing import DefaultDict

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
userParticipation = "shows how many questions a user has asked/answered in the server"


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


def QuestionStats(qTable, aTable, guild_id, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()

    try:
        conn = Db.open()
        cur = conn.cursor()

        Q1 = f"""SELECT username, COUNT(*) as COUNT FROM {qTable} WHERE channel = {guild_id} GROUP BY username"""
        cur.execute(Q1)
        result1 = cur.fetchall()

        Q2 = f"""SELECT asked_by, COUNT(*) as COUNT FROM {aTable} WHERE channel = {guild_id} GROUP BY asked_by"""
        cur.execute(Q2)
        result2 = cur.fetchall()
        Db.close()

        return result1, result2

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
        # guild = ctx.guild
        # print(guild)
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

    # questionstats command
    @commands.command(brief="Displays user participation", description=userParticipation, name='QuestionStats',
                      aliases=["Qstats", "qs"])
    @commands.cooldown(1, 2)
    async def QuestionStats(self, ctx):
        guild_id = str(ctx.guild.id)

        isBot = True

        if not ctx.author.bot:
            isBot = False
            qTable = "DiscordQuestions"
            aTable = "DiscordAnswers"
        else:
            qTable = "TestDiscordQuestions"
            aTable = "TestDiscordAnswers"

        result = QuestionStats(qTable, aTable, guild_id, isBot)

        if result != -1:
            result1 = result[0]
            result2 = result[1]

            r1 = pd.DataFrame.from_dict(result1)


            r2 = pd.DataFrame.from_dict(result2)


            if not r1.empty and not r2.empty:
                r1.columns = ["Username", "Unanswered_Questions"]
                r2.columns = ["Username", "Answered_Questions"]
                joint = r1.merge(r2, on="Username", how="outer").fillna(0)
                joint[['Unanswered_Questions', "Answered_Questions"]] = joint[
                    ['Unanswered_Questions', "Answered_Questions"]].astype(int)

            elif r1.empty:
                r2.columns = ["Username", "Answered_Questions"]
                joint = r2

            else:
                r1.columns = ["Username", "Unanswered_Questions"]
                joint = r1

            usernames = joint["Username"]
            for i in range(len(usernames)):
                member = await ctx.bot.fetch_user(usernames[i])
                name = member.display_name
                usernames[i] = name

            if not isBot:
                file_path = r"../src/csv/Question_Stats.csv"
                joint.to_csv(file_path, index=False)
                await ctx.author.send(file=discord.File(file_path))

            else:
                file_path = r"../src/csv/TestQuestion_Stats.csv"
                joint.to_csv(file_path, index=False)

            await ctx.send("Question Stats file sent.")


        else:
            ctx.send("An error has occurred")


def setup(bot):
    bot.add_cog(SQLCog(bot))
