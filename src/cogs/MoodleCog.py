import asyncio

from discord.ext import commands, tasks
from datetime import datetime
import pymysql.cursors
import os
from sshtunnel import SSHTunnelForwarder
from dateutil.parser import parse

isSSH = os.getenv('using_SSH')
if isSSH.lower() == "true":  # pragma: no cover
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
else:  # pragma: no cover
    class DBConnect:  # pragma: no cover
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
            self.Connection.close()  # pragma: no cover


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


def AddReminder(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT INTO {table} (server_id, due_date, item_due, created_by) Values (%s,%s,%s,%s)"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1

    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def QueryDates(table, Server_id, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select id FROM {table} WHERE server_id =%s AND due_date <= DATE_ADD(CURDATE(), INTERVAL 3 DAY);"""
        cur.execute(Q, (Server_id,))
        result = cur.fetchall()
        Db.close()
        if result:
            return result
        else:
            return -1
    except Exception as e:  # pragma: no cover
        print(e)
        Db.close()
        return -1

def CleanUp(table, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q=f"""Delete from {table} WHERE due_date<NOW()"""
        #Q = f"""Select id FROM {table} WHERE server_id =%s AND due_date <= DATE_ADD(CURDATE(), INTERVAL 3 DAY);"""
        cur.execute(Q, )
        conn.commit()
        Db.close()
        return 1

    except Exception as e:  # pragma: no cover
        print(e)
        Db.close()
        return -1


class MoodleCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Moodle Integration Commands"
        self.Item_IDs = []

    @tasks.loop(seconds=10)
    async def checkDates(self):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        await self.checkDates()

    @commands.command(name='Que', brief="", description="Add an item that's due")
    @commands.cooldown(1, 2)
    async def que(self, ctx):
        CleanUp("DueDates", isBot=False)
        self.Item_IDs.clear()
        arr = QueryDates("DueDates", ctx.guild.id, isBot=False)
        for i in arr:
            self.Item_IDs.append(i["id"])
        print(self.Item_IDs)


    @commands.command(name='Due', brief="", description="Add an item that's due")
    @commands.cooldown(1, 2)
    async def add_due(self, ctx, *, message):
        item = message
        created_by = ctx.author.id
        server_id = ctx.guild.id
        await ctx.send("When is it due? (DD/MM/YYYY HH:MM:SS) \n NB: Time is optional")

        def check(m):
            if m.author == ctx.author:
                try:
                    x = parse(m.content, dayfirst=True)
                    return isinstance(x, datetime) and x >= datetime.now()
                except ValueError:
                    return False
                # send error message if not in correct format

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20)
            if message is not None:
                due_date = parse(msg.content, dayfirst=True).strftime("%Y-%m-%d %H:%M:%S")
                val = (server_id, due_date, item, created_by)

                isBot = True

                if not ctx.author.bot:
                    table = "DueDates"
                    isBot = False
                else:
                    table = "TestDueDates"

                code = AddReminder(table, val, isBot)
                if code == 1:
                    await ctx.send("Due date has been added")
                else:
                    await ctx.send("An error occurred, please try again")

        except asyncio.TimeoutError:
            await ctx.send("Item not added. Please ensure you use the correct format and try again")


def setup(bot):
    bot.add_cog(MoodleCog(bot))
