import discord
from discord.ext import commands
from discord import app_commands
from database import Database

db = Database()

class TempChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}  # {channel_id: owner_id}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # إذا دخل عضو لقناة مؤقتة
        if after.channel:
            temp_category_id = db.get_setting('temp_category')
            if temp_category_id and after.channel.category_id == int(temp_category_id):
                # إنشاء قناة جديدة
                guild = member.guild
                new_channel = await guild.create_voice_channel(
                    f"🎧 {member.display_name}",
                    category=after.channel.category,
                    reason=f"قناة مؤقتة لـ {member.display_name}"
                )
                await member.move_to(new_channel)
                self.temp_channels[new_channel.id] = member.id
                
                # حفظ في قاعدة البيانات
                db.set_setting(f'temp_channel_{new_channel.id}', member.id)
        
        # إذا غادر عضو قناة مؤقتة وأصبحت فارغة
        if before.channel:
            if before.channel.id in self.temp_channels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    del self.temp_channels[before.channel.id]
                    db.set_setting(f'temp_channel_{before.channel.id}', None)

    @app_commands.command(name="settempcat", description="تحديد كاتيجوري الرومات المؤقتة")
    @app_commands.describe(category="الكاتيجوري")
    async def set_temp_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        if not db.is_admin(interaction.user.id):
            embed = discord.Embed(title="❌ خطأ", description="ليس لديك صلاحية.", color=0xff2d55)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.set_setting('temp_category', category.id)
        embed = discord.Embed(
            title="✅ تم التحديد",
            description=f"تم تحديد {category.name} ككاتيجوري للرومات المؤقتة.",
            color=0x00ff88
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TempChannels(bot))
