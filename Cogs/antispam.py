import discord
from discord.ext import commands
from datetime import datetime, timedelta
from config import SPAM_LIMIT, SPAM_WINDOW

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = {}
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # تجاهل الأدمن
        if message.author.guild_permissions.administrator:
            return
        
        user_id = message.author.id
        
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        
        # إضافة الوقت الحالي
        self.user_messages[user_id].append(datetime.now())
        
        # حذف الرسائل القديمة
        cutoff = datetime.now() - timedelta(seconds=SPAM_WINDOW)
        self.user_messages[user_id] = [
            t for t in self.user_messages[user_id]
            if t > cutoff
        ]
        
        # التحقق من السبام
        if len(self.user_messages[user_id]) > SPAM_LIMIT:
            # تحذير العضو
            try:
                await message.delete()
                warning = await message.channel.send(
                    f"⚠️ {message.author.mention} ممنوع السبام!",
                    delete_after=5
                )
                
                # تايم تلقائي لمدة 1 دقيقة
                await message.author.timeout(
                    timedelta(minutes=1),
                    reason="سبام تلقائي"
                )
            except:
                pass

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
