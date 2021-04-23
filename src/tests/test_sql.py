import os
import sys

import pymysql.cursors
from distest import TestCollector
from distest import run_dtest_bot
from sshtunnel import SSHTunnelForwarder


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


def addQuestion(user, ques):
    val = (user, ques)
    try:
        Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = """INSERT INTO TestDiscordQuestions (username, question) Values (%s,%s)"""
        affected = cur.execute(Q, val)
        conn.commit()
        Db.close()
        return affected
    except Exception as e:
        print(e)

    return -99


def removeQuestionByID(ID):
    try:
        Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = """DELETE FROM TestDiscordQuestions WHERE id= %s """
        affected = cur.execute(Q, (ID,))
        conn.commit()
        Db.close()
        return affected
    except Exception as e:
        print(e)
    return -99


def removeAllBotQuestions(username):
    try:
        Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = """DELETE FROM DiscordQuestions WHERE username = %s """
        affected = cur.execute(Q, (username,))
        conn.commit()
        Db.close()
        return affected
    except Exception as e:
        print(e)
    return -99


def getQuestionsID(username):
    try:
        Db = DBConnect()
        conn = Db.open()
        cur = conn.cursor()
        Q = """SELECT * FROM DiscordQuestions WHERE username = %s"""
        cur.execute(Q, (username,))
        result = cur.fetchone()
        return result["id"]
    except Exception as e:
        print(e)


TESTER = os.getenv('Tester')
test_collector = TestCollector()
created_channel = None


@test_collector()
async def test_ask(interface):
    await interface.send_message(
        "./Ask Is this a test question?"
    )
    Username = 829768047350251530
    Question = "Is this a test question?"
    affected = addQuestion(Username, Question)
    if affected == 1:
        await interface.get_delayed_reply(3, interface.assert_message_equals, 'Question Added')
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


async def test_who(interface):
    await interface.send_message("./Who")
    Username = 829768047350251530
    ID = getQuestionsID(Username)
    await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


@test_collector()
async def test_answered(interface):
    Username = 829768047350251530
    ID = str(getQuestionsID(Username))
    await interface.send_message("./Answered " + ID)
    affected = removeQuestionByID(ID)
    if affected == 1:
        await interface.get_delayed_reply(2, interface.assert_message_equals, 'Question Removed')
    else:
        await interface.get_delayed_reply(1, interface.assert_message_equals, 'Fail')


# Actually run the bot
if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
