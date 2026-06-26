import discord
from discord.ext import commands
import random
import math
from config import COLORS, XP_MIN, XP_MAX, MSG_MIN, MSG_MAX, LEVEL_REQS, AUTO_ROLES
from database import Database

db = Database()

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = {}  # لتتبع عدد الرسائل
    
    # ====== حساب متطلبات المستوى ======
    def get_level_req(self, level):
        for lvl, req in sorted(LEVEL_REQS.items(), reverse=True):
            if level >= lvl:
                return req
        return 200
    
    # ====== مستمع الرسائل ======
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # ====== منع السبام (تتبع الرسائل) ======
        if message.author.id not in self.user_messages:
            self.user_messages[message.author.id] = []
        
        self.user_messages[message.author.id].append(message.created_at)
        
        # حذف الرسائل القديمة من التتبع
        self.user_messages[message.author.id] = [
            t for t in self.user_messages[message.author.id]
            if (message.created_at - t).seconds < 60
        ]
        
        # إذا أرسل أكثر من 10 رسائل في دقيقة = سبام
        if len(self.user_messages[message.author.id]) > 10:
            return
        
        # ====== إضافة XP عشوائي ======
        # فرصة 30% للحصول على XP
        if random.randint(1, 100) <= 30:
            # عدد رسائل عشوائي بين MSG_MIN و MSG_MAX
            required_msgs = random.randint(MSG_MIN, MSG_MAX)
            
            # إذا وصل لعدد الرسائل المطلوب
            if len(self.user_messages[message.author.id]) >= required_msgs:
                xp_gain = random.randint(XP_MIN, XP_MAX)
                
                # جلب بيانات العضو الحالية
                data = db.get_level_data(message.author.id)
                
                if data:
                    current_xp, current_level = data
                    new_xp = current_xp + xp_gain
                    req = self.get_level_req(current_level)
                    
                    # إذا تجاوز متطلبات المستوى
                    if new_xp >= req:
                        new_level = current_level + 1
                        remaining_xp = new_xp - req
                        
                        db.update_level(message.author.id, remaining_xp, new_level)
                        
                        # رسالة الترقية
                        embed = discord.Embed(
                            title="🎉 ترقية مستوى!",
                            description=f"{message.author.mention} وصل إلى **مستوى {new_level}**!",
                            color=COLORS["primary"]
                        )
                        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵")
                        await message.channel.send(embed=embed)
                        
                        # ====== إعطاء رتبة تلقائية ======
                        if new_level in AUTO_ROLES:
                            role_id = AUTO_ROLES[new_level]
                            if role_id:
                                role = message.guild.get_role(role_id)
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
                    # أول مرة يحصل على XP
                    db.update_level(message.author.id, xp_gain, 0)
    
    # ====== عرض الرتبة ======
    @commands.command(name='rank', aliases=['level'])
    async def show_rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        data = db.get_level_data(member.id)
        
        if not data:
            embed = discord.Embed(
                title="❌ لا توجد بيانات",
                description=f"{member.mention} ليس لديه أي نقاط حتى الآن.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        xp, level = data
        req = self.get_level_req(level)
        progress = int((xp / req) * 100) if req > 0 else 0
        
        embed = discord.Embed(
            title=f"📊 رتبة {member.name}",
            color=member.color if member.color != discord.Color.default() else COLORS["primary"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🏅 المستوى", value=f"**{level}**", inline=True)
        embed.add_field(name="⭐ النقاط", value=f"**{xp}/{req}**", inline=True)
        embed.add_field(name="📈 التقدم", value=f"**{progress}%**", inline=True)
        
        # شريط التقدم
        bar_length = 20
        filled = int((progress / 100) * bar_length)
        bar = "▰" * filled + "▱" * (bar_length - filled)
        embed.add_field(name="", value=f"`{bar}`", inline=False)
        
        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵")
        await ctx.send(embed=embed)
    
    # ====== لوحة المتصدرين ======
    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    async def show_leaderboard(self, ctx, limit: int = 10):
        if limit > 20:
            limit = 20
        
        leaderboard = db.get_leaderboard(limit)
        
        if not leaderboard:
            embed = discord.Embed(
                title="❌ لا توجد بيانات",
                description="لا يوجد أعضاء في لوحة المتصدرين حتى الآن.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="🏆 لوحة المتصدرين",
            description="أعلى المستويات في السيرفر",
            color=COLORS["gold"]
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, level, xp) in enumerate(leaderboard, 1):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"<@{user_id}>"
            
            medal = medals[i-1] if i <= 3 else f"#{i}"
            embed.add_field(
                name=f"{medal} {name}",
                value=f"المستوى: **{level}** | النقاط: **{xp}**",
                inline=False
            )
        
        embed.set_footer(text=f"TOKYO COMMUNITY 🇯🇵 | إجمالي {len(leaderboard)} عضو")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
