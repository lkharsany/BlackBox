import os
from datetime import datetime
import pymysql.cursors
import discord
from discord.ext import commands
from discord.utils import get, find
from sshtunnel import SSHTunnelForwarder
import pandas as pd

isSSH = os.getenv('using_SSH')
if isSSH.lower() == "true": # pragma: no cover
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
else: # pragma: no cover
    class DBConnect: # pragma: no cover
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
            self.Connection.close() # pragma: no cover


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


class ThreadCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Commands to Add, Display and Remove Questions from a Database"

    # Ask command
    @commands.command(name='Thread', usage="<question>", aliases=["thread"])
    @commands.cooldown(1, 2)
    async def Thread(self, ctx, *, message):
        pass