import discord
from discord.ext import commands
from discord import app_commands
from database import Database

db = Database()

class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addtwitch", description="إضافة إشعارات لتويش")
    @app_commands.describe(channel="قناة الإشعارات", streamer="اسم المقدم")
    async def add_twitch(self, interaction: discord.Interaction, channel: discord.TextChannel, streamer: str):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.add_notification('twitch', streamer.lower(), channel.id)
        embed = discord.Embed(
            title="✅ تمت الإضافة",
            description=f"سيتم إرسال إشعارات {streamer} في {channel.mention}.",
            color=0x00ff88
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addyoutube", description="إضافة إشعارات ليوتيوب")
    @app_commands.describe(channel="قناة الإشعارات", channel_id="معرف القناة")
    async def add_youtube(self, interaction: discord.Interaction, channel: discord.TextChannel, channel_id: str):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.add_notification('youtube', channel_id, channel.id)
        embed = discord.Embed(
            title="✅ تمت الإضافة",
            description=f"سيتم إرسال إشعارات القناة {channel_id} في {channel.mention}.",
            color=0x00ff88
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removenotification", description="إزالة إشعار")
    @app_commands.describe(service="t أو y", identifier="المعرف")
    async def remove_notification(self, interaction: discord.Interaction, service: str, identifier: str):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        service_map = {'t': 'twitch', 'y': 'youtube'}
        service_name = service_map.get(service.lower())
        if not service_name:
            embed = discord.Embed(title="❌ خطأ", description="استخدم `t` لتويش أو `y` ليوتيوب.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.remove_notification(service_name, identifier)
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"تم إزالة الإشعار لـ {identifier}.",
            color=0x00ff88
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Notifications(bot))
