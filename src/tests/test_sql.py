import os
import sys

import pymysql.cursors
from distest import TestCollector
from distest import run_dtest_bot
from discord import Embed
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


def getQuestionsID(username):
    try:
        Db = TravisDBConnect()
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
    Username = 829768047350251530
    await interface.send_message("./Ask Is this a test question?")
    await asyncio.sleep(1)
    new_ID = getQuestionsID(Username)
    if new_ID != -99:
        await interface.get_delayed_reply(2, interface.assert_message_equals, 'Question Added')
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


@test_collector()
async def test_who(interface):
    message = await interface.send_message("Testing Query")
    user_id = 829768047350251530
    Question = "Is this a test question?"
    member = message.author
    ID = getQuestionsID(user_id)
    attributeList = ["author", "description"]

    embed = Embed(color=0xff9999, title="", description=member.mention)
    embed.set_author(name=member.name, url=Embed.Empty, icon_url=member.avatar_url)
    embed.add_field(name="Question Asked", value=Question)
    embed.set_footer(text=f"Question ID:  {ID}")

    await interface.assert_reply_embed_equals("./Who", embed, attributeList)


@test_collector()
async def test_answer(interface):
    Username = 829768047350251530
    Question = "Is this a test question?"
    ID = getQuestionsID(Username)
    message = await interface.send_message("Testing Answer")
    member = message.author

    attributeList = ["author", "description"]
    embed = Embed(color=0xff9999, title="", description=member.mention)
    embed.set_author(name=member.name, url=Embed.Empty, icon_url=member.avatar_url)
    embed.add_field(name="Question Asked", value=Question)
    embed.set_footer(text=f"Question ID:  {ID}")

    x = await interface.assert_reply_embed_equals(f"./Answer {ID}", embed, attributeList)
    if x:
        y = await interface.get_delayed_reply(2, interface.assert_message_equals,
                                              f"What's the answer? Begin with the phrase \"answer: \"")
        if y:
            message = await interface.send_message("answer: yes, yes it is")
            await interface.get_delayed_reply(2, interface.assert_message_equals, "Question has been Answered")



# Actually run the bot
if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
