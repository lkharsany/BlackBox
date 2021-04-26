import pymysql.cursors
from sshtunnel import SSHTunnelForwarder
from discord.ext import commands
import os
from discord import Embed


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


        #used to "override" the table that the question is added to for testing purposes
        if "$!" not in message:
            table = "DiscordQuestions"
            mes = message
        else:
            mes_list = message.split("$!")
            table = mes_list[0]
            mes = mes_list[1]

        val = (user, mes)
        try:
            Db = DBConnect()
            conn = Db.open()
            cur = conn.cursor()
            Q = f"""INSERT INTO {table} (username, question) Values (%s,%s)"""
            cur.execute(Q, val)
            conn.commit()
        except pymysql.err as err:
            print("here?")
            print(err)
        await ctx.send('Question Added')

    @commands.command(name='Who')
    @commands.cooldown(1, 2)
    async def Who(self, ctx, *, message=None):
        if not message:
            table = "DiscordQuestions"
        else:
            table = message
        try:
            Db = DBConnect()
            conn = Db.open()
            cur = conn.cursor()
            Q = f"""Select * FROM {table}"""
            cur.execute(Q)
            result = cur.fetchall()
            if len(result) > 0:
                await ctx.send(
                    """Use The "./Answered" Command Followed by the Question ID to Delete Answered Questions""")
                for r in result:
                    ID = r['id']
                    user_id = int(r["username"])
                    question = r["question"]
                    member = await ctx.bot.fetch_user(user_id)

                    Member_url = " https://discordapp.com/users/" + str(user_id)
                    embed = Embed(color=0xff9999, title="", description="")
                    embed.set_author(name=member.name, url=Member_url, icon_url=member.avatar_url)
                    embed.add_field(name="Question Asked", value=question)
                    embed.set_footer(text=f"Question ID:  {str(ID)}")

                    await ctx.send(embed=embed)

            else:
                await ctx.send("No Open Questions. Nice!")
        except pymysql.err as err:
            print(err)

    @commands.command(name='Answered')
    @commands.cooldown(1, 2)
    async def Del(self, ctx, *, message):

        if "$!" not in message:
            table = "DiscordQuestions"
            ID = message
        else:
            mes_list = message.split("$!")
            table = mes_list[0]
            ID = mes_list[1]

        if ID.isdigit():
            ID = int(ID)
            try:
                Db = DBConnect()
                conn = Db.open()
                cur = conn.cursor()
                Q = f"""DELETE FROM {table} WHERE id = %s """
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
