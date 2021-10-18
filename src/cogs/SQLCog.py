import os
from datetime import datetime
import pymysql.cursors
import discord
from discord.ext import commands
from discord.utils import get, find
from sshtunnel import SSHTunnelForwarder
import pandas as pd

answeredBrief = "Usage: Answer <question id>\nYou will then need to send your answer prefixed with the \"answer:\" " \
                "when " \
                "prompted. \nSends the answer to the person who asked the question"
AnsweredDesc = "Used by tutors or lecturers to answer questions asked by students. \nWill then send the answer to the " \
               "student who asked the question. "


WhoDesc = "Displays all Questions, Users and ID as an Embedded Message"
WhoBrief = "Displays all qustions asked by students as Embedded Messages"

AskBrief = "Usage: Ask <question>\nAdds Question to the Database"
AskDesc = "Adds Question to the database where it can be queried at later time"

QStatsBrief = "Generates a CSV file with the amount of questions students asked on the server is any."
QStatsDesc = "Sends a CSV via DM with the amount of questions students asked on the server is any."

RStatsBrief = "Generates a CSV file with the amount of reactions messages have if any."
RStatsDesc = "Sends a CSV via DM with the amount of positive or negative reactions messages have if any."

MStatsBrief = "Generates a CSV file with the amount of messages students have sent in the server"
MStatsDesc = "Sends a CSV via DM with the amount of messages students have sent in the server. \nThe messages are " \
             "grouped by length. "

DelFaqBrief = "Deletes the FAQ Channel if it exists"
FAQBrief = "Creates a FAQ Channel with all previously answered questions"

LecturerBrief = "Usage: Lecturer <question id>\nUsed by lecturer to answer referred questions"
LecturerDesc = "Used to answer referred question. \nIt will then send the answer to both the tutor and the person who " \
               "asked it "

ReferBrief = "Usage: Refer <question id>\nUsed by tutors to refer a question they don't know to the lecturer"
ReferDesc = "Refers a question to a lecturer.\nThe question will then be sent to the lecturer via dm"

