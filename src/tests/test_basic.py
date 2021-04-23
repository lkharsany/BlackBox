import sys
from distest import TestCollector
from distest import run_dtest_bot
from time import sleep
import os
from sshtunnel import SSHTunnelForwarder
import pymysql.cursors



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
    Db = DBConnect()
    conn = Db.open()
    cur = conn.cursor()
    Q = """INSERT INTO DiscordQuestions (username, question) Values (%s,%s)"""
    affected = cur.execute(Q, val)
    conn.commit()
    Db.close()
    return affected

TESTER = os.getenv('Tester')
# The tests themselves

test_collector = TestCollector()
created_channel = None


@test_collector()
async def test_scrum(interface):
    sleep(1)
    await interface.assert_reply_equals("./Scrum", "Master")


@test_collector()
async def test_cool(interface):
    sleep(1)
    await interface.assert_reply_equals("./CoolBot", "This bot is cool. :)")


@test_collector()
async def test_ping(interface):
    sleep(1)
    await interface.assert_reply_contains("ping", "Pong!")


@test_collector()
async def test_cheers(interface):
    sleep(1)
    await interface.assert_reply_contains("hi", "Hello there")



async def test_ask(interface):
    message = await interface.send_message(
        "./Ask Is this a test question?"
    )
    Username = 829768047350251530
    Question = "Is this a test question?"
    print(addQuestion(Username,Question))
    await interface.get_delayed_reply(2, interface.assert_message_equals, 'Question Added')



# Actually run the bot

if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
