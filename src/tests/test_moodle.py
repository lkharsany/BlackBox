import os
import sys
import pymysql.cursors
from distest import TestCollector
from distest import run_dtest_bot
from discord import Embed
from datetime import datetime, timedelta
import asyncio


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


def getRow(username):
    try:
        Db = TravisDBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = """SELECT * FROM TestDueDates WHERE created_by = %s"""
        cur.execute(Q, (username,))

        result = cur.fetchone()
        if result:
            return result["id"]
        else:
            return -99
    except Exception as e:
        print(e)
        return -99




TESTER = os.getenv('Tester')
test_collector = TestCollector()
created_channel = None



@test_collector()
async def test_due(interface):
    Username = 829768047350251530
    await interface.send_message("./Due testlab")
    await asyncio.sleep(1)

    y = await interface.get_delayed_reply(2, interface.assert_message_equals,
                                          "When is it due? (DD/MM/YYYY HH:MM:SS) \n NB: Time is optional")
    if y:
        date = (datetime.today()+timedelta(days=3)).strftime("%d/%m/%y")
        message = await interface.send_message(date)

    row = getRow(Username)
    if row != -99:
        await interface.get_delayed_reply(2, interface.assert_message_equals, 'Due date has been added')
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'An error occurred, please try again')


@test_collector()
async def test_upcoming(interface):
    message = await interface.send_message("Testing Upcoming")
    item = "testlab"
    member = message.author
    attributeList = ["author", "description"]
    embed = Embed(color=0xff9999, title="", description=item.capitalize() + " Due")
    embed.set_author(name=member.name, url=Embed.Empty, icon_url=member.avatar_url)
    await interface.assert_reply_embed_equals("./Upcoming 5", embed, attributeList)

@test_collector()
async def test_CourseDates(interface):
    message = await interface.send_message("./CourseDates")
    await interface.get_delayed_reply(2, interface.assert_message_equals, "Nothing Due")


@test_collector()
async def test_update(interface):
    Username = 829768047350251530
    message = await interface.send_message("./update testlab")
    y = await interface.get_delayed_reply(2, interface.assert_message_equals,
                                          "Whats the new due date? (DD/MM/YYYY HH:MM:SS) \nNB: Time is optional")
    if y:
        date = (datetime.today()+timedelta(days=5)).strftime("%d/%m/%y")
        message = await interface.send_message(date)
    row = getRow(Username)
    if row != -99:
        await interface.get_delayed_reply(2, interface.assert_message_equals, "Due date has been updated")
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'An error occurred, please try again')

@test_collector()
async def test_course(interface):
    ID = "188"
    Coordinator = "Branden Ingram"
    Shorthand = "COMS3010A"
    Name = "Operating Systems"
    message = await interface.send_message("Testing Course")
    attributeList = ["description"]
    embed = Embed(color=0xff9999, title=Name, description=Shorthand)
    embed.add_field(name="ID", value=ID, inline=False)
    embed.add_field(name="Course Coordinator", value=Coordinator, inline=False)
    await interface.assert_reply_embed_equals("./Course 188", embed, attributeList)

@test_collector()
async def test_linkServer(interface):
    Username = 829768047350251530
    await interface.send_message("./LinkServer 187")
    await asyncio.sleep(1)

    y = await interface.get_delayed_reply(2,interface.assert_message_equals,
                                          "Is this course\nCOMS2015A/COMS2021A - Analysis of Algorithms - 2021?\n Y/N")
    if y:
        message = await interface.send_message("Y")

    row = getRow(Username)
    if row != -99:
        await interface.get_delayed_reply(2, interface.assert_message_equals, 'Server and Course Linked Successfully')
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'An error occurred, please try again')



# Actually run the bot
if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
