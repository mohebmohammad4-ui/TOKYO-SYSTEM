import discord
from discord.ext import commands
import os
import asyncio
import sys
from config import TOKEN, PREFIX, COLORS
from database import Database

# ====== إعدادات البوت مع تفعيل Intents ======
intents = discord.Intents.all()
intents.message_content = True  # ✅ هذا هو المطلوب عشان يقرأ الرسائل

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
db = Database()

async def load_cogs():
    cogs_list = [
        'cogs.admin',
        'cogs.leveling',
        'cogs.tickets',
        'cogs.autoreply',      # ✅ تأكد من وجوده
        'cogs.welcome',
        'cogs.logs',
        'cogs.antispam',
        'cogs.voice'
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
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="TOKYO COMMUNITY 🇯🇵"
        )
    )

@bot.event
async def on_connect():
    print('🔄 جاري الاتصال بـ Discord...')

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
