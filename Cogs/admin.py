import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config import COLORS, OWNER_ID
from database import Database

db = Database()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # ====== التحقق من الصلاحيات ======
    def is_authorized(self, user_id):
        return db.is_admin(user_id) or user_id == OWNER_ID
    
    # ====== إضافة أدمن ======
    @commands.command(name='addadmin')
    async def add_admin(self, ctx, member: discord.Member):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        db.add_admin(member.id)
        
        embed = discord.Embed(
            title="✅ تمت الإضافة",
            description=f"تم إضافة {member.mention} كأدمن في البوت.",
            color=COLORS["success"]
        )
        await ctx.send(embed=embed)
    
    # ====== حذف أدمن ======
    @commands.command(name='removeadmin')
    async def remove_admin(self, ctx, member: discord.Member):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        if member.id == OWNER_ID:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكن إزالة مالك البوت.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        db.remove_admin(member.id)
        
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"تم إزالة {member.mention} من أدمن البوت.",
            color=COLORS["success"]
        )
        await ctx.send(embed=embed)
    
    # ====== بان ======
    @commands.command(name='ban')
    async def ban_member(self, ctx, member: discord.Member, *, reason="لا يوجد سبب"):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        try:
            await member.ban(reason=reason)
            
            embed = discord.Embed(
                title="🚫 تم الحظر",
                description=f"تم حظر {member.mention}",
                color=COLORS["danger"]
            )
            embed.add_field(name="السبب", value=reason)
            embed.add_field(name="المشرف", value=ctx.author.mention)
            embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=COLORS["danger"]
            )
            await ctx.send(embed=embed)
    
    # ====== تايم ======
    @commands.command(name='timeout')
    async def timeout_member(self, ctx, member: discord.Member, minutes: int, *, reason="لا يوجد سبب"):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        try:
            duration = datetime.timedelta(minutes=minutes)
            await member.timeout(duration, reason=reason)
            
            embed = discord.Embed(
                title="⏰ تم التايم",
                description=f"تم وضع {member.mention} في تايم لمدة {minutes} دقائق",
                color=COLORS["warning"]
            )
            embed.add_field(name="السبب", value=reason)
            embed.add_field(name="المشرف", value=ctx.author.mention)
            embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=COLORS["danger"]
            )
            await ctx.send(embed=embed)
    
    # ====== تحذير ======
    @commands.command(name='warn')
    async def warn_member(self, ctx, member: discord.Member, *, reason="لا يوجد سبب"):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        warn_id = db.add_warning(member.id, reason, ctx.author.id)
        
        embed = discord.Embed(
            title="⚠️ تم التحذير",
            description=f"تم تحذير {member.mention}",
            color=COLORS["warning"]
        )
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=ctx.author.mention)
        embed.add_field(name="رقم التحذير", value=f"#{warn_id}")
        embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        await ctx.send(embed=embed)
        
        # محاولة إرسال DM للعضو
        try:
            dm_embed = discord.Embed(
                title="⚠️ تحذير من TOKYO COMMUNITY",
                description=f"لقد تم تحذيرك في سيرفر {ctx.guild.name}",
                color=COLORS["warning"]
            )
            dm_embed.add_field(name="السبب", value=reason)
            dm_embed.add_field(name="المشرف", value=ctx.author.name)
            await member.send(embed=dm_embed)
        except:
            pass
    
    # ====== عرض التحذيرات ======
    @commands.command(name='warnings')
    async def show_warnings(self, ctx, member: discord.Member):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        warnings = db.get_warnings(member.id)
        
        if not warnings:
            embed = discord.Embed(
                title="✅ لا توجد تحذيرات",
                description=f"{member.mention} ليس لديه أي تحذيرات.",
                color=COLORS["success"]
            )
            return await ctx.send(embed=embed)
        
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
        
        await ctx.send(embed=embed)
    
    # ====== حذف تحذير ======
    @commands.command(name='delwarn')
    async def delete_warning(self, ctx, member: discord.Member, warn_id: int):
        if not self.is_authorized(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        warnings = db.get_warnings(member.id)
        
        if not warnings or len(warnings) < warn_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"لا يوجد تحذير #{warn_id} لهذا العضو.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        db.delete_warning(warnings[warn_id-1][0], member.id)
        
        embed = discord.Embed(
            title="✅ تم الحذف",
            description=f"تم حذف التحذير #{warn_id} من {member.mention}",
            color=COLORS["success"]
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
