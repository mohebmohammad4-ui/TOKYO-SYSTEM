import discord
from discord.ext import commands
import sqlite3
import os

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # جلب جميع الردود من قاعدة البيانات
        db_path = '/app/data/tokyo.db'
        if not os.path.exists(db_path):
            os.makedirs('/app/data', exist_ok=True)
            open(db_path, 'a').close()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT trigger, response FROM autoreply")
        replies = c.fetchall()
        conn.close()

        for trigger, response in replies:
            if trigger.lower() in message.content.lower():
                await message.channel.send(response)
                break

async def setup(bot):
    await bot.add_cog(AutoReply(bot))
