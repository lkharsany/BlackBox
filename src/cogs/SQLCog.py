import pymysql.cursors
from sshtunnel import SSHTunnelForwarder
from discord.ext import commands
import os
from discord import Embed
from datetime import datetime

AskBrief = "Usage: Ask <question>\nAdds Question to the Database"
answeredBrief = "Usage: Answered <question id>\nRemoves Answered Question from Database"
WhoDesc = "Displays all Questions, Users and ID as an Embeded Message\n Only Users with  Allocated Roles Can Access " \
          "This Command "
AnsweredDesc = "Removes Answered Question from Database\n Only Users with Allocated Roles Can Access This Command"


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
    try:
        # tries to insert values into table.
        if isBot:
            Db = TravisDBConnect()
        else:
            Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (username, question, question_date, question_time) Values (%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        return 1
    except pymysql.err as err:
        print(err)
        return -1


def queryQuestions(table, isBot):
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


def getQuestionRow(table, ID, isBot):
    try:
        if isBot:
            Db = TravisDBConnect()
        else:
            Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""SELECT * FROM {table} WHERE id = %s"""
        cur.execute(Q, (ID,))

        result = cur.fetchone()
        if result:
            return result
        else:
            return -1
    except Exception as e:
        print(e)
        return -1


def addAnswer(table, val, isBot):
    try:
        if isBot:
            Db = TravisDBConnect()
        else:
            Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (asked_by, question, question_date, question_time, answered_by, answer, answer_date, answer_time) Values (%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        return 1
    except pymysql.err as err:
        print(err)
        return -1


def delQuestion(table, ID, isBot):
    try:
        if isBot:
            Db = TravisDBConnect()
        else:
            Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""DELETE FROM {table} WHERE id = %s """
        cur.execute(Q, (ID,))
        conn.commit()
        Db.close()
        return 1
    except pymysql.err as err:
        print(err)
        return -1


def createEmbed(member, question, asked_date, asked_time, ID):
    embed = Embed(color=0xff9999, title="", description=member.mention)
    embed.set_author(name=member.name, url=Embed.Empty, icon_url=member.avatar_url)
    embed.add_field(name="Question Asked", value=question)
    embed.add_field(name="Asked On", value=str(asked_date) + "\n" + str(asked_time) + "\n")
    embed.set_footer(text=f"Question ID:  {str(ID)}")
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
                    embed = createEmbed(member, question, asked_date, asked_time, ID)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("No Open Questions. Nice!")

    # Answered command
    #@commands.command(brief=answeredBrief, description=AnsweredDesc, usage="<question id>", name='Answered')
    #@commands.cooldown(1, 2)
    # @commands.has_role("")
    async def Del(self, ctx, *, message):
        ID = message
        # used to "override" the table that the question is added to for testing purposes
        if not ctx.message.author.bot:
            if ID.isdigit():
                ID = int(ID)
                try:
                    Db = DBConnect()
                    conn = Db.open()
                    cur = conn.cursor()
                    Q = f"""DELETE FROM DiscordQuestions WHERE id = %s """
                    cur.execute(Q, (ID,))
                    conn.commit()
                    Db.close()
                    await ctx.send('Question Removed')
                except pymysql.err as err:
                    print(err)

            else:
                await ctx.send("Not a Valid Answered ID")
        else:
            if ID.isdigit():
                ID = int(ID)
                try:
                    Db = TravisDBConnect()
                    conn = Db.open()
                    cur = conn.cursor()
                    Q = f"""DELETE FROM TestDiscordQuestions WHERE id = %s """
                    cur.execute(Q, (ID,))
                    conn.commit()
                    Db.close()
                    await ctx.send('Question Removed')
                except pymysql.err as err:
                    print(err)

            else:
                await ctx.send("Not a Valid Answered ID")

    @commands.command(name='Answer')
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
                ask_by = int(result["username"])
                question = result["question"]
                asked_date = result["question_date"]
                asked_time = result["question_time"]

                member = await ctx.bot.fetch_user(ask_by)
                embed = createEmbed(member, question, asked_date, asked_time, ID)

                await ctx.send(embed=embed)
                await ctx.send(f"What's the answer? Begin with the phrase \"answer: \"")

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author and "answer" in m.content.lower()

                msg = await self.bot.wait_for("message", check=check)
                ans_by = int(msg.author.id)
                answer = msg.content.split(" ", 1)[1]
                curr_date = datetime.now().strftime('%Y-%m-%d')
                curr_time = datetime.now().strftime('%H:%M:%S')

                val = (ask_by, question, asked_date, asked_time, ans_by, answer, curr_date, curr_time)
                code = addAnswer(ansTable, val, isBot)
                if code == 1:
                    delCode = delQuestion(qTable, ID, isBot)
                    if delCode == 1:
                        await ctx.send("Question has been Answered")
        else:
            await ctx.send("Not a Valid Answered ID")


def setup(bot):
    bot.add_cog(SQLCog(bot))