isSSH = os.getenv('using_SSH')
if isSSH.lower() == "true": # pragma: no cover
    class DBConnect:  # pragma: no cover
        def __init__(self):
            self._username = os.getenv('db_username')
            self._password = os.getenv('db_password')
            self._ssh_host = os.getenv('ssh_host')
            self._database = os.getenv('db_database')
            self._ssh_username = os.getenv('ssh_username')
            self._ssh_password = os.getenv('ssh_password')

        def _ConnectServer(self):
            server = SSHTunnelForwarder(
                (self._ssh_host, 22),
                ssh_username=self._ssh_username,
                ssh_password=self._ssh_password,
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
else: # pragma: no cover
    class DBConnect: # pragma: no cover
        def __init__(self):
            self._username = os.getenv('db_username')
            self._password = os.getenv('db_password')
            self._database = os.getenv('db_database')

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
            self.Connection.close() # pragma: no cover


# USED FOR TESTING DO NOT CHANGE.
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
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (username, question, question_date, question_time,channel) Values (%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def queryQuestions(table, isBot, Channel):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} WHERE channel =%s"""
        cur.execute(Q, (Channel,))
        result = cur.fetchall()
        Db.close()
        return result
    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def getQuestionRow(table, ID, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
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
    except Exception as e:  # pragma: no cover
        print(e)
        Db.close()
        return -1


def addAnswer(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (asked_by, question, question_date, question_time, answered_by, answer, answer_date, answer_time,channel) Values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def delQuestion(table, ID, isBot, isLecture):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
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
    except pymysql.err as err:  # pragma: no cover
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
        else:  # pragma: no cover
            Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} where channel = %s"""
        cur.execute(Q, (channel,))
        result = cur.fetchall()
        return result
    except pymysql.err as err:  # pragma: no cover
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
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (asked_by, question_id, question, question_date, question_time, referred_by, channel) Values (%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1

    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def getReferredQuestionRow(table, ID, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
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
    except Exception as e:  # pragma: no cover
        print(e)
        Db.close()
        return -1


def QuestionStats(qTable, aTable, guild_id, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
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

    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def addReaction(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
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
            cur.execute(Q, val)

        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def removeReaction(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
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

    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def getReactionCSV(table, isBot, guild_ID):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} where guild = %s"""
        cur.execute(Q, (guild_ID,))
        result = cur.fetchall()
        Db.close()

        return result

    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


def AddMessageCount(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Val = [val[0], val[4]]
        Q = f"""SELECT count(*) FROM {table} WHERE discord_id = %s AND server_id = %s """
        cur.execute(Q, Val)

        newVal = [val[2], str(val[0]), str(val[4])]
        doesUserExist = cur.fetchone()
        doesUserExist = doesUserExist.get('count(*)')
        if doesUserExist > 0:
            if val[3] == 1:
                Q = f"""UPDATE {table} set record_count = record_count +1,last_message_date = %s, record_count_20 = 
                record_count_20 +1 WHERE  %s = discord_id AND server_id = %s """
                cur.execute(Q, newVal)
            else:
                Q = f"""UPDATE {table} set record_count = record_count +1,last_message_date = %s WHERE 
                discord_id = %s and server_id = %s """
                cur.execute(Q, newVal)
            conn.commit()
        else:
            if val[3] == 1:
                val = [val[0], val[1], 1, val[2], 1, val[4]]
                Q = f"""INSERT INTO {table} (discord_id, discord_username, record_count, last_message_date,
                record_count_20, server_id) Values (%s,%s,%s,%s,%s,%s) """
                cur.execute(Q, val)
            else:
                val = [val[0], val[1], 1, val[2], 0, val[4]]
                Q = f"""INSERT INTO {table} (discord_id, discord_username, record_count, last_message_date,
                record_count_20, server_id) 
                Values (%s,%s,%s,%s,%s,%s) """
                cur.execute(Q, val)
            conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def getMessageCSV(table, isBot, guild_ID):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} where server_id = %s"""
        cur.execute(Q, (guild_ID,))
        result = cur.fetchall()
        Db.close()

        return result

    except pymysql.err as err:  # pragma: no cover
        print(err)
        Db.close()
        return -1


class SQLCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Commands to Add, Display and Remove Questions from a Database"

    # Ask command
    @commands.command(name='Ask',brief=AskBrief, description=AskDesc, usage="<question>",aliases=["ask"])
    @commands.cooldown(1, 2)
    async def Ask(self, ctx, *, message):
        guild = ctx.guild.id
        user = ctx.message.author.id
        curr_date = datetime.now().strftime('%Y-%m-%d')
        curr_time = datetime.now().strftime('%H:%M:%S')
        val = (user, message, curr_date, curr_time, guild)
        # used to "override" the table that the question is added to for testing purposes
        isBot = True
        if not ctx.message.author.bot:  # pragma: no cover
            table = "DiscordQuestions"
            isBot = False
        else:
            table = "TestDiscordQuestions"

        code = addQuestion(table, val, isBot)
        if code == 1:
            await ctx.send('Question Added')

    # Who command
    @commands.command(name='Who', brief=WhoBrief, description=WhoDesc, aliases=["who"])
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

    #@commands.has_any_role('lecturer', 'Lecturer', 'tutor')
    @commands.cooldown(1, 2)
    @commands.command(name='Answer', brief=answeredBrief, description=AnsweredDesc, usage="<question id>",
                      aliases=["answer"])


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

    @commands.command(name='FAQ', brief=FAQBrief, description=FAQBrief, aliases=["faq"])
    # @commands.has_role("")
    async def createChannel(self, ctx, *, isBot=True, serverID=None):
        if serverID is not None:
            serverID = int(serverID)
            guild = self.bot.get_guild(serverID)
        else:
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
                    asked_by = int(r["asked_by"])
                    question = r["question"]

                    ans_by = int(r["answered_by"])
                    answer = r["answer"]

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

    @commands.command(name='DELFAQ', brief=DelFaqBrief, description=DelFaqBrief, aliases=["delfaq", "df"])
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

    @commands.command(name='Refer', brief=ReferBrief, description=ReferDesc, usage="<question id>",
                      aliases=["refer", "ref"])
    # @commands.has_role("")
    async def referQuestion(self, ctx, *, message):
        guild = ctx.guild.id
        author = ctx.author
        ansID = message
        roleName = "Not Lecturer"
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
    @commands.command(name='Lecturer', brief=LecturerBrief, description=LecturerDesc, usage="<question id>",
                      aliases=["lecturer", "lect"])
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

                                if not isBot:
                                    await ctx.invoke(self.bot.get_command('FAQ'), isBot=isBot, serverID=channel)
        else:
            await ctx.send("Not a Valid Question ID")

    @commands.command(brief=QStatsBrief,
                      description=QStatsDesc, name='QuestionStats',
                      aliases=["QStats", "qs"])
    @commands.cooldown(1, 2)
    async def questionCSV(self, ctx):
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
                to_replace = usernames[i]
                joint.replace(to_replace, name, inplace=True)

            if isBot:
                file_path = r"src/csv/TestQuestion_Stats.csv"
                joint.to_csv(file_path, index=False)

            else:  # pragma: no cover
                file_path = r"../src/csv/Question_Stats.csv"
                joint.to_csv(file_path, index=False)
                await ctx.author.send(file=discord.File(file_path))

            await ctx.send("Question Stats file sent.")

        else:
            ctx.send("An error has occurred")

    @commands.command(name='ReactionStats', brief=RStatsBrief,
                      description=RStatsDesc,
                      aliases=["RStats", "rs"])
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

            if not df.empty:
                df.drop(["id", 'message_id', 'guild'], axis=1, inplace=True)
                usernames = df.author.unique()
                for i in range(len(usernames)):
                    member = await ctx.bot.fetch_user(usernames[i])
                    name = member.display_name
                    to_replace = usernames[i]
                    df.replace(to_replace, name, inplace=True)

            if isBot:
                file_path = r"src/csv/TestReactions_Stats.csv"
                df.to_csv(file_path, index=False)

            else:  # pragma: no cover
                file_path = r"../src/csv/Reactions_Stats.csv"
                df.to_csv(file_path, index=False)
                await ctx.author.send(file=discord.File(file_path))

            await ctx.send("Reactions Stats file sent.")

        else:
            await ctx.send("An error has occurred")

    @commands.command(name='MessageStats', brief=MStatsDesc,
                      description=MStatsDesc,
                      aliases=["MStats", "ms"])
    async def messageCSV(self, ctx):

        guild = ctx.guild.id

        isBot = True

        if not ctx.author.bot:
            table = "student_message_log"
            isBot = False
        else:
            table = "teststudent_message_log"

        result = getMessageCSV(table, isBot, guild)

        if result != -1:
            df = pd.DataFrame.from_dict(result)

            if not df.empty:
                df.drop(["id", "discord_username", 'server_id'], axis=1, inplace=True)
                df.rename(columns={'discord_id': 'Username'}, inplace=True)
                usernames = df.Username.unique()
                for i in range(len(usernames)):
                    member = await ctx.bot.fetch_user(usernames[i])
                    name = member.display_name
                    to_replace = usernames[i]
                    df.replace(to_replace, name, inplace=True)

            if isBot:
                df.drop(["last_message_date"], axis=1, inplace=True)
                file_path = r"src/csv/TestMessage_Stats.csv"
                df.to_csv(file_path, index=False)

            else:  # pragma: no cover
                file_path = r"../src/csv/Message_Stats.csv"
                df.to_csv(file_path, index=False)
                await ctx.author.send(file=discord.File(file_path))

            await ctx.send("Message Stats file sent.")

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
        addReaction(table, info, isBot)

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

        removeReaction(table, val, isBot)

    @commands.Cog.listener("on_message")
    @commands.cooldown(1, 2)
    async def on_messageSQL(self, message):
        if message.author == self.bot.user or not message.guild:
            return
        userID = message.author.id
        username = str(self.bot.get_user(userID))
        curr_date = datetime.now().strftime('%Y-%m-%d')
        serverID = message.guild.id
        if len(message.content) > 20:
            biggerthan20 = 1
        else:
            biggerthan20 = 0
        val = (userID, username, curr_date, biggerthan20, serverID)
        isBot = True
        if not message.author.bot:
            table = "student_message_log"
            isBot = False
        else:
            table = "teststudent_message_log"

        if isBot and (message.content == "Message added test"):
            code = AddMessageCount(table, val, isBot)
            if code == 1:
                await message.channel.send('Message Added')
        else:
            code = AddMessageCount(table, val, isBot)


def setup(bot):
    bot.add_cog(SQLCog(bot))