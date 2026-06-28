import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config import COLORS, OWNER_ID
from database import Database

db = Database()

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_authorized(self, user_id):
        return db.is_admin(user_id) or user_id == OWNER_ID
    
    # ====== /addadmin ======
    @app_commands.command(name="addadmin", description="إضافة عضو كأدمن في البوت")
    @app_commands.describe(member="العضو المراد إضافته")
    async def add_admin(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.add_admin(member.id)
        embed = discord.Embed(title="✅ تمت الإضافة", description=f"تم إضافة {member.mention} كأدمن.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)
    
    # ====== /removeadmin ======
    @app_commands.command(name="removeadmin", description="إزالة عضو من أدمن البوت")
    @app_commands.describe(member="العضو المراد إزالته")
    async def remove_admin(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if member.id == OWNER_ID:
            embed = discord.Embed(title="❌ خطأ", description="لا يمكن إزالة المالك.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.remove_admin(member.id)
        embed = discord.Embed(title="✅ تمت الإزالة", description=f"تم إزالة {member.mention} من الأدمن.", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)
    
    # ====== /ban ======
    @app_commands.command(name="ban", description="حظر عضو من السيرفر")
    @app_commands.describe(member="العضو المراد حظره", reason="سبب الحظر")
    async def ban_member(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="🚫 تم الحظر", description=f"تم حظر {member.mention}", color=COLORS["danger"])
            embed.add_field(name="السبب", value=reason)
            embed.add_field(name="المشرف", value=interaction.user.mention)
            embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ خطأ", description=f"حدث خطأ: {str(e)}", color=COLORS["danger"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ====== /timeout ======
    @app_commands.command(name="timeout", description="وضع عضو في تايم")
    @app_commands.describe(member="العضو", minutes="عدد الدقائق", reason="سبب التايم")
    async def timeout_member(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "لا يوجد سبب"):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            duration = datetime.timedelta(minutes=minutes)
            await member.timeout(duration, reason=reason)
            embed = discord.Embed(title="⏰ تم التايم", description=f"تم وضع {member.mention} في تايم لمدة {minutes} دقائق", color=COLORS["warning"])
            embed.add_field(name="السبب", value=reason)
            embed.add_field(name="المشرف", value=interaction.user.mention)
            embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ خطأ", description=f"حدث خطأ: {str(e)}", color=COLORS["danger"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ====== /warn ======
    @app_commands.command(name="warn", description="إعطاء تحذير لعضو")
    @app_commands.describe(member="العضو", reason="سبب التحذير")
    async def warn_member(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        warn_id = db.add_warning(member.id, reason, interaction.user.id)
        embed = discord.Embed(title="⚠️ تم التحذير", description=f"تم تحذير {member.mention}", color=COLORS["warning"])
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        embed.add_field(name="رقم التحذير", value=f"#{warn_id}")
        embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        await interaction.response.send_message(embed=embed)
    
    # ====== /warnings ======
    @app_commands.command(name="warnings", description="عرض تحذيرات العضو")
    @app_commands.describe(member="العضو")
    async def show_warnings(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        warnings = db.get_warnings(member.id)
        
        if not warnings:
            embed = discord.Embed(title="✅ لا توجد تحذيرات", description=f"{member.mention} ليس لديه أي تحذيرات.", color=COLORS["success"])
            return await interaction.response.send_message(embed=embed)
        
        embed = discord.Embed(title=f"⚠️ تحذيرات {member.name}", description=f"عدد التحذيرات: {len(warnings)}", color=COLORS["warning"])
        
        for i, warn in enumerate(warnings[:10], 1):
            embed.add_field(name=f"#{i}", value=f"السبب: {warn[2]}\nالمشرف: <@{warn[3]}>\nالوقت: {warn[4][:16]}", inline=False)
        
        if len(warnings) > 10:
            embed.set_footer(text=f"و {len(warnings) - 10} تحذيرات أخرى")
        
        await interaction.response.send_message(embed=embed)
    
    # ====== /delwarn ======
    @app_commands.command(name="delwarn", description="حذف تحذير معين")
    @app_commands.describe(member="العضو", warn_id="رقم التحذير")
    async def delete_warning(self, interaction: discord.Interaction, member: discord.Member, warn_id: int):
        if not self.is_authorized(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        warnings = db.get_warnings(member.id)
        
        if not warnings or len(warnings) < warn_id:
            embed = discord.Embed(title="❌ خطأ", description=f"لا يوجد تحذير #{warn_id} لهذا العضو.", color=COLORS["danger"])
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.delete_warning(warnings[warn_id-1][0], member.id)
        embed = discord.Embed(title="✅ تم الحذف", description=f"تم حذف التحذير #{warn_id} من {member.mention}", color=COLORS["success"])
        await interaction.response.send_message(embed=embed)
    
    # ====== /settings ======
    @app_commands.command(name="settings", description="عرض إعدادات البوت")
    async def show_settings(self, interaction: discord.Interaction):
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
        
        embed.add_field(name="📋 قناة اللوقات", value=f"<#{log_channel}>" if log_channel else "❌ غير محددة", inline=False)
        embed.add_field(name="🎊 قناة الترحيب", value=f"<#{welcome_channel}>" if welcome_channel else "❌ غير محددة", inline=False)
        embed.add_field(name="📁 كاتيجوري التكتات", value=f"<#{ticket_category}>" if ticket_category else "❌ غير محددة", inline=False)
        embed.add_field(name="🛡️ رتبة الدعم", value=f"<@&{support_role}>" if support_role else "❌ غير محددة", inline=False)
        
        if auto_roles:
            roles_text = "\n".join([f"المستوى {level} → <@&{role_id}>" for level, role_id in auto_roles])
            embed.add_field(name="🏅 الرتب التلقائية", value=roles_text, inline=False)
        else:
            embed.add_field(name="🏅 الرتب التلقائية", value="❌ لا توجد", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
