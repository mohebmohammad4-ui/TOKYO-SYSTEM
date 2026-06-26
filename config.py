import discord

# ====== TOKEN & PREFIX ======
TOKEN = "YOUR_BOT_TOKEN_HERE"
PREFIX = "!"
OWNER_ID = 123456789  # ضع ID حسابك

# ====== الألوان (ثيم TOKYO) ======
COLORS = {
    "primary": 0x00d4ff,
    "danger": 0xff2d55,
    "success": 0x00ff88,
    "warning": 0xffd700,
    "purple": 0x7b2ffc,
    "dark": 0x0a0a0a,
    "pink": 0xff2d95,
    "gold": 0xffd700
}

# ====== نظام XP ======
XP_MIN = 1
XP_MAX = 5
MSG_MIN = 3
MSG_MAX = 5

# ====== متطلبات المستويات ======
LEVEL_REQS = {
    0: 200,
    5: 400,
    10: 800,
    15: 1000
}

# ====== الرتب التلقائية ======
AUTO_ROLES = {}  # هتتضاف عن طريق الأمر !setautolevel

# ====== أعضاء Premium ======
PREMIUM_USERS = []  # هتتضاف عن طريق الأمر !premium

# ====== Anti-Spam ======
SPAM_LIMIT = 5
SPAM_WINDOW = 5

# ====== رسائل الترحيب ======
WELCOME_MESSAGES = [
    "🎌 **{member}** مرحبًا بك في **TOKYO COMMUNITY**!",
    "🇯🇵 أهلاً {member} في طوكيو! استمتع معنا 💫",
    "🌸 نورت السيرفر {member}! TOKYO COMMUNITY تفتخر بك ✨"
]

# ====== رسائل التكت ======
TICKET_OPEN_MESSAGE = """
🎫 **تم فتح تكت جديد!**

<@&{support_role}> مطلوب دعم للعضو {member}

**الرجاء الضغط على زر الاستلام للتعامل مع التكت.**
"""

TICKET_CLOSE_MESSAGE = """
🔒 **تم إغلاق التكت**

شكراً لاستخدامك نظام الدعم في **TOKYO COMMUNITY** 🇯🇵
"""
