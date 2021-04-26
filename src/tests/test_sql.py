import os
import sys

import pymysql.cursors
from distest import TestCollector
from distest import run_dtest_bot
from sshtunnel import SSHTunnelForwarder
from discord import Embed
import asyncio


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


def getQuestionsID(username):
    try:
        Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = """SELECT * FROM TestDiscordQuestions WHERE username = %s"""
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
async def test_ask(interface):
    await interface.send_message(
        "./Ask TestDiscordQuestions$!Is this a test question?"
    )
    user_id = 829768047350251530
    await asyncio.sleep(3)
    ID = getQuestionsID(user_id)
    if ID != -99:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'Question Added')
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


@test_collector()
async def test_who(interface):
    message = await interface.send_message("Testing Query")
    user_id = 829768047350251530
    Question = "Is this a test question?"
    member = message.author
    ID = getQuestionsID(user_id)

    attributeList = ["author"]

    Member_url = " https://discordapp.com/users/" + str(user_id)
    embed = Embed(color=0xff9999, title="", description="")
    embed.set_author(name=member.name, url=Member_url, icon_url=member.avatar_url)
    embed.add_field(name="Question Asked", value=Question)
    embed.set_footer(text=f"Question ID:  {str(ID)}")

    check = """Use The "./Answered" Command Followed by the Question ID to Delete Answered Questions"""
    if await interface.assert_reply_equals("./Who TestDiscordQuestions", check):
        try:
            await interface.assert_reply_embed_equals("Check Embed", embed, attributeList)
            # await interface.assert_reply_embed_equals("Testing Embed", embed, attributeList)
        except Exception as e:
            print(e)
        # await interface.get_delayed_reply(1, interface.assert_reply_embed_equals, embed,"")


@test_collector()
async def test_answered(interface):
    Username = 829768047350251530
    ID = getQuestionsID(Username)
    await interface.send_message("./Answered " + "TestDiscordQuestions$!" + str(ID))
    await asyncio.sleep(3)
    new_ID = getQuestionsID(Username)
    if new_ID == -99:
        await interface.get_delayed_reply(2, interface.assert_message_equals, 'Question Removed')
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


# Actually run the bot
if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
