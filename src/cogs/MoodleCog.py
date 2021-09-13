import asyncio
import discord.embeds
from discord.ext import commands, tasks
from datetime import datetime
import pymysql.cursors
import os
from sshtunnel import SSHTunnelForwarder
from dateutil.parser import parse
from discord.utils import get
from requests import post

# Module variables to connect to moodle api
KEY = os.getenv("moodle_key")

URL = os.getenv("moodle_url")
ENDPOINT = "/webservice/rest/server.php"


def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    """
    if out_dict == None:
        out_dict = {}
    if not type(in_args) in (list, dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args) == list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args) == dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict


def MoodleCall(fname, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments """
    parameters = rest_api_parameters(kwargs)
    parameters.update({"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})
    response = post(URL + ENDPOINT, parameters)
    response = response.json()
    if type(response) == dict and response.get('exception'):
        raise SystemError("Error calling Moodle API\n", response)
    return response


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
def QueryDates(table, isBot):  # pragma: no cover
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
        embed = discord.Embed(color=0xff9999, title=item.capitalize(), description="")
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


# redundant
def getMoodleCalenderMonth(y, m):
    function = "core_calendar_get_calendar_monthly_view"
    res = MoodleCall(function, year=y, month=m)
    return res


# redundant
def getMoodleDates(MonthDict, courseid):
    words = ["closes", "due", "close"]
    items = {}
    for w in range(len(MonthDict["weeks"])):
        weeks = MonthDict["weeks"][w]
        days = weeks["days"]
        for d in days:
            events = d["events"]
            has_events = d["hasevents"]
            if has_events:
                for i in events:
                    if i["course"]["id"] == courseid:
                        name = i["name"]
                        startTime = datetime.fromtimestamp(i["timestart"])
                        if any(word in name for word in words) and datetime.now() < startTime:
                            items[name] = startTime
    return items


def getMoodleUpcomingDates(ID):
    Dates = {}
    function = "core_calendar_get_calendar_upcoming_view"
    res = MoodleCall(function, courseid=ID)
    events = res["events"]
    for i in events:
        name = i["name"]
        due = datetime.fromtimestamp(i["timestart"])
        event_type = i["eventtype"]
        if event_type == "close":
            Dates[name] = due
    return Dates


def getMoodleCourses():
    function = "core_course_get_enrolled_courses_by_timeline_classification"
    # classification can be inprogress, past or future
    res = MoodleCall(function, classification="inprogress")
    for i in res["courses"]:
        print(i)


def getMoodleCourseByField(f, val):
    function = "core_course_get_courses_by_field"
    # fields = id or shortname
    # id = int and shortname=coursecode-acronym-year eg COMS3011A-SDP-2021
    res = MoodleCall(function, field=f, value=val)["courses"]
    if res:
        return res[0]


def mergeDict(x, y):
    if not x:
        return y
    elif not y:
        return x
    else:
        z = x.copy()
        z.update(y)
        return z


def allDueDates(courseID):
    DueDates = {}
    for i in range(1, 13):
        CalDict = getMoodleCalenderMonth(datetime.now().year, i)
        due = getMoodleDates(CalDict, courseID)
        if due:
            DueDates = mergeDict(DueDates, due)
    return DueDates


def createCourseEmbed(ID, Coordinator, Name, Shorthand, isBot):
    if not isBot:  # pragma: no cover
        embed = discord.Embed(color=0xff9999, title=Name, description=Shorthand)
        embed.add_field(name="ID", value=ID, inline=False)
        embed.add_field(name="Course Coordinator", value=Coordinator, inline=False)
    else:
        embed = discord.Embed(color=0xff9999, title=Name, description="")
        embed.add_field(name="ID", value=ID, inline=False)
        embed.add_field(name="Course Coordinator", value=Coordinator, inline=False)
    return embed


def addLinkServer(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""INSERT IGNORE INTO {table} (server_id, moodle_shorthand, moodle_id) Values (%s,%s,%s) ON DUPLICATE KEY UPDATE moodle_shorthand = %s, moodle_id=%s;"""
        cur.execute(Q, val)
        conn.commit()
        Db.close()
        return 1

    except pymysql.err as err:
        print(err)
        Db.close()
        return -1


def getServerLink(table, val, isBot):
    if isBot:
        Db = TravisDBConnect()
    else:  # pragma: no cover
        Db = DBConnect()
    try:
        conn = Db.open()
        cur = conn.cursor()
        Q = f"""Select * FROM {table} WHERE server_id =%s;"""
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


class MoodleCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Moodle Integration Commands"

    # clears the reminders channel of previous reminders so only most recent items due are visible
    async def CleanChannel(self):  # pragma: no cover
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
    async def checkDates(self):  # pragma: no cover
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

    @tasks.loop(minutes=1)
    async def checkMoodleDates(self):  # pragma: no cover
        channel_name = "reminders"
        await self.CleanChannel()
        for guild in self.bot.guilds:
            server = guild.id
            row = getServerLink("ServerLink", (server, ), False)
            if row != -1:
                course_id = row["moodle_id"]
                shortname = row["moodle_shorthand"]
                channel = get(guild.text_channels, name=channel_name)
                dates = getMoodleUpcomingDates(course_id)
                title_embed = discord.Embed(color=0xff9999, title=shortname, description="")
                await channel.send(embed=title_embed)
                if dates:
                    for k, v in dates.items():
                        embed = createDueEmbed(k, v, self.bot.user, False)
                        await channel.send(embed=embed)
                else:
                    await channel.send("Nothing Due")


    @commands.Cog.listener()
    async def on_ready(self):  # pragma: no cover
        is_travis = 'TRAVIS' in os.environ
        if not is_travis:
            channel_name = "reminders"
            for guild in self.bot.guilds:
                channel = get(guild.text_channels, name=channel_name)
                if channel is None:
                    await guild.create_text_channel(channel_name)
            self.checkMoodleDates.start()

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

    ##Update command to change due dates
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
            if not isBot:
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

    @commands.command(name='Course', brief="", description="", aliases=["course"])
    @commands.cooldown(1, 2)
    async def MoodleGetCourseCommand(self, ctx, *, msg):  # pragma: no cover
        if msg.isdigit():
            course = getMoodleCourseByField("id", int(msg))
        else:
            course = getMoodleCourseByField("shortname", msg.upper())
        if course is not None:
            c_id = str(course["id"])
            idLong = course["displayname"].split("-")
            name = idLong[1]
            shorthand = idLong[0]
            Coordinator = course["contacts"][0]["fullname"]
            embed = createCourseEmbed(c_id, Coordinator, name, shorthand, False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Course Not Found")

    @commands.command(name='CourseDates', brief="", description="", aliases=["coursedates"])
    @commands.cooldown(1, 2)
    async def MoodleGetDueDates(self, ctx, *, msg=None):  # pragma: no cover
        if msg is None:
            server_id = ctx.guild.id
            val = (server_id,)
            isBot = True
            if not ctx.author.bot:
                table = "ServerLink"
                isBot = False
            else:
                table = "TestServerLink"
            row = getServerLink(table, val, isBot)
            if row != -1:
                course_id = row["moodle_id"]
            else:
                await ctx.send("Could Not Find Course\nConsider Linking Course With This Server Using the LinkServer Command")
                return

        elif msg.isdigit():
            course_id = int(msg)
            course = getMoodleCourseByField("id", course_id)
            if not course:
                await ctx.send("Could Not Find Course")
                return

        else:
            course = getMoodleCourseByField("shortname", msg.upper())
            if course is not None:
                course_id = int(course["id"])
            else:
                await ctx.send("Could Not Find Course")
                return

        dates = getMoodleUpcomingDates(course_id)
        if dates:
            for k, v in dates.items():
                embed = createDueEmbed(k, v, ctx.author, False)
                await ctx.send(embed=embed)
        else:
            await ctx.send("Nothing Due")

    @commands.command(name='LinkServer', brief="", description="", aliases=["linkserver"])
    @commands.cooldown(1, 2)
    async def ServerLink(self, ctx, *, msg):
        server_id = ctx.guild.id
        if msg.isdigit():
            course_id = int(msg)
            course = getMoodleCourseByField("id", course_id)
            if course is not None:
                shortname = course["shortname"]
                name = course["displayname"]
            else:
                await ctx.send("Course Not Found")
                return

        else:
            shortname = msg
            course = getMoodleCourseByField("shortname", shortname)
            if course is not None:
                course_id = course["id"]
                name = course["displayname"]
            else:
                await ctx.send("Course Not Found")
                return

        def check(m):
            return m.author == ctx.author and m.content.lower() == "y"

        await ctx.send(f"Is this course\n{name}?\n Y/N")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20)
            if msg is not None:
                val = (server_id, shortname, course_id,shortname, course_id)
                isBot = True
                if not ctx.author.bot:
                    table = "ServerLink"
                    isBot = False
                else:
                    table = "TestServerLink"
                code = addLinkServer(table, val, isBot)
                if code != -1:
                    await ctx.send("Server and Course Linked Successfully")
                else:
                    await ctx.send("An Error Occured. Please Try Again")

        except asyncio.TimeoutError:
            await ctx.send("Timeout Error. Please Try Again")

def setup(bot):
    bot.add_cog(MoodleCog(bot))
