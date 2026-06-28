import discord
from discord.ext import commands
import re
import datetime
from config import COLORS, OWNER_ID
from database import Database

db = Database()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_authorized(self, user_id):
        return db.is_admin(user_id) or user_id == OWNER_ID

    # ====== دالة تحويل الوقت ======
    def parse_time(self, time_str):
        """تحويل نص الوقت إلى timedelta"""
        total_seconds = 0
        
        # استخراج الأرقام والوحدات (مثال: 1w2d3h4m)
        pattern = r'(\d+)([wdhm])'
        matches = re.findall(pattern, time_str.lower())
        
        if not matches:
            return None
        
        for value, unit in matches:
            value = int(value)
            if unit == 'w':
                total_seconds += value * 7 * 24 * 3600
            elif unit == 'd':
                total_seconds += value * 24 * 3600
            elif unit == 'h':
                total_seconds += value * 3600
            elif unit == 'm':
                total_seconds += value * 60
        
        return datetime.timedelta(seconds=total_seconds) if total_seconds > 0 else None

    # ====== نظام قراءة الشات ======
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not (db.is_admin(message.author.id) or message.author.id == OWNER_ID):
            return

        # ====== أمر التايم (بالصيغ الجديدة) ======
        # مثال: "تايم @أحمد 5m سبام" أو "تايم @أحمد 1w2d سبام"
        match = re.match(r'تايم\s+<@!?(\d+)>\s+([\dwdhm]+)(?:\s+(.+))?', message.content)
        if match:
            user_id = int(match.group(1))
            time_str = match.group(2)
            reason = match.group(3) or "لا يوجد سبب"

            duration = self.parse_time(time_str)
            if not duration:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="صيغة الوقت غير صحيحة. استخدم:\n`5m` (دقائق)\n`2h` (ساعات)\n`1d` (أيام)\n`1w` (أسابيع)\nمثال: `تايم @أحمد 1w2d3h مخالفة`",
                    color=COLORS["danger"]
                )
                await message.channel.send(embed=embed)
                return

            member = message.guild.get_member(user_id)
            if member:
                try:
                    await member.timeout(duration, reason=reason)
                    
                    # تنسيق مدة التايم
                    total_seconds = duration.total_seconds()
                    days = int(total_seconds // 86400)
                    hours = int((total_seconds % 86400) // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    
                    time_text = ""
                    if days > 0:
                        time_text += f"{days} يوم "
                    if hours > 0:
                        time_text += f"{hours} ساعة "
                    if minutes > 0:
                        time_text += f"{minutes} دقيقة"
                    
                    embed = discord.Embed(
                        title="⏰ تم التايم",
                        description=f"تم وضع {member.mention} في تايم لمدة **{time_text}**",
                        color=COLORS["warning"]
                    )
                    embed.add_field(name="السبب", value=reason)
                    embed.add_field(name="المشرف", value=message.author.mention)
                    embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                    
                    await message.channel.send(embed=embed)
                    await message.delete()
                except Exception as e:
                    await message.channel.send(f"❌ خطأ: {str(e)}")
            return

        # ====== أمر الحظر ======
        match = re.match(r'بان\s+<@!?(\d+)>(?:\s+(.+))?', message.content)
        if match:
            user_id = int(match.group(1))
            reason = match.group(2) or "لا يوجد سبب"

            member = message.guild.get_member(user_id)
            if member:
                try:
                    await member.ban(reason=reason)
                    embed = discord.Embed(
                        title="🚫 تم الحظر",
                        description=f"تم حظر {member.mention}",
                        color=COLORS["danger"]
                    )
                    embed.add_field(name="السبب", value=reason)
                    embed.add_field(name="المشرف", value=message.author.mention)
                    embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                    await message.channel.send(embed=embed)
                    await message.delete()
                except Exception as e:
                    await message.channel.send(f"❌ خطأ: {str(e)}")
            return

        # ====== أمر التحذير ======
        match = re.match(r'تحذير\s+<@!?(\d+)>(?:\s+(.+))?', message.content)
        if match:
            user_id = int(match.group(1))
            reason = match.group(2) or "لا يوجد سبب"

            member = message.guild.get_member(user_id)
            if member:
                warn_id = db.add_warning(user_id, reason, message.author.id)
                embed = discord.Embed(
                    title="⚠️ تم التحذير",
                    description=f"تم تحذير {member.mention}",
                    color=COLORS["warning"]
                )
                embed.add_field(name="السبب", value=reason)
                embed.add_field(name="المشرف", value=message.author.mention)
                embed.add_field(name="رقم التحذير", value=f"#{warn_id}")
                embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                await message.channel.send(embed=embed)
                await message.delete()
            return

        # ====== أمر عرض التحذيرات ======
        match = re.match(r'تحذيرات\s+<@!?(\d+)>', message.content)
        if match:
            user_id = int(match.group(1))
            member = message.guild.get_member(user_id)
            if member:
                warnings = db.get_warnings(user_id)
                
                if not warnings:
                    embed = discord.Embed(
                        title="✅ لا توجد تحذيرات",
                        description=f"{member.mention} ليس لديه أي تحذيرات.",
                        color=COLORS["success"]
                    )
                    await message.channel.send(embed=embed)
                    await message.delete()
                    return
                
                embed = discord.Embed(
                    title=f"⚠️ تحذيرات {member.name}",
                    description=f"عدد التحذيرات: {len(warnings)}",
                    color=COLORS["warning"]
                )
                
                for i, warn in enumerate(warnings[:10], 1):
                    embed.add_field(
                        name=f"#{i}",
                        value=f"السبب: {warn[2]}\nالمشرف: <@{warn[3]}>\nالوقت: {warn[4][:16]}",
                        inline=False
                    )
                
                if len(warnings) > 10:
                    embed.set_footer(text=f"و {len(warnings) - 10} تحذيرات أخرى")
                
                await message.channel.send(embed=embed)
                await message.delete()
            return

        # ====== أمر حذف تحذير ======
        match = re.match(r'حذف_تحذير\s+<@!?(\d+)>\s+(\d+)', message.content)
        if match:
            user_id = int(match.group(1))
            warn_id = int(match.group(2))
            member = message.guild.get_member(user_id)
            
            if member:
                warnings = db.get_warnings(user_id)
                
                if not warnings or len(warnings) < warn_id:
                    embed = discord.Embed(
                        title="❌ خطأ",
                        description=f"لا يوجد تحذير #{warn_id} لهذا العضو.",
                        color=COLORS["danger"]
                    )
                    await message.channel.send(embed=embed)
                    await message.delete()
                    return
                
                db.delete_warning(warnings[warn_id-1][0], user_id)
                embed = discord.Embed(
                    title="✅ تم الحذف",
                    description=f"تم حذف التحذير #{warn_id} من {member.mention}",
                    color=COLORS["success"]
                )
                await message.channel.send(embed=embed)
                await message.delete()
            return

    # ====== الأوامر القديمة (للأدمن) ======
    @commands.command(name='addadmin')
    async def add_admin(self, ctx, member: discord.Member):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.add_admin(member.id)
        embed = discord.Embed(title="✅ تمت الإضافة", description=f"تم إضافة {member.mention} كأدمن.", color=COLORS["success"])
        await ctx.send(embed=embed)

    @commands.command(name='removeadmin')
    async def remove_admin(self, ctx, member: discord.Member):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        if member.id == OWNER_ID:
            embed = discord.Embed(title="❌ خطأ", description="لا يمكن إزالة المالك.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.remove_admin(member.id)
        embed = discord.Embed(title="✅ تمت الإزالة", description=f"تم إزالة {member.mention} من الأدمن.", color=COLORS["success"])
        await ctx.send(embed=embed)

    # ====== أوامر الإعدادات ======
    @commands.command(name='setlog')
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.set_setting('log_channel', channel.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {channel.mention} كقناة للوقات.", color=COLORS["success"])
        await ctx.send(embed=embed)

    @commands.command(name='setwelcome')
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.set_setting('welcome_channel', channel.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {channel.mention} كقناة للترحيب.", color=COLORS["success"])
        await ctx.send(embed=embed)

    @commands.command(name='setticketcat')
    async def set_ticket_category(self, ctx, category: discord.CategoryChannel):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.set_setting('ticket_category', category.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {category.name} ككاتيجوري للتكتات.", color=COLORS["success"])
        await ctx.send(embed=embed)

    @commands.command(name='setsupport')
    async def set_support_role(self, ctx, role: discord.Role):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.set_setting('support_role', role.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {role.mention} كرتبة للدعم.", color=COLORS["success"])
        await ctx.send(embed=embed)

    @commands.command(name='setautolevel')
    async def set_auto_level_role(self, ctx, level: int, role: discord.Role):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.add_auto_role(level, role.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"عند الوصول للمستوى **{level}** سيتم إعطاء رتبة {role.mention}.", color=COLORS["success"])
        await ctx.send(embed=embed)

    @commands.command(name='removeautolevel')
    async def remove_auto_level_role(self, ctx, level: int):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        db.remove_auto_role(level)
        embed = discord.Embed(title="✅ تم الحذف", description=f"تم إلغاء الرتبة التلقائية للمستوى **{level}**.", color=COLORS["success"])
        await ctx.send(embed=embed)

    @commands.command(name='settings')
    async def show_settings(self, ctx):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await ctx.send(embed=embed)
        
        settings = db.get_all_settings()
        auto_roles = db.get_auto_roles()
        
        embed = discord.Embed(title="⚙️ إعدادات TOKYO SYSTEM", color=COLORS["primary"])
        
        log_channel = settings.get('log_channel')
        welcome_channel = settings.get('welcome_channel')
        ticket_category = settings.get('ticket_category')
        support_role = settings.get('support_role')
        
        embed.add_field(name="📋 قناة اللوقات", value=f"<#{log_channel}>" if log_channel else "❌ غير محددة", inline=False)
        embed.add_field(name="🎊 قناة الترحيب", value=f"<#{welcome_channel}>" if welcome_channel else "❌ غير محددة", inline=False)
        embed.add_field(name="📁 كاتيجوري التكتات", value=f"<#{ticket_category}>" if ticket_category else "❌ غير محددة", inline=False)
        embed.add_field(name="🛡️ رتبة الدعم", value=f"<@&{support_role}>" if support_role else "❌ غير محددة", inline=False)
        
        if auto_roles:
            roles_text = "\n".join([f"المستوى {level} → <@&{role_id}>" for level, role_id in auto_roles])
            embed.add_field(name="🏅 الرتب التلقائية", value=roles_text, inline=False)
        else:
            embed.add_field(name="🏅 الرتب التلقائية", value="❌ لا توجد", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
