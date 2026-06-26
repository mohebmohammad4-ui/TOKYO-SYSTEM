import os

# ====== TOKEN & PREFIX ======
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise ValueError("❌ التوكن غير موجود! ضعه في متغيرات البيئة TOKEN")

PREFIX = os.getenv('PREFIX', '!')
OWNER_ID = int(os.getenv('OWNER_ID', 123456789))

# ====== الألوان ======
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
XP_MIN = int(os.getenv('XP_MIN', 1))
XP_MAX = int(os.getenv('XP_MAX', 5))
MSG_MIN = int(os.getenv('MSG_MIN', 3))
MSG_MAX = int(os.getenv('MSG_MAX', 5))

# ====== متطلبات المستويات ======
LEVEL_REQS = {
    0: 200,
    5: 400,
    10: 800,
    15: 1000
}

# ====== Anti-Spam ======
SPAM_LIMIT = int(os.getenv('SPAM_LIMIT', 5))
SPAM_WINDOW = int(os.getenv('SPAM_WINDOW', 5))

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
