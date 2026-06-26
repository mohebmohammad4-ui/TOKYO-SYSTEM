import discord
from discord.ext import commands
import os
import asyncio
import sys
from config import TOKEN, PREFIX, COLORS
from database import Database

# ====== إعدادات البوت ======
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
db = Database()

# ====== تحميل جميع الـ Cogs ======
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
        'cogs.premium',
        'cogs.temp_channels',
        'cogs.suggestions',
        'cogs.giveaways'
    ]
    
    for cog in cogs_list:
        try:
            await bot.load_extension(cog)
            print(f'✅ تم تحميل {cog}')
        except Exception as e:
            print(f'❌ فشل تحميل {cog}: {e}')

# ====== حدث تشغيل البوت ======
@bot.event
async def on_ready():
    print(f'✅ {bot.user} جاهز للعمل!')
    print(f'📊 شغال على {len(bot.guilds)} سيرفرات')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="TOKYO COMMUNITY 🇯🇵"
        )
    )

# ====== حدث بدء التشغيل ======
@bot.event
async def on_connect():
    print('🔄 جاري الاتصال بـ Discord...')

# ====== أمر المساعدة الرئيسي ======
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="🎌 TOKYO SYSTEM - قائمة الأوامر",
        description="جميع أوامر البوت مقسمة حسب الأنظمة",
        color=COLORS["primary"]
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    embed.add_field(
        name="🛡️ الإدارة",
        value="`!ban` `!timeout` `!warn` `!warnings` `!delwarn` `!addadmin` `!removeadmin`",
        inline=False
    )
    
    embed.add_field(
        name="📈 المستويات",
        value="`!rank` `!leaderboard`",
        inline=False
    )
    
    embed.add_field(
        name="🎫 التكتات",
        value="`!ticket` `!close` `!claim` `!unclaim`",
        inline=False
    )
    
    embed.add_field(
        name="🤖 الردود التلقائية",
        value="`!addreply` `!delreply` `!replies`",
        inline=False
    )
    
    embed.add_field(
        name="🎊 الترحيب",
        value="`!setwelcome` `!testwelcome`",
        inline=False
    )
    
    embed.add_field(
        name="📝 الاقتراحات",
        value="`!suggest` `!vote`",
        inline=False
    )
    
    embed.add_field(
        name="🎁 السحوبات",
        value="`!giveaway` `!reroll`",
        inline=False
    )
    
    embed.set_footer(text="TOKYO COMMUNITY 🇯🇵 | صنع بحب ❤️")
    await ctx.send(embed=embed)

# ====== تشغيل البوت ======
async def main():
    try:
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ خطأ في التوكن! تأكد من وضع التوكن الصحيح في متغيرات البيئة TOKEN")
        sys.exit(1)
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
