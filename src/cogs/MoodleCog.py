import asyncio

import discord.embeds
from discord.ext import commands, tasks
from datetime import datetime
import pymysql.cursors
import os
from sshtunnel import SSHTunnelForwarder
from dateutil.parser import parse
from discord.utils import get, find

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


def QueryDatesCommand(table, Server_id, days,isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} WHERE server_id =%s AND due_date <= DATE_ADD(CURDATE(), INTERVAL {days} DAY);"""
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

def QueryDates(table, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} WHERE  due_date <= DATE_ADD(CURDATE(), INTERVAL 3 DAY);"""
        cur.execute(Q, )
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


def createDueEmbed(item, date, member):
    remaining = (date - datetime.now())
    embed = discord.Embed(color=0xff9999, title=item + " Due", description="")
    embed.add_field(name="Date", value=date.date().strftime("%d/%m/%Y"), inline=False)
    if date.hour != 0:
        embed.add_field(name="Time", value=date.time(), inline=False)
    m, s = divmod(remaining.seconds, 60)
    h, m = divmod(m, 60)
    d = remaining.days

    days = "day" if d == 1 else "days"
    hours = "hour" if h == 1 else "hours"
    minutes = "minute" if m == 1 else "minutes"

    timeLeft = f"{d} {days}, {h} {hours}, {m} {minutes}"
    embed.add_field(name='Time Left', value=timeLeft)
    embed.set_footer(text=f"Created By:  {member.name}")
    return embed


def CleanUp(table, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Delete from {table} WHERE due_date<NOW()"""
        # Q = f"""Select id FROM {table} WHERE server_id =%s AND due_date <= DATE_ADD(CURDATE(), INTERVAL 3 DAY);"""
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

    async def CleanChannel(self):
        channel_name = "reminders"
        for guild in self.bot.guilds:
            channel = get(guild.text_channels, name=channel_name)
            if channel is not None:
                oldMessages = await channel.history(limit=200).flatten()
                for msg in oldMessages:
                    await msg.delete()

    @tasks.loop(seconds=30)
    async def checkDates(self):
        channel_name = "reminders"
        CleanUp("DueDates", isBot=False)
        allDates = QueryDates("DueDates", isBot=False)
        await self.CleanChannel()
        for i in allDates:
            print(i)
            item = i['item_due']
            date = i["due_date"]
            server_id = int(i["server_id"])
            member = await self.bot.fetch_user(i['created_by'])
            guild = self.bot.get_guild(server_id)
            channel = get(guild.text_channels, name=channel_name)
            embed = createDueEmbed(item, date, member)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        channel_name = "reminders"
        for guild in self.bot.guilds:
            channel = get(guild.text_channels, name=channel_name)
            if channel is None:
                await guild.create_text_channel(channel_name)

        self.checkDates.start()

    @commands.command(name='Upcoming', brief="", description="See What's Due")
    @commands.cooldown(1, 2)
    async def Upcoming(self, ctx,  amount=3):
        Upcoming = QueryDatesCommand("DueDates", ctx.guild.id, amount,isBot=False)
        for i in Upcoming:
            item = i['item_due']
            date = i["due_date"]
            member = await ctx.bot.fetch_user(i['created_by'])
            embed = createDueEmbed(item, date, member)
            await ctx.send(embed=embed)

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
