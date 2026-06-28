import discord
from discord.ext import commands
from discord import app_commands
from database import Database

db = Database()

class SelfRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="selfrole", description="أخذ أو إزالة رتبة اختيارية")
    @app_commands.describe(role="الرتبة")
    async def self_role(self, interaction: discord.Interaction, role: discord.Role):
        if not db.is_self_role(role.id):
            embed = discord.Embed(
                title="❌ غير متاحة",
                description="هذه الرتبة غير متاحة للاختيار الذاتي.",
                color=0xff2d55
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(
                title="✅ تمت الإزالة",
                description=f"تم إزالة {role.mention} من رتبك.",
                color=0x00ff88
            )
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(
                title="✅ تمت الإضافة",
                description=f"تم إضافة {role.mention} إلى رتبك.",
                color=0x00ff88
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addselfrole", description="إضافة رتبة اختيارية")
    @app_commands.describe(role="الرتبة", emoji="الإيموجي (اختياري)")
    async def add_self_role(self, interaction: discord.Interaction, role: discord.Role, emoji: str = None):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.add_self_role(role.id, emoji)
        embed = discord.Embed(
            title="✅ تمت الإضافة",
            description=f"أصبح بإمكان الأعضاء الآن أخذ {role.mention} بأنفسهم.",
            color=0x00ff88
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removeselfrole", description="إزالة رتبة اختيارية")
    @app_commands.describe(role="الرتبة")
    async def remove_self_role(self, interaction: discord.Interaction, role: discord.Role):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.remove_self_role(role.id)
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"تم إزالة {role.mention} من الرتب الاختيارية.",
            color=0x00ff88
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SelfRoles(bot))
