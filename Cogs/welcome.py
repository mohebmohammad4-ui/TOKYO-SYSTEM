import discord
from discord.ext import commands
import random
from config import COLORS, WELCOME_MESSAGES
from database import Database

db = Database()

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel_id = db.get_setting('welcome_channel')
        if not welcome_channel_id:
            return
        
        channel = member.guild.get_channel(int(welcome_channel_id))
        if not channel:
            return
        
        welcome_msg = random.choice(WELCOME_MESSAGES).format(member=member.mention)
        member_count = member.guild.member_count
        
        embed = discord.Embed(
            title="🌸 مرحباً في TOKYO COMMUNITY",
            description=welcome_msg,
            color=COLORS["primary"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👥 عدد الأعضاء", value=f"**{member_count}** عضو", inline=True)
        embed.add_field(name="📅 تاريخ الانضمام", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵 | نتمنى لك وقتاً ممتعاً")
        
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        welcome_channel_id = db.get_setting('welcome_channel')
        if not welcome_channel_id:
            return
        
        channel = member.guild.get_channel(int(welcome_channel_id))
        if not channel:
            return
        
        embed = discord.Embed(
            title="👋 مع السلامة",
            description=f"غادرنا {member.mention}",
            color=COLORS["danger"]
        )
        embed.add_field(name="👥 عدد الأعضاء", value=f"**{member.guild.member_count}** عضو")
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
