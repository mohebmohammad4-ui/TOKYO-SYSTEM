import discord
from discord.ext import commands
from discord import app_commands
import re
from database import Database

db = Database()

class Colors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setcolor", description="تغيير لون الرتبة")
    @app_commands.describe(role="الرتبة", color="اللون (hex: #FF0000 أو FF0000)")
    async def set_color(self, interaction: discord.Interaction, role: discord.Role, color: str):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        color = color.replace('#', '').strip()
        if not re.match(r'^[0-9a-fA-F]{6}$', color):
            embed = discord.Embed(
                title="❌ خطأ",
                description="صيغة اللون غير صحيحة.\nاستخدم: `#FF0000` أو `FF0000`",
                color=0xff2d55
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            color_int = int(color, 16)
            await role.edit(color=discord.Color(color_int))
            embed = discord.Embed(
                title="✅ تم التغيير",
                description=f"تم تغيير لون {role.mention} إلى `#{color}`",
                color=color_int
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=0xff2d55
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Colors(bot))
