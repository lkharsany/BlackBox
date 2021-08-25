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


def getLecturerQuestionsID(username):
    try:
        Db = TravisDBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = """SELECT * FROM TestLecturerQuestions WHERE asked_by = %s"""
        cur.execute(Q, (username,))

        result = cur.fetchone()
        if result:
            return result["question_id"]
        else:
            return -99
    except Exception as e:
        print(e)
        return -99


TESTER = os.getenv('Tester')
test_collector = TestCollector()
created_channel = None


@test_collector()
async def test_messageStats(interface):
    await interface.send_message("Message added test")
    await interface.get_delayed_reply(1, interface.assert_message_equals, "Message Added")
    await interface.send_message("./MessageStats")
    await asyncio.sleep(2)
    with open('src/csv/MStatsComparison.csv', 'r') as t1, open('src/csv/TestMessage_Stats.csv', 'r') as t2:
        fileone = t1.readlines()
        filetwo = t2.readlines()

    isSame = True
    sizeOne = len(fileone)
    sizeTwo = len(filetwo)

    if sizeOne == sizeTwo:
        for i, j in zip(range(sizeOne), range(sizeTwo)):
            if fileone[i] != filetwo[j]:
                isSame = False
                print("unequal")
                print(fileone[i])
                print(filetwo[i])
    else:
        isSame = False
        print("uneven!")
        print(fileone)
        print(filetwo)

    if isSame:
        await interface.get_delayed_reply(2, interface.assert_message_equals, "Message Stats file sent.")
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


@test_collector()
async def test_reactionStats(interface):
    await interface.send_message("./ReactionStats")
    await asyncio.sleep(2)
    with open('src/csv/RStatsComparison.csv', 'r') as t1, open('src/csv/TestReactions_Stats.csv', 'r') as t2:
        fileOne = t1.readlines()
        fileTwo = t2.readlines()

        isSame = True
        sizeOne = len(fileOne)
        sizeTwo = len(fileTwo)

        if sizeOne == sizeTwo:
            for i, j in zip(range(sizeOne), range(sizeTwo)):
                if fileOne[i] != fileTwo[j]:
                    isSame = False
                    print(fileOne[i])
                    print(fileTwo[j])
        else:
            isSame = False
            print("Uneven")
            print(fileOne)
            print(fileTwo)

        if isSame:
            await interface.get_delayed_reply(5, interface.assert_message_equals, "Reactions Stats file sent.")
        else:
            await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


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


@test_collector()
async def test_refer(interface):
    Username = 829768047350251530
    await interface.send_message("./Ask Is this a test question?")
    new_ID = getQuestionsID(Username)
    if new_ID != -99:
        if new_ID != -99:
            x = await interface.get_delayed_reply(2, interface.assert_message_equals, 'Question Added')
            if x:
                message = await interface.send_message(f"./Refer {new_ID}")
                await interface.get_delayed_reply(2, interface.assert_message_equals, "Message Sent to Lecturer")
        else:
            await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


@test_collector()
async def test_questionStats(interface):
    await interface.send_message("./QuestionStats")

    with open('src/csv/QStatsComparison.csv', 'r') as t1, open('src/csv/TestQuestion_Stats.csv', 'r') as t2:
        fileOne = t1.readlines()
        fileTwo = t2.readlines()

        isSame = True
        sizeOne = len(fileOne)
        sizeTwo = len(fileTwo)

        if sizeOne == sizeTwo:
            for i, j in zip(range(sizeOne), range(sizeTwo)):
                if fileOne[i] != fileTwo[j]:
                    isSame = False
                    print(fileOne[i])
                    print(fileTwo[j])
        else:
            isSame = False

        if isSame:
            print("HERE")
            await interface.get_delayed_reply(5, interface.assert_message_equals, "Question Stats file sent.")
        else:
            await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


@test_collector()
async def test_lecturer(interface):
    Username = 829768047350251530
    new_ID = getLecturerQuestionsID(Username)
    if new_ID != -99:
        if new_ID != -99:
            message = await interface.send_message(f"./Lecturer {new_ID}")
            y = await interface.get_delayed_reply(2, interface.assert_message_equals,
                                                  f"What's the answer? Begin with the phrase \"answer: \"")
            if y:
                message = await interface.send_message("answer: yes, yes it is")
                await interface.get_delayed_reply(2, interface.assert_message_equals, "Question has been Answered")
        else:
            await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


@test_collector()
async def test_faq(interface):
    await interface.send_message("./FAQ")
    await interface.get_delayed_reply(2, interface.assert_message_equals, "FAQ Channel Created")


@test_collector()
async def test_delfaq(interface):
    await interface.send_message("./DELFAQ")
    await interface.get_delayed_reply(2, interface.assert_message_equals, "FAQ Channel Deleted")


# Actually run the bot
if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
