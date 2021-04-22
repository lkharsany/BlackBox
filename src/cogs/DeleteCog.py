from discord.ext import commands
from time import sleep

class DeleteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Deletes files with certain extensions
    @commands.Cog.listener()
    @commands.cooldown(1,2)
    async def on_message(self, message):
        blacklist = ['py', 'cpp', 'ipynb','pdf', 'docx', 'png','jpg','c','h','css','java','html','js','txt','sql']
        try:
            for attachment in message.attachments:

                if attachment.filename.split('.')[-1] in blacklist:
                    sleep(5)
                    await message.delete()
                    await message.channel.send('Please refrain from sending code to this channel.')
                    await message.author.send('Please do not send code to the group, if you need help regarding your code DM one of the tutors or lecturers.')
                    await self.bot.process_commands(message)
                    break
        except:
            print('unknown error')

def setup(bot):
    bot.add_cog(DeleteCog(bot))
