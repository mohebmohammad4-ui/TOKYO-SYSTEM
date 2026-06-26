import discord
from discord.ext import commands
from datetime import datetime
from database import Database

db = Database()

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_join_time = {}
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # دخول الفويس
        if before.channel is None and after.channel is not None:
            self.voice_join_time[member.id] = datetime.now()
            
            # تحديث قاعدة البيانات
            db.c.execute(
                "INSERT INTO voice_activity (user_id, last_join) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET last_join = ?",
                (member.id, datetime.now().isoformat(), datetime.now().isoformat())
            )
            db.conn.commit()
        
        # خروج الفويس
        elif before.channel is not None and after.channel is None:
            if member.id in self.voice_join_time:
                join_time = self.voice_join_time[member.id]
                duration = (datetime.now() - join_time).seconds // 60  # بالدقائق
                
                if duration > 0:
                    # تحديث عدد الدقائق
                    db.c.execute(
                        "UPDATE voice_activity SET total_minutes = total_minutes + ? WHERE user_id = ?",
                        (duration, member.id)
                    )
                    db.conn.commit()
                    
                    # إضافة XP مقابل وقت الفويس (كل 10 دقائق = 1 XP)
                    xp_from_voice = duration // 5
                    if xp_from_voice > 0:
                        data = db.get_level_data(member.id)
                        if data:
                            current_xp, current_level = data
                            db.update_level(member.id, current_xp + xp_from_voice, current_level)
                
                del self.voice_join_time[member.id]

async def setup(bot):
    await bot.add_cog(Voice(bot))
