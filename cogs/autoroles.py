import discord
from discord.ext import commands
from discord import app_commands
from database import Database

db = Database()

class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        join_role_id = db.get_setting('auto_join_role')
        if join_role_id:
            role = member.guild.get_role(int(join_role_id))
            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass

    @app_commands.command(name="setjoinrole", description="تحديد رتبة للأعضاء الجدد")
    @app_commands.describe(role="الرتبة")
    async def set_join_role(self, interaction: discord.Interaction, role: discord.Role):
        # ✅ تأجيل الرد لتجنب انتهاء الوقت
        await interaction.response.defer(ephemeral=True)
        
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        db.set_setting('auto_join_role', role.id)
        embed = discord.Embed(
            title="✅ تم التحديد",
            description=f"سيتم إعطاء {role.mention} تلقائياً للأعضاء الجدد.",
            color=0x00ff88
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="setlevelrole", description="تحديد رتبة عند مستوى معين")
    @app_commands.describe(level="المستوى", role="الرتبة")
    async def set_level_role(self, interaction: discord.Interaction, level: int, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        db.add_auto_role(level, role.id)
        embed = discord.Embed(
            title="✅ تم التحديد",
            description=f"عند الوصول للمستوى **{level}** سيتم إعطاء {role.mention}.",
            color=0x00ff88
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="removelevelrole", description="إزالة رتبة تلقائية")
    @app_commands.describe(level="المستوى")
    async def remove_level_role(self, interaction: discord.Interaction, level: int):
        await interaction.response.defer(ephemeral=True)
        
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        db.remove_auto_role(level)
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"تم إزالة الرتبة التلقائية للمستوى **{level}**.",
            color=0x00ff88
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoRoles(bot))
