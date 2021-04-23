import sys
from distest import TestCollector
from distest import run_dtest_bot
from time import sleep
import os
from sshtunnel import SSHTunnelForwarder
import pymysql.cursors



TESTER = os.getenv('Tester')
# The tests themselves

test_collector = TestCollector()
created_channel = None


@test_collector()
async def test_scrum(interface):
    await interface.send_message("./Scrum")
    await interface.get_delayed_reply(2, interface.assert_message_equals, 'Master')


@test_collector()
async def test_cool(interface):
    await interface.send_message("./CoolBot")
    await interface.get_delayed_reply(1, interface.assert_message_equals, 'This bot is cool. :)')


@test_collector()
async def test_ping(interface):
    await interface.send_message("ping")
    await interface.get_delayed_reply(1, interface.assert_message_equals, "Pong!")


@test_collector()
async def test_cheers(interface):
    await interface.send_message("hi")
    await interface.get_delayed_reply(1, interface.assert_message_equals, "Hello there")


# Actually run the bot

if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
