import pymysql.cursors
from sshtunnel import SSHTunnelForwarder
from discord.ext import commands
import os
from discord import Embed
import time
from datetime import datetime


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


class SQLCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Commands to Add, Display and Remove Questions from a Database"

    # Ask command
    @commands.command(brief="Usage: Ask <question>\nAdds Question to the Database",
                      description="Adds Question to the Database",
                      usage="<question>",
                      name='Ask')
    @commands.cooldown(1, 2)
    async def Ask(self, ctx, *, message):
        user = ctx.message.author.id
        val = (user, message)
        # used to "override" the table that the question is added to for testing purposes
        if not ctx.message.author.bot:
            try:
                # tries to insert values into table.
                Db = DBConnect()
                conn = Db.open()
                cur = conn.cursor()
                Q = f"""INSERT INTO DiscordQuestions (username, question) Values (%s,%s)"""
                cur.execute(Q, val)
                conn.commit()
                await ctx.send('Question Added')
            except pymysql.err as err:
                print(err)

        else:
            try:
                # tries to insert values into table.
                Db = TravisDBConnect()
                conn = Db.open()
                cur = conn.cursor()
                Q = f"""INSERT INTO TestDiscordQuestions (username, question) Values (%s,%s)"""
                cur.execute(Q, val)
                conn.commit()
                await ctx.send('Question Added')
            except pymysql.err as err:
                print(err)

    # Who command
    @commands.command(brief="Displays All Questions",
                      description="Displays all Questions, Users and ID as an Embeded Message\n Only Users with "
                                  "Allocated Roles Can Access This Command",
                      name='Who')
    @commands.cooldown(1, 2)
    # @commands.has_role("")
    async def Who(self, ctx, *, message=None):
        # used to "override" the table that the question is added to for testing purposes
        if not ctx.author.bot:
            try:
                Db = DBConnect()
                conn = Db.open()
                cur = conn.cursor()
                Q = f"""Select * FROM DiscordQuestions"""
                cur.execute(Q)
                result = cur.fetchall()
                if len(result) > 0:
                    for r in result:
                        ID = r['id']
                        user_id = int(r["username"])
                        question = r["question"]
                        member = await ctx.bot.fetch_user(user_id)
                        embed = Embed(color=0xff9999, title="", description=member.mention)
                        embed.set_author(name=member.name, url=Embed.Empty, icon_url=member.avatar_url)
                        embed.add_field(name="Question Asked", value=question)
                        embed.set_footer(text=f"Question ID:  {str(ID)}")
                        await ctx.send(embed=embed)
                else:
                    await ctx.send("No Open Questions. Nice!")
            except pymysql.err as err:
                print(err)

        else:
            try:
                Db = TravisDBConnect()
                conn = Db.open()
                cur = conn.cursor()
                Q = f"""Select * FROM TestDiscordQuestions"""
                cur.execute(Q)
                result = cur.fetchall()
                if len(result) > 0:
                    for r in result:
                        ID = r['id']
                        user_id = int(r["username"])
                        question = r["question"]
                        member = await ctx.bot.fetch_user(user_id)
                        embed = Embed(color=0xff9999, title="", description=member.mention)
                        embed.set_author(name=member.name, url=Embed.Empty, icon_url=member.avatar_url)
                        embed.add_field(name="Question Asked", value=question)
                        embed.set_footer(text=f"Question ID:  {str(ID)}")
                        await ctx.send(embed=embed)
            except pymysql.err as err:
                print(err)




    # Answered command
    @commands.command(brief="Usage: Answered <question id>\nRemoves Answered Question from Database",
                      description="Removes Answered Question from Database\n Only Users with Allocated Roles Can "
                                  "Access This Command",
                      usage="<question id>",
                      name='Answered')
    @commands.cooldown(1, 2)
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
                    Q = f"""DELETE FROM "DiscordQuestions" WHERE id = %s """
                    cur.execute(Q, (ID,))
                    conn.commit()
                    Db.close()
                except pymysql.err as err:
                    print(err)
                await ctx.send('Question Removed')
            else:
                await ctx.send("Not a Valid Answered ID")
        else:
            if ID.isdigit():
                ID = int(ID)
                try:
                    Db = TravisDBConnect()
                    conn = Db.open()
                    cur = conn.cursor()
                    Q = f"""DELETE FROM "TestDiscordQuestions" WHERE id = %s """
                    cur.execute(Q, (ID,))
                    conn.commit()
                    Db.close()
                except pymysql.err as err:
                    print(err)
                await ctx.send('Question Removed')
            else:
                await ctx.send("Not a Valid Answered ID")


def setup(bot):
    bot.add_cog(SQLCog(bot))
