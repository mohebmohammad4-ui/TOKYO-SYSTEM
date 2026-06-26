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
        if before.channel is None and after.channel is not None:
            self.voice_join_time[member.id] = datetime.now()
            
            db.c.execute(
                "INSERT INTO voice_activity (user_id, last_join) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET last_join = ?",
                (member.id, datetime.now().isoformat(), datetime.now().isoformat())
            )
            db.conn.commit()
        
        elif before.channel is not None and after.channel is None:
            if member.id in self.voice_join_time:
                join_time = self.voice_join_time[member.id]
                duration = (datetime.now() - join_time).seconds // 60
                
                if duration > 0:
                    db.c.execute(
                        "UPDATE voice_activity SET total_minutes = total_minutes + ? WHERE user_id = ?",
                        (duration, member.id)
                    )
                    db.conn.commit()
                    
                    xp_from_voice = duration // 10
                    if xp_from_voice > 0:
                        data = db.get_level_data(member.id)
                        if data:
                            current_xp, current_level = data
                            db.update_level(member.id, current_xp + xp_from_voice, current_level)
                
                del self.voice_join_time[member.id]

async def setup(bot):
    await bot.add_cog(Voice(bot))
