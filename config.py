import discord

# ====== TOKEN & PREFIX ======
TOKEN = "YOUR_BOT_TOKEN_HERE"
PREFIX = "!"
OWNER_ID = 123456789  # ضع ID حسابك

# ====== CHANNEL IDs (اتركها None دلوقتي وهتضبطها بعدين) ======
LOG_CHANNEL_ID = None
WELCOME_CHANNEL_ID = None
TICKET_CATEGORY_ID = None
SUPPORT_ROLE_ID = None

# ====== الألوان (ثيم TOKYO) ======
COLORS = {
    "primary": 0x00d4ff,    # أزرق نيون
    "danger": 0xff2d55,     # أحمر نيون
    "success": 0x00ff88,    # أخضر نيون
    "warning": 0xffd700,    # ذهبي
    "purple": 0x7b2ffc,     # بنفسجي
    "dark": 0x0a0a0a,       # أسود
    "pink": 0xff2d95        # وردي
}

# ====== نظام XP ======
XP_MIN = 1
XP_MAX = 5
MSG_MIN = 3  # أقل عدد رسائل للحصول على XP
MSG_MAX = 5  # أقصى عدد رسائل للحصول على XP

# ====== متطلبات المستويات ======
LEVEL_REQS = {
    0: 200,    # من 0 إلى 4
    5: 400,    # من 5 إلى 9
    10: 800,   # من 10 إلى 14
    15: 1000   # 15 فما فوق
}

# ====== الرتب التلقائية (Level -> Role ID) ======
AUTO_ROLES = {
    5: None,   # حط ID الرتبة
    10: None,
    15: None,
    20: None,
    30: None
}

# ====== أعضاء Premium ======
PREMIUM_USERS = []

# ====== Anti-Spam ======
SPAM_LIMIT = 5      # عدد الرسائل
SPAM_WINDOW = 5     # بالثواني

# ====== ردود الترحيب ======
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
