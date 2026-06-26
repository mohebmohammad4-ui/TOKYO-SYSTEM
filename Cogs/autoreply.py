import discord
from discord.ext import commands
from config import COLORS
from database import Database

db = Database()

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        for trigger, response in db.get_all_replies():
            if trigger.lower() in message.content.lower():
                await message.channel.send(response)
                break
    
    @commands.command(name='addreply')
    async def add_reply(self, ctx, trigger: str, *, response: str):
        if not db.is_admin(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        db.add_reply(trigger, response)
        
        embed = discord.Embed(
            title="✅ تمت الإضافة",
            description=f"تم إضافة رد تلقائي للكلمة: **{trigger}**",
            color=COLORS["success"]
        )
        embed.add_field(name="الرد", value=response)
        await ctx.send(embed=embed)
    
    @commands.command(name='delreply')
    async def delete_reply(self, ctx, trigger: str):
        if not db.is_admin(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        db.delete_reply(trigger)
        
        embed = discord.Embed(
            title="✅ تم الحذف",
            description=f"تم حذف الرد التلقائي للكلمة: **{trigger}**",
            color=COLORS["success"]
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='replies')
    async def show_replies(self, ctx):
        replies = db.get_all_replies()
        
        if not replies:
            embed = discord.Embed(
                title="📭 لا توجد ردود",
                description="لا يوجد أي ردود تلقائية مسجلة.",
                color=COLORS["warning"]
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="📋 قائمة الردود التلقائية",
            color=COLORS["primary"]
        )
        
        for trigger, response in replies[:20]:
            embed.add_field(
                name=f"🔑 {trigger}",
                value=f"رد: {response[:100]}{'...' if len(response) > 100 else ''}",
                inline=False
            )
        
        if len(replies) > 20:
            embed.set_footer(text=f"و {len(replies) - 20} ردود أخرى")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoReply(bot))
