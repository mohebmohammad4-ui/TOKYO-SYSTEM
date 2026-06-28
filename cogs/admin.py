import discord
from discord.ext import commands
from discord import app_commands
import re
import datetime
from config import COLORS, OWNER_ID, BASE_ADMIN_ROLE_ID
from database import Database

db = Database()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_authorized(self, user_id):
        return db.is_admin(user_id) or user_id == OWNER_ID

    # ====== التحقق من أن العضو لديه رتبة إدارية (أعلى من الرتبة الأساسية) ======
    def is_admin_role(self, member):
        """التحقق مما إذا كان العضو لديه أي رتبة إدارية (أعلى من الرتبة الأساسية)"""
        base_role = member.guild.get_role(BASE_ADMIN_ROLE_ID)
        if not base_role:
            return False

        for role in member.roles:
            if role.position >= base_role.position:
                return True
        return False
        
# ====== دالة تسجيل الإجراءات ======
def log_mod_action(self, action, target, moderator, reason):
    """تسجيل أوامر الإدارة في قاعدة البيانات"""
    db.add_mod_action(action, target.id, moderator.id, reason)
    
    # ====== نظام الصلاحيات الهرمي ======
    def has_command_permission(self, member):
        """التحقق من صلاحية العضو بناءً على الرتبة الهرمية"""
        if member.id == OWNER_ID:
            return True
        if db.is_admin(member.id):
            return True

        # جلب رتبة الصلاحيات من قاعدة البيانات
        command_role_id = db.get_setting('command_role')
        if not command_role_id:
            return False

        command_role = member.guild.get_role(int(command_role_id))
        if not command_role:
            return False

        # التحقق: إذا كان العضو عنده الرتبة أو رتبة أعلى منها
        for role in member.roles:
            if role.position >= command_role.position:
                return True

        return False

    # ====== دالة تحويل الوقت ======
    def parse_time(self, time_str):
        total_seconds = 0
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

    # ====== دالة تصحيح الأخطاء ======
    def get_command_help(self, command_name):
        helps = {
            'تايم': '`تايم @user وقت سبب`\nمثال: `تايم @أحمد 5m سبام`\nالوقت: `5m` (دقائق)، `2h` (ساعات)، `1d` (أيام)، `1w` (أسابيع)',
            'بان': '`بان @user سبب`\nمثال: `بان @أحمد شتائم`',
            'تحذير': '`تحذير @user سبب`\nمثال: `تحذير @أحمد مخالفة`',
            'تحذيرات': '`تحذيرات @user`\nمثال: `تحذيرات @أحمد`',
            'حذف_تحذير': '`حذف_تحذير @user رقم`\nمثال: `حذف_تحذير @أحمد 2`'
        }
        return helps.get(command_name, "الأمر غير معروف")

    # ====== نظام قراءة الشات (هرمي) ======
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # ====== التحقق من أن العضو لديه رتبة إدارية ======
        if not self.is_admin_role(message.author):
            return

        # ====== التحقق من الصلاحية الهرمية ======
        if not self.has_command_permission(message.author):
            embed = discord.Embed(
                title="❌ لا يوجد صلاحية",
                description=f"{message.author.mention}، ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            await message.channel.send(embed=embed)
            await message.delete()
            return

        # ====== أمر التايم ======
        match = re.match(r'تايم\s+<@!?(\d+)>\s+([\dwdhm]+)(?:\s+(.+))?', message.content)
        if match:
            user_id = int(match.group(1))
            time_str = match.group(2)
            reason = match.group(3) or "لا يوجد سبب"

            duration = self.parse_time(time_str)
            if not duration:
                embed = discord.Embed(
                    title="❌ صيغة الوقت غير صحيحة",
                    description=f"{message.author.mention}، الصيغة غير صحيحة.",
                    color=COLORS["danger"]
                )
                embed.add_field(
                    name="📖 الطريقة الصحيحة",
                    value=self.get_command_help('تايم'),
                    inline=False
                )
                await message.channel.send(embed=embed)
                await message.delete()
                return

            member = message.guild.get_member(user_id)
            if member:
                try:
                    await member.timeout(duration, reason=reason)
                    
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
                    embed = discord.Embed(
                        title="❌ خطأ",
                        description=f"حدث خطأ: {str(e)}",
                        color=COLORS["danger"]
                    )
                    await message.channel.send(embed=embed)
            return
            self.log_mod_action("timeout", member, ctx.auther, reason)

        # ====== أمر الحظر ======
        match = re.match(r'بان\s+<@!?(\d+)>(?:\s+(.+))?', message.content)
        if match:
            user_id = int(match.group(1))
            reason = match.group(2) or "لا يوجد سبب"

            if not message.mentions:
                embed = discord.Embed(
                    title="❌ خطأ في الصيغة",
                    description=f"{message.author.mention}، يجب أن تمنشن العضو.",
                    color=COLORS["danger"]
                )
                embed.add_field(
                    name="📖 الطريقة الصحيحة",
                    value=self.get_command_help('بان'),
                    inline=False
                )
                await message.channel.send(embed=embed)
                await message.delete()
                return

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
                    embed = discord.Embed(
                        title="❌ خطأ",
                        description=f"حدث خطأ: {str(e)}",
                        color=COLORS["danger"]
                    )
                    await message.channel.send(embed=embed)
            return
            self.log_mod_action("ban", member, ctx.auther, reason)

        # ====== أمر التحذير ======
        match = re.match(r'تحذير\s+<@!?(\d+)>(?:\s+(.+))?', message.content)
        if match:
            user_id = int(match.group(1))
            reason = match.group(2) or "لا يوجد سبب"

            if not message.mentions:
                embed = discord.Embed(
                    title="❌ خطأ في الصيغة",
                    description=f"{message.author.mention}، يجب أن تمنشن العضو.",
                    color=COLORS["danger"]
                )
                embed.add_field(
                    name="📖 الطريقة الصحيحة",
                    value=self.get_command_help('تحذير'),
                    inline=False
                )
                await message.channel.send(embed=embed)
                await message.delete()
                return
                self.log_mod_action("warn", member, ctx.auther, reason)

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

    # ====== أوامر / (Slash Commands) ======
    
    @app_commands.command(name="setcommandrole", description="تحديد رتبة الصلاحيات (الرتب الأعلى تاخذ صلاحية تلقائيًا)")
    @app_commands.describe(role="الرتبة المطلوبة (كل الرتب الأعلى منها تاخذ الصلاحية)")
    async def set_command_role(self, interaction: discord.Interaction, role: discord.Role):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.set_setting('command_role', role.id)
        
        # جلب الرتب الأعلى
        higher_roles = [r for r in interaction.guild.roles if r.position > role.position]
        higher_roles_text = "\n".join([f"- {r.mention}" for r in higher_roles[:10]]) if higher_roles else "لا يوجد"
        if len(higher_roles) > 10:
            higher_roles_text += f"\nو {len(higher_roles) - 10} رتب أخرى"
        
        embed = discord.Embed(
            title="✅ تم التحديد",
            description=f"تم تحديد رتبة {role.mention} كرتبة الصلاحيات الأساسية.",
            color=COLORS["success"]
        )
        embed.add_field(
            name="👑 الرتب التي ستأخذ الصلاحية تلقائيًا",
            value=higher_roles_text,
            inline=False
        )
        embed.add_field(
            name="📌 ملاحظة",
            value="جميع الرتب الأعلى من {role.mention} في ترتيب الرتب ستأخذ نفس الصلاحية تلقائيًا.",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addadmin", description="إضافة عضو كأدمن في البوت")
    @app_commands.describe(member="العضو المراد إضافته")
    async def add_admin_slash(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.add_admin(member.id)
        embed = discord.Embed(title="✅ تمت الإضافة", description=f"تم إضافة {member.mention} كأدمن.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removeadmin", description="إزالة عضو من أدمن البوت")
    @app_commands.describe(member="العضو المراد إزالته")
    async def remove_admin_slash(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if member.id == OWNER_ID:
            embed = discord.Embed(title="❌ خطأ", description="لا يمكن إزالة المالك.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.remove_admin(member.id)
        embed = discord.Embed(title="✅ تمت الإزالة", description=f"تم إزالة {member.mention} من الأدمن.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="حظر عضو من السيرفر")
    @app_commands.describe(member="العضو المراد حظره", reason="سبب الحظر")
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🚫 تم الحظر",
                description=f"تم حظر {member.mention}",
                color=COLORS["danger"]
            )
            embed.add_field(name="السبب", value=reason)
            embed.add_field(name="المشرف", value=interaction.user.mention)
            embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ خطأ", description=f"حدث خطأ: {str(e)}", color=COLORS["danger"])
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="timeout", description="وضع عضو في تايم")
    @app_commands.describe(member="العضو", duration="المدة (مثال: 5m, 2h, 1d, 1w)", reason="سبب التايم")
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "لا يوجد سبب"):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        time_delta = self.parse_time(duration)
        if not time_delta:
            embed = discord.Embed(
                title="❌ صيغة الوقت غير صحيحة",
                description="استخدم: `5m` (دقائق)، `2h` (ساعات)، `1d` (أيام)، `1w` (أسابيع)",
                color=COLORS["danger"]
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.timeout(time_delta, reason=reason)
            total_seconds = time_delta.total_seconds()
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
            embed.add_field(name="المشرف", value=interaction.user.mention)
            embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ خطأ", description=f"حدث خطأ: {str(e)}", color=COLORS["danger"])
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="warn", description="إعطاء تحذير لعضو")
    @app_commands.describe(member="العضو", reason="سبب التحذير")
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        warn_id = db.add_warning(member.id, reason, interaction.user.id)
        embed = discord.Embed(
            title="⚠️ تم التحذير",
            description=f"تم تحذير {member.mention}",
            color=COLORS["warning"]
        )
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        embed.add_field(name="رقم التحذير", value=f"#{warn_id}")
        embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="عرض تحذيرات العضو")
    @app_commands.describe(member="العضو")
    async def warnings_slash(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        warnings = db.get_warnings(member.id)
        
        if not warnings:
            embed = discord.Embed(
                title="✅ لا توجد تحذيرات",
                description=f"{member.mention} ليس لديه أي تحذيرات.",
                color=COLORS["success"]
            )
            return await interaction.response.send_message(embed=embed)
        
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
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delwarn", description="حذف تحذير معين")
    @app_commands.describe(member="العضو", warn_id="رقم التحذير")
    async def delwarn_slash(self, interaction: discord.Interaction, member: discord.Member, warn_id: int):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        warnings = db.get_warnings(member.id)
        
        if not warnings or len(warnings) < warn_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"لا يوجد تحذير #{warn_id} لهذا العضو.",
                color=COLORS["danger"]
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.delete_warning(warnings[warn_id-1][0], member.id)
        embed = discord.Embed(
            title="✅ تم الحذف",
            description=f"تم حذف التحذير #{warn_id} من {member.mention}",
            color=COLORS["success"]
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="settings", description="عرض إعدادات البوت")
    async def settings_slash(self, interaction: discord.Interaction):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        settings = db.get_all_settings()
        auto_roles = db.get_auto_roles()
        
        embed = discord.Embed(title="⚙️ إعدادات TOKYO SYSTEM", color=COLORS["primary"])
        
        log_channel = settings.get('log_channel')
        welcome_channel = settings.get('welcome_channel')
        ticket_category = settings.get('ticket_category')
        support_role = settings.get('support_role')
        command_role = settings.get('command_role')
        
        embed.add_field(name="📋 قناة اللوقات", value=f"<#{log_channel}>" if log_channel else "❌ غير محددة", inline=False)
        embed.add_field(name="🎊 قناة الترحيب", value=f"<#{welcome_channel}>" if welcome_channel else "❌ غير محددة", inline=False)
        embed.add_field(name="📁 كاتيجوري التكتات", value=f"<#{ticket_category}>" if ticket_category else "❌ غير محددة", inline=False)
        embed.add_field(name="🛡️ رتبة الدعم", value=f"<@&{support_role}>" if support_role else "❌ غير محددة", inline=False)
        embed.add_field(name="🔑 رتبة الصلاحيات", value=f"<@&{command_role}>" if command_role else "❌ غير محددة", inline=False)
        
        if auto_roles:
            roles_text = "\n".join([f"المستوى {level} → <@&{role_id}>" for level, role_id in auto_roles])
            embed.add_field(name="🏅 الرتب التلقائية", value=roles_text, inline=False)
        else:
            embed.add_field(name="🏅 الرتب التلقائية", value="❌ لا توجد", inline=False)
        
        await interaction.response.send_message(embed=embed)

    # ====== أوامر الإعدادات ======
    @app_commands.command(name="setlog", description="تحديد قناة اللوقات")
    @app_commands.describe(channel="القناة")
    async def setlog_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.set_setting('log_channel', channel.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {channel.mention} كقناة للوقات.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setwelcome", description="تحديد قناة الترحيب")
    @app_commands.describe(channel="القناة")
    async def setwelcome_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.set_setting('welcome_channel', channel.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {channel.mention} كقناة للترحيب.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setticketcat", description="تحديد كاتيجوري التكتات")
    @app_commands.describe(category="الكاتيجوري")
    async def setticketcat_slash(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.set_setting('ticket_category', category.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {category.name} ككاتيجوري للتكتات.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setsupport", description="تحديد رتبة الدعم")
    @app_commands.describe(role="الرتبة")
    async def setsupport_slash(self, interaction: discord.Interaction, role: discord.Role):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.set_setting('support_role', role.id)
        embed = discord.Embed(title="✅ تم التحديد", description=f"تم تحديد {role.mention} كرتبة للدعم.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setautolevel", description="تحديد رتبة تلقائية لمستوى معين")
    @app_commands.describe(level="المستوى", role="الرتبة")
    async def setautolevel_slash(self, interaction: discord.Interaction, level: int, role: discord.Role):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.add_auto_role(level, role.id)
        embed = discord.Embed(
            title="✅ تم التحديد",
            description=f"عند الوصول للمستوى **{level}** سيتم إعطاء رتبة {role.mention}.",
            color=COLORS["success"]
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removeautolevel", description="حذف رتبة تلقائية")
    @app_commands.describe(level="المستوى")
    async def removeautolevel_slash(self, interaction: discord.Interaction, level: int):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.remove_auto_role(level)
        embed = discord.Embed(
            title="✅ تم الحذف",
            description=f"تم إلغاء الرتبة التلقائية للمستوى **{level}**.",
            color=COLORS["success"]
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
