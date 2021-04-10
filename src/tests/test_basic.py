import sys
from distest import TestCollector
from distest import run_dtest_bot
from dotenv import load_dotenv
from time import sleep
import os

load_dotenv()

TESTER = os.getenv('Tester')
# The tests themselves

test_collector = TestCollector()
created_channel = None


@test_collector()
async def test_scrum(interface):
    sleep(1)
    await interface.assert_reply_contains("./Scrum", "Master")


@test_collector()
async def test_cool(interface):
    sleep(1)
    await interface.assert_reply_contains("./CoolBot", "This bot is cool. :)")


@test_collector()
async def test_ping(interface):
    sleep(1)
    await interface.assert_reply_contains("ping", "P;ong!")


@test_collector()
async def test_cheers(interface):
    sleep(1)
    await interface.assert_reply_contains("hi", "Hello there")

@test_collector()
async def test_shutdown(interface):
    sleep(1)
    await interface.assert_reply_equals("./bye", 'Shutting Down')


# Actually run the bot

if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
