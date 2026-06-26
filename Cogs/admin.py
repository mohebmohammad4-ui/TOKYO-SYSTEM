import discord
from discord.ext import commands
import random
from config import COLORS, XP_MIN, XP_MAX, MSG_MIN, MSG_MAX, LEVEL_REQS
from database import Database

db = Database()

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = {}
    
    def get_level_req(self, level):
        for lvl, req in sorted(LEVEL_REQS.items(), reverse=True):
            if level >= lvl:
                return req
        return 200
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # منع السبام
        if message.author.id not in self.user_messages:
            self.user_messages[message.author.id] = []
        
        self.user_messages[message.author.id].append(message.created_at)
        self.user_messages[message.author.id] = [
            t for t in self.user_messages[message.author.id]
            if (message.created_at - t).seconds < 60
        ]
        
        if len(self.user_messages[message.author.id]) > 10:
            return
        
        # نظام XP
        if random.randint(1, 100) <= 30:
            required_msgs = random.randint(MSG_MIN, MSG_MAX)
            
            if len(self.user_messages[message.author.id]) >= required_msgs:
                xp_gain = random.randint(XP_MIN, XP_MAX)
                
                # التحقق من Premium
                is_premium = db.get_setting(f'premium_{message.author.id}', 'false') == 'true'
                if is_premium:
                    xp_gain *= 2
                
                data = db.get_level_data(message.author.id)
                
                if data:
                    current_xp, current_level = data
                    new_xp = current_xp + xp_gain
                    req = self.get_level_req(current_level)
                    
                    if new_xp >= req:
                        new_level = current_level + 1
                        remaining_xp = new_xp - req
                        
                        db.update_level(message.author.id, remaining_xp, new_level)
                        
                        embed = discord.Embed(
                            title="🎉 ترقية مستوى!",
                            description=f"{message.author.mention} وصل إلى **مستوى {new_level}**!",
                            color=COLORS["primary"]
                        )
                        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵")
                        await message.channel.send(embed=embed)
                        
                        # الرتب التلقائية
                        auto_roles = db.get_auto_roles()
                        for level, role_id in auto_roles:
                            if new_level == level:
                                role = message.guild.get_role(int(role_id))
                                if role:
                                    try:
                                        await message.author.add_roles(role)
                                        embed = discord.Embed(
                                            title="🏅 رتبة جديدة!",
                                            description=f"{message.author.mention} حصل على رتبة **{role.name}**!",
                                            color=COLORS["gold"]
                                        )
                                        await message.channel.send(embed=embed)
                                    except:
                                        pass
                    else:
                        db.update_level(message.author.id, new_xp, current_level)
                else:
                    db.update_level(message.author.id, xp_gain, 0)
    
    @commands.command(name='rank', aliases=['level'])
    async def show_rank(self, ctx, member: discord.Member = None):
