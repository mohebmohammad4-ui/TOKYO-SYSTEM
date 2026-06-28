import discord
from discord.ext import commands
from datetime import datetime
from config import COLORS
from database import Database

db = Database()

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # ====== دوال إرسال لكل قناة ======
    async def send_log(self, embed, log_type="general"):
        """إرسال اللوق حسب النوع"""
        # جلب معرف القناة من قاعدة البيانات حسب النوع
        channel_id = db.get_setting(f'log_channel_{log_type}')
        if not channel_id:
            # إذا ما فيه قناة مخصصة، استخدم القناة العامة
            channel_id = db.get_setting('log_channel')
        
        if not channel_id:
            return
        
        channel = self.bot.get_channel(int(channel_id))
        if channel:
            await channel.send(embed=embed)
    
    # ====== أوامر تحديد قنوات مخصصة ======
    @commands.command(name='setlogdelete')
    async def set_log_delete(self, ctx, channel: discord.TextChannel):
        """تحديد قناة لوق حذف الرسائل"""
        if not db.is_admin(ctx.author.id):
            return await ctx.send("❌ ليس لديك صلاحية.")
        
        db.set_setting('log_channel_delete', channel.id)
        await ctx.send(f"✅ تم تحديد {channel.mention} للوق حذف الرسائل.")
    
    @commands.command(name='setlogedit')
    async def set_log_edit(self, ctx, channel: discord.TextChannel):
        """تحديد قناة لوق تعديل الرسائل"""
        if not db.is_admin(ctx.author.id):
            return await ctx.send("❌ ليس لديك صلاحية.")
        
        db.set_setting('log_channel_edit', channel.id)
        await ctx.send(f"✅ تم تحديد {channel.mention} للوق تعديل الرسائل.")
    
    @commands.command(name='setlogban')
    async def set_log_ban(self, ctx, channel: discord.TextChannel):
        """تحديد قناة لوق الحظر"""
        if not db.is_admin(ctx.author.id):
            return await ctx.send("❌ ليس لديك صلاحية.")
        
        db.set_setting('log_channel_ban', channel.id)
        await ctx.send(f"✅ تم تحديد {channel.mention} للوق الحظر.")
    
    @commands.command(name='setlogrole')
    async def set_log_role(self, ctx, channel: discord.TextChannel):
        """تحديد قناة لوق تغيير الرتب"""
        if not db.is_admin(ctx.author.id):
            return await ctx.send("❌ ليس لديك صلاحية.")
        
        db.set_setting('log_channel_role', channel.id)
        await ctx.send(f"✅ تم تحديد {channel.mention} للوق تغيير الرتب.")
    
    # ====== الأحداث ======
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        embed = discord.Embed(
            title="🗑️ رسالة محذوفة",
            color=COLORS["danger"],
            timestamp=datetime.now()
        )
        embed.add_field(name="المرسل", value=message.author.mention)
        embed.add_field(name="القناة", value=message.channel.mention)
        embed.add_field(name="المحتوى", value=message.content[:1000] or "بدون محتوى", inline=False)
        await self.send_log(embed, "delete")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        
        embed = discord.Embed(
            title="✏️ رسالة معدلة",
            color=COLORS["warning"],
            timestamp=datetime.now()
        )
        embed.add_field(name="المرسل", value=before.author.mention)
        embed.add_field(name="القناة", value=before.channel.mention)
        embed.add_field(name="قبل التعديل", value=before.content[:500] or "بدون محتوى", inline=False)
        embed.add_field(name="بعد التعديل", value=after.content[:500] or "بدون محتوى", inline=False)
        await self.send_log(embed, "edit")
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title="🚫 تم الحظر",
            color=COLORS["danger"],
            timestamp=datetime.now()
        )
        embed.add_field(name="العضو", value=f"{user} ({user.id})")
        embed.add_field(name="السيرفر", value=guild.name)
        await self.send_log(embed, "ban")
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            title="✅ تم فك الحظر",
            color=COLORS["success"],
            timestamp=datetime.now()
        )
        embed.add_field(name="العضو", value=f"{user} ({user.id})")
        embed.add_field(name="السيرفر", value=guild.name)
        await self.send_log(embed, "ban")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles
        
        for role in added_roles:
            if role.name != "@everyone":
                embed = discord.Embed(
                    title="➕ تم إضافة رتبة",
                    color=COLORS["success"],
                    timestamp=datetime.now()
                )
                embed.add_field(name="العضو", value=after.mention)
                embed.add_field(name="الرتبة", value=role.mention)
                await self.send_log(embed, "role")
        
        for role in removed_roles:
            if role.name != "@everyone":
                embed = discord.Embed(
                    title="➖ تم إزالة رتبة",
                    color=COLORS["danger"],
                    timestamp=datetime.now()
                )
                embed.add_field(name="العضو", value=after.mention)
                embed.add_field(name="الرتبة", value=role.name)
                await self.send_log(embed, "role")

async def setup(bot):
    await bot.add_cog(Logs(bot))
