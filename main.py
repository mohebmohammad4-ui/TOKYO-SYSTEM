import discord
from discord.ext import commands
import os
import asyncio
import sys
from config import TOKEN, PREFIX, COLORS
from database import Database

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
db = Database()

async def load_cogs():
    cogs_list = [
        'cogs.admin',
        'cogs.leveling',
        'cogs.tickets',
        'cogs.autoreply',
        'cogs.welcome',
        'cogs.logs',
        'cogs.antispam',
        'cogs.voice',
        'cogs.slash_commands'  # ➕ نظام الأوامر المائلة
    ]
    
    for cog in cogs_list:
        try:
            await bot.load_extension(cog)
            print(f'✅ تم تحميل {cog}')
        except Exception as e:
            print(f'❌ فشل تحميل {cog}: {e}')

@bot.event
async def on_ready():
    print(f'✅ {bot.user} جاهز للعمل!')
    print(f'📊 شغال على {len(bot.guilds)} سيرفرات')
    
    # ====== تسجيل الأوامر المائلة ======
    try:
        synced = await bot.tree.sync()
        print(f'✅ تم تسجيل {len(synced)} أمر مائل')
    except Exception as e:
        print(f'❌ فشل تسجيل الأوامر: {e}')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="TOKYO COMMUNITY 🇯🇵"
        )
    )

@bot.event
async def on_connect():
    print('🔄 جاري الاتصال بـ Discord...')

# ====== أمر المساعدة ======
@bot.tree.command(name="help", description="عرض قائمة الأوامر")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎌 TOKYO SYSTEM - قائمة الأوامر",
        description="جميع أوامر البوت مقسمة حسب الأنظمة",
        color=COLORS["primary"]
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    embed.add_field(
        name="🛡️ الإدارة",
        value="`/ban` `/timeout` `/warn` `/warnings` `/delwarn` `/addadmin` `/removeadmin`",
        inline=False
    )
    
    embed.add_field(
        name="📈 المستويات",
        value="`/rank` `/leaderboard`",
        inline=False
    )
    
    embed.add_field(
        name="🎫 التكتات",
        value="`/ticket` `/close` `/claim` `/unclaim`",
        inline=False
    )
    
    embed.add_field(
        name="🤖 الردود التلقائية",
        value="`/addreply` `/delreply` `/replies`",
        inline=False
    )
    
    embed.add_field(
        name="🎊 الترحيب",
        value="`/setwelcome`",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ الإعدادات",
        value="`/settings` `/setlog` `/setticketcat` `/setsupport` `/setautolevel`",
        inline=False
    )
    
    embed.set_footer(text="TOKYO COMMUNITY 🇯🇵 | صنع بحب ❤️")
    await interaction.response.send_message(embed=embed)

async def main():
    try:
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ خطأ في التوكن!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
