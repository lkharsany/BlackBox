import pymysql.cursors
from sshtunnel import SSHTunnelForwarder
from discord.ext import commands
import os

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


class SQLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='Ask')
    @commands.cooldown(1, 2)
    async def Ask(self, ctx, *, message):
        user = ctx.message.author.id
        val = (user, message)
        try:
            Db = DBConnect()
            conn = Db.open()
            cur = conn.cursor()
            Q = """INSERT INTO DiscordQuestions (username, question) Values (%s,%s)"""
            cur.execute(Q, val)
            conn.commit()
        except pymysql.err as err:
            print(err)
        await ctx.send('Question Added')

    @commands.command(name='Who')
    @commands.cooldown(1, 2)
    async def Who(self, ctx):
        try:
            Db = DBConnect()
            conn = Db.open()
            cur = conn.cursor()
            Q = """Select * FROM DiscordQuestions"""
            cur.execute(Q)
            result = cur.fetchall()
            for row in result:
                print(row)
            if len(result) > 0:
                await ctx.send("""Use The "./Answered" Command Followed by the Question ID to Delete Answered Questions""")
                for r in result:
                    ID = r['id']
                    user_id = int(r["username"])
                    question = r["question"]
                    member = await ctx.bot.fetch_user(user_id)
                    await ctx.send(member.mention + f"\n Asked:   {question}" + f"\n Question ID:  {str(ID)}")
                    #await ctx.send(f"```\n Asked:   {question}  \n Question ID:  {str(ID)}\n```")
            else:
                await ctx.send("No Open Questions. Nice!")
        except pymysql.err as err:
            print(err)

    @commands.command(name='Answered')
    @commands.cooldown(1, 2)
    async def Del(self, ctx, *, message):
        if message.isdigit():
            ID = int(message)
            try:
                Db = DBConnect()
                conn = Db.open()
                cur = conn.cursor()
                Q = """DELETE FROM DiscordQuestions WHERE id = %s """
                cur.execute(Q, (ID,))
                conn.commit()
                Db.close()
            except pymysql.err as err:
                print(err)
            await ctx.send('Question Removed')
        else:
            await ctx.send("Not a Valid Answered ID")


def setup(bot):
    bot.add_cog(SQLCog(bot))
