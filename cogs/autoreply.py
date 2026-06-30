import discord
from discord.ext import commands
import sqlite3
import os

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ AutoReply Cog loaded!")

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل رسائل البوت نفسه
        if message.author.bot:
            return

        # طباعة للتصحيح (تأكد من أن البوت يقرأ الرسائل)
        print(f"📩 رسالة من {message.author}: {message.content}")

        # مسار قاعدة البيانات
        db_path = '/app/data/tokyo.db'
        if not os.path.exists(db_path):
            os.makedirs('/app/data', exist_ok=True)
            open(db_path, 'a').close()

        # جلب جميع الردود من قاعدة البيانات
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT trigger, response FROM autoreply")
        replies = c.fetchall()
        conn.close()

        # التحقق من وجود ردود
        if not replies:
            return

        # التحقق من كل رد
        for trigger, response in replies:
            if trigger.lower() in message.content.lower():
                print(f"✅ رد على رسالة {message.author}: {response}")
                await message.channel.send(response)
                break

async def setup(bot):
    await bot.add_cog(AutoReply(bot))
