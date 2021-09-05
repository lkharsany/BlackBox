import asyncio

import discord.embeds
from discord.ext import commands, tasks
from datetime import datetime
import pymysql.cursors
import os
from sshtunnel import SSHTunnelForwarder
from dateutil.parser import parse
from discord.utils import get

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


# adds the reminder data to the DueDates table
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


# Returns all items whose due dates are within the users given interval period from the current date
def QueryDatesCommand(table, Server_id, days, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} WHERE server_id =%s AND due_date <= DATE_ADD(CURDATE(), INTERVAL {days} DAY) ORDER BY due_date DESC;"""
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


# Returns all the items in the database whose due dates are 3 days away from the current date
def QueryDates(table, isBot): # pragma: no cover
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} ORDER BY due_date DESC """
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


# Creates an embed to display the reminders
def createDueEmbed(item, date, member, isBot):
    remaining = (date - datetime.now())
    if not isBot:  # pragma: no cover
        embed = discord.Embed(color=0xff9999, title=item.capitalize() + " Due", description="")
        embed.add_field(name="Date", value=date.date().strftime("%d/%m/%Y"), inline=False)
        embed.add_field(name="Item", value=item, inline=False)
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
    else:
        embed = discord.Embed(color=0xff9999, title="", description=item.capitalize() + " Due")
        embed.set_author(name=member.name, url=discord.Embed.Empty, icon_url=member.avatar_url)
    return embed


# Deletes items from DueDates table
def CleanUp(table, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Delete from {table} WHERE due_date<NOW()"""
        cur.execute(Q, )
        conn.commit()
        Db.close()
        return 1

    except Exception as e:  # pragma: no cover
        print(e)
        Db.close()
        return -1


def GetDueDateRow(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} WHERE server_id =%s AND item_due=%s;"""
        cur.execute(Q, val)
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


def UpdateDueDate(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""UPDATE {table} SET due_date = %s WHERE id=%s"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1

    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


class MoodleCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Moodle Integration Commands"

    # clears the reminders channel of previous reminders so only most recent items due are visible
    async def CleanChannel(self): # pragma: no cover
        channel_name = "reminders"
        for guild in self.bot.guilds:
            channel = get(guild.text_channels, name=channel_name)
            if channel is not None:
                oldMessages = await channel.history(limit=200).flatten()
                for msg in oldMessages:
                    await msg.delete()

    # Runs the following code everyday
    # Deletes all items whose due dates have passed from the database
    # sends reminders in the form of a message for items which are due within 3 days of the current date
    # @tasks.loop(hours=24)
    @tasks.loop(minutes=1)
    async def checkDates(self): # pragma: no cover
        channel_name = "reminders"
        table = "DueDates"

        CleanUp(table, isBot=False)
        allDates = QueryDates(table, isBot=False)
        await self.CleanChannel()
        for i in allDates:
            item = i['item_due']
            date = i["due_date"]
            server_id = int(i["server_id"])
            member = await self.bot.fetch_user(i['created_by'])
            guild = self.bot.get_guild(server_id)
            channel = get(guild.text_channels, name=channel_name)
            embed = createDueEmbed(item, date, member, isBot=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self): # pragma: no cover
        is_travis = 'TRAVIS' in os.environ
        if not is_travis:
            channel_name = "reminders"
            for guild in self.bot.guilds:
                channel = get(guild.text_channels, name=channel_name)
                if channel is None:
                    await guild.create_text_channel(channel_name)
            self.checkDates.start()

    # Displays all upcoming assignments due within the given time period the user specifies
    @commands.command(name='Upcoming', brief="", description="See What's Due", aliases=["upcoming", "upc"])
    @commands.cooldown(1, 2)
    async def Upcoming(self, ctx, amount=3):

        isBot = True
        if not ctx.author.bot:
            table = "DueDates"
            isBot = False
        else:
            table = "TestDueDates"

        Upcoming = QueryDatesCommand(table, ctx.guild.id, amount, isBot)
        if Upcoming != -1:
            for i in Upcoming:
                item = i['item_due']
                date = i["due_date"]
                member = await ctx.bot.fetch_user(i['created_by'])
                embed = createDueEmbed(item, date, member, isBot)
                await ctx.send(embed=embed)
        else:
            await ctx.send(f"Nothing Due Within {amount} Days")

    # Command for the user to set a reminder for when something is due and adds said reminder to the DueDates table
    @commands.command(name='Due', brief="", description="Add an item that's due")
    @commands.cooldown(1, 2)
    async def add_due(self, ctx, *, message):
        item = message
        created_by = ctx.author.id
        server_id = ctx.guild.id
        await ctx.send("When is it due? (DD/MM/YYYY HH:MM:SS) \n NB: Time is optional")

        # Checks if the date provided by the user is in the correct format
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

    @commands.command(name='Update', brief="", description="Update due dates", aliases=["update"])
    @commands.cooldown(1, 2)
    async def Update(self, ctx, *, message):
        item = message
        isBot = True

        if not ctx.author.bot:
            table = "DueDates"
            isBot = False
        else:
            table = "TestDueDates"
        server_id = ctx.guild.id
        val = (server_id, item)

        row = GetDueDateRow(table, val, isBot)
        if row != -1:
            member = await ctx.bot.fetch_user(row['created_by'])
            await ctx.send(embed=createDueEmbed(row["item_due"], row["due_date"], member, isBot))
            await ctx.send("Whats the new due date? (DD/MM/YYYY HH:MM:SS) \nNB: Time is optional")

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
                id_num = row["id"]
                if message is not None:
                    due_date = parse(msg.content, dayfirst=True).strftime("%Y-%m-%d %H:%M:%S")
                    val = (due_date, id_num)

                    isBot = True

                    if not ctx.author.bot:
                        table = "DueDates"
                        isBot = False
                    else:
                        table = "TestDueDates"

                    code = UpdateDueDate(table, val, isBot)
                    if code == 1:
                        await ctx.send("Due date has been updated")
                    else:
                        await ctx.send("An error occurred, please try again")

            except asyncio.TimeoutError:
                await ctx.send("Item not updated. Please ensure you use the correct format and try again")

        else:
            await ctx.send("No Such Item Exists")


def setup(bot):
    bot.add_cog(MoodleCog(bot))
