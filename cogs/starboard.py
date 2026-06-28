import discord
from discord.ext import commands
from discord import app_commands
from database import Database

db = Database()

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.star_threshold = 3

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or reaction.emoji != '⭐':
            return
        
        message = reaction.message
        channel_id = db.get_setting('starboard_channel')
        if not channel_id:
            return
        
        channel = message.guild.get_channel(int(channel_id))
        if not channel:
            return
        
        # حساب عدد النجوم
        star_count = sum(1 for r in message.reactions if str(r.emoji) == '⭐')
        
        if star_count >= self.star_threshold:
            embed = discord.Embed(
                description=message.content or "*بدون محتوى*",
                color=0xffd700,
                timestamp=message.created_at
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url
            )
            embed.add_field(name="⭐", value=str(star_count), inline=True)
            embed.add_field(name="🔗", value=f"[الرابط]({message.jump_url})", inline=True)
            
            if message.attachments:
                embed.set_image(url=message.attachments[0].url)
            
            await channel.send(embed=embed)

    @app_commands.command(name="setstarboard", description="تحديد قناة الـ Starboard")
    @app_commands.describe(channel="القناة", threshold="عدد النجوم المطلوب (افتراضي: 3)")
    async def set_starboard(self, interaction: discord.Interaction, channel: discord.TextChannel, threshold: int = 3):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.set_setting('starboard_channel', channel.id)
        self.star_threshold = threshold
        embed = discord.Embed(
            title="✅ تم التحديد",
            description=f"سيتم إرسال الرسائل المميزة إلى {channel.mention}\nالحد الأدنى للنجوم: **{threshold}**",
            color=0x00ff88
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Starboard(bot))
