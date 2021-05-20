import os
from datetime import datetime

import pymysql.cursors
from discord import Embed
from discord import PermissionOverwrite
from discord.ext import commands
from discord.utils import get
from sshtunnel import SSHTunnelForwarder

AskBrief = "Usage: Ask <question>\nAdds Question to the Database"
answeredBrief = "Usage: Answer <question id>\n Will then need to send your answer prefixed with  the \"answer:\" when prompted \nRemoves Answered Question from Database"
WhoDesc = "Displays all Questions, Users and ID as an Embeded Message\n Only Users with  Allocated Roles Can Access " \
          "This Command "
AnsweredDesc = "Removes Answered Question from Database and adds It to the answered Table \n Only Users with Allocated Roles Can Access This Command"

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
        Q = f"""INSERT INTO {table} (username, question, question_date, question_time) Values (%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def queryQuestions(table, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table}"""
        cur.execute(Q)
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
        Q = f"""INSERT INTO {table} (asked_by, question, question_date, question_time, answered_by, answer, answer_date, answer_time) Values (%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def delQuestion(table, ID, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
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
    embed = Embed(color=0xff9999, title="", description=member.mention)
    embed.set_author(name=member.name, url=Embed.Empty, icon_url=member.avatar_url)
    embed.add_field(name="Question Asked", value=question)
    embed.add_field(name="Asked On", value=str(asked_date) + "\n" + str(asked_time) + "\n")
    embed.set_footer(text=f"Question ID:  {str(ID)}")
    return embed


def queryAnswers(table, isBot):
    try:
        if isBot:
            Db = TravisDBConnect()
        else:
            Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table}"""
        cur.execute(Q)
        result = cur.fetchall()
        return result
    except pymysql.err as err:
        print(err)
        return -1


def createAnswerEmbed(ans_member, question, answer):
    embed = Embed(color=0xff9999, title="", description="")
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=answer, inline=False)
    # embed.add_field(name="Answered By", value=ans_member.mention,inline=False)
    embed.set_footer(text=f"Answered By: {ans_member.name}")
    return embed


class SQLCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Commands to Add, Display and Remove Questions from a Database"

    # Ask command
    @commands.command(brief=AskBrief, description="Adds Question to the Database", usage="<question>", name='Ask')
    @commands.cooldown(1, 2)
    async def Ask(self, ctx, *, message):
        user = ctx.message.author.id
        curr_date = datetime.now().strftime('%Y-%m-%d')
        curr_time = datetime.now().strftime('%H:%M:%S')
        val = (user, message, curr_date, curr_time)
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
        # used to "override" the table that the question is added to for testing purposes
        isBot = True
        if not ctx.author.bot:
            table = "DiscordQuestions"
            isBot = False
        else:
            table = "TestDiscordQuestions"
        result = queryQuestions(table, isBot)
        if result != -1:
            if len(result) > 0:
                for r in result:
                    ID = r['id']
                    user_id = int(r["username"])
                    question = r["question"]
                    asked_date = r["question_date"]
                    asked_time = r["question_time"]
                    member = await ctx.bot.fetch_user(user_id)
                    embed = createQuestionEmbed(member, question, asked_date, asked_time, ID)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("No Open Questions. Nice!")

    # Answer command
    @commands.cooldown(1, 2)
    @commands.command(brief=answeredBrief, description=AnsweredDesc, usage="<question id>", name='Answer')
    # @commands.has_role("")
    async def waitForReply(self, ctx, *, message):
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

                    val = (asked_by, question, asked_date, asked_time, ans_by, answer, curr_date, curr_time)
                    code = addAnswer(ansTable, val, isBot)
                    if code == 1:
                        delCode = delQuestion(qTable, ID, isBot)
                        if delCode == 1:
                            await ctx.send("Question has been Answered")

                            if not isBot:
                                await ctx.invoke(self.bot.get_command('FAQ'), isBot=isBot)
        else:
            await ctx.send("Not a Valid Answered ID")


    @commands.command(brief=FAQBrief, description=FAQBrief,name='FAQ')
    # @commands.has_role("")
    async def createChannel(self, ctx, *, isBot=True):
        guild = ctx.guild
        if not ctx.author.bot:
            table = "DiscordAnswers"
            isBot = False
            channel_name = "faq"
            overwrites = {
                guild.default_role: PermissionOverwrite(send_messages=False),
                guild.me: PermissionOverwrite(send_messages=True),
            }
        else:
            table = "TestDiscordAnswers"
            channel_name = "test faq"
            overwrites = {
                guild.default_role: PermissionOverwrite(send_messages=False),
                guild.me: PermissionOverwrite(send_messages=True),
                ctx.author: PermissionOverwrite(read_messages=True)
            }

        channel = get(guild.text_channels, name=channel_name)
        if channel:
            oldMessages = await channel.history(limit=200).flatten()
            for msg in oldMessages:
                await msg.delete()
        else:
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
            await ctx.send("FAQ Channel Created")
        result = queryAnswers(table, isBot)
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
                    await channel.send(embed=embed)
            else:
                await channel.send("Ask Some Stuff")


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


def setup(bot):
    bot.add_cog(SQLCog(bot))
