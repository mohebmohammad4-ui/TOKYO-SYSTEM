import discord
from discord.ext import commands
from datetime import datetime
from config import COLORS
from database import Database

db = Database()

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def send_log(self, embed):
        log_channel_id = db.get_setting('log_channel')
        if not log_channel_id:
            return
        
        channel = self.bot.get_channel(int(log_channel_id))
        if channel:
            await channel.send(embed=embed)
    
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
        await self.send_log(embed)
    
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
        embed.add_field(name="قبل التعديل", value=before.content[:500], inline=False)
        embed.add_field(name="بعد التعديل", value=after.content[:500], inline=False)
        await self.send_log(embed)
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title="🚫 تم الحظر",
            color=COLORS["danger"],
            timestamp=datetime.now()
        )
        embed.add_field(name="العضو", value=f"{user} ({user.id})")
        embed.add_field(name="السيرفر", value=guild.name)
        await self.send_log(embed)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            title="✅ تم فك الحظر",
            color=COLORS["success"],
            timestamp=datetime.now()
        )
        embed.add_field(name="العضو", value=f"{user} ({user.id})")
        embed.add_field(name="السيرفر", value=guild.name)
        await self.send_log(embed)
    
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
                await self.send_log(embed)
        
        for role in removed_roles:
            if role.name != "@everyone":
                embed = discord.Embed(
                    title="➖ تم إزالة رتبة",
                    color=COLORS["danger"],
                    timestamp=datetime.now()
                )
                embed.add_field(name="العضو", value=after.mention)
                embed.add_field(name="الرتبة", value=role.name)
                await self.send_log(embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))
