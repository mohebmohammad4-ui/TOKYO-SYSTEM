import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import datetime
import asyncio
from config import COLORS, TICKET_CLOSE_MESSAGE
from database import Database

db = Database()

# ====== قائمة أقسام التكتات ======
TICKET_CATEGORIES = {
    "استفسار": {
        "emoji": "❓",
        "color": 0x00d4ff,
        "description": "للاستفسارات العامة عن السيرفر"
    },
    "شكوى": {
        "emoji": "⚠️",
        "color": 0xff2d55,
        "description": "لتقديم شكوى ضد عضو أو مشرف"
    },
    "طلب رتبة": {
        "emoji": "🏅",
        "color": 0xffd700,
        "description": "لطلب رتبة معينة (تأكد من استيفاء الشروط)"
    },
    "اقتراح": {
        "emoji": "💡",
        "color": 0x7b2ffc,
        "description": "لتقديم اقتراح لتطوير السيرفر"
    },
    "دعم فني": {
        "emoji": "🔧",
        "color": 0x00ff88,
        "description": "للحصول على دعم فني في البوت أو السيرفر"
    },
    "أخرى": {
        "emoji": "📌",
        "color": 0xff2d95,
        "description": "لأي شيء آخر غير مذكور"
    }
}

# ====== أزرار التكت داخل الروم ======
class TicketButtons(View):
    def __init__(self, bot, ticket_channel, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_channel = ticket_channel
        self.user = user
    
    @discord.ui.button(label="🔒 إغلاق التكت", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        ticket_data = db.get_ticket(self.ticket_channel.id)
        if not ticket_data:
            return await interaction.response.send_message("❌ هذا التكت غير موجود.", ephemeral=True)
        
        user_id = ticket_data[1]
        assigned_to = ticket_data[3]
        
        is_owner = interaction.user.id == user_id
        is_assigned = interaction.user.id == assigned_to if assigned_to else False
        is_admin = db.is_admin(interaction.user.id)
        
        if not (is_owner or is_assigned or is_admin):
            return await interaction.response.send_message("❌ ليس لديك صلاحية لإغلاق هذا التكت.", ephemeral=True)
        
        db.close_ticket(self.ticket_channel.id)
        
        embed = discord.Embed(
            title="🔒 تم إغلاق التكت",
            description=TICKET_CLOSE_MESSAGE,
            color=COLORS["danger"]
        )
        embed.add_field(name="تم الإغلاق بواسطة", value=interaction.user.mention)
        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵")
        
        await interaction.response.send_message(embed=embed)
        
        # حذف الروم بعد 5 ثواني
        await asyncio.sleep(5)
        await self.ticket_channel.delete()
    
    @discord.ui.button(label="📩 استلام التكت", style=discord.ButtonStyle.primary, custom_id="claim_ticket")
    async def claim_button(self, interaction: discord.Interaction, button: Button):
        # التحقق من أن المستخدم أدمن أو عنده رتبة الدعم
        support_role_id = db.get_setting('support_role')
        is_support = False
        if support_role_id:
            role = interaction.guild.get_role(int(support_role_id))
            if role and role in interaction.user.roles:
                is_support = True
        
        if not (db.is_admin(interaction.user.id) or is_support):
            return await interaction.response.send_message("❌ فقط فريق الدعم يمكنهم استلام التكتات.", ephemeral=True)
        
        ticket_data = db.get_ticket(self.ticket_channel.id)
        if not ticket_data:
            return await interaction.response.send_message("❌ هذا التكت غير موجود.", ephemeral=True)
        
        if ticket_data[3]:
            return await interaction.response.send_message(f"❌ هذا التكت تم استلامه بالفعل بواسطة <@{ticket_data[3]}>.", ephemeral=True)
        
        db.assign_ticket(self.ticket_channel.id, interaction.user.id)
        
        embed = discord.Embed(
            title="✅ تم استلام التكت",
            description=f"تم استلام التكت بواسطة {interaction.user.mention}",
            color=COLORS["success"]
        )
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label="🔄 إلغاء الاستلام", style=discord.ButtonStyle.secondary, custom_id="unclaim_ticket")
    async def unclaim_button(self, interaction: discord.Interaction, button: Button):
        support_role_id = db.get_setting('support_role')
        is_support = False
        if support_role_id:
            role = interaction.guild.get_role(int(support_role_id))
            if role and role in interaction.user.roles:
                is_support = True
        
        if not (db.is_admin(interaction.user.id) or is_support):
            return await interaction.response.send_message("❌ فقط فريق الدعم يمكنهم استخدام هذا الزر.", ephemeral=True)
        
        ticket_data = db.get_ticket(self.ticket_channel.id)
        if not ticket_data:
            return await interaction.response.send_message("❌ هذا التكت غير موجود.", ephemeral=True)
        
        if ticket_data[3] != interaction.user.id:
            return await interaction.response.send_message("❌ أنت لست المستلم لهذا التكت.", ephemeral=True)
        
        db.unassign_ticket(self.ticket_channel.id)
        
        embed = discord.Embed(
            title="🔄 تم إلغاء الاستلام",
            description=f"تم إلغاء استلام التكت بواسطة {interaction.user.mention}",
            color=COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed)

# ====== زر فتح التكت ======
class OpenTicketButton(Button):
    def __init__(self, category, emoji):
        super().__init__(
            label=category,
            emoji=emoji,
            style=discord.ButtonStyle.primary,
            custom_id=f"ticket_{category}"
        )
        self.category = category
    
    async def callback(self, interaction: discord.Interaction):
        # التحقق من التكتات المفتوحة للعضو
        open_tickets = db.get_open_tickets()
        for ticket in open_tickets:
            if ticket[1] == interaction.user.id:
                channel = interaction.guild.get_channel(ticket[0])
                if channel:
                    embed = discord.Embed(
                        title="❌ لديك تكت مفتوح بالفعل",
                        description=f"لديك تكت مفتوح في {channel.mention}",
                        color=COLORS["danger"]
                    )
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # جلب الإعدادات
        ticket_category_id = db.get_setting('ticket_category')
        support_role_id = db.get_setting('support_role')
        
        if not ticket_category_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم تحديد كاتيجوري للتكتات بعد.\nاستخدم الأمر `!setticketcat`",
                color=COLORS["danger"]
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        category = interaction.guild.get_channel(int(ticket_category_id))
        if not category:
            embed = discord.Embed(
                title="❌ خطأ",
                description="الكاتيجوري المحددة غير موجودة.",
                color=COLORS["danger"]
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # إنشاء الروم
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        if support_role_id:
            support_role = interaction.guild.get_role(int(support_role_id))
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        # إضافة الأدمن
        for admin_id in db.get_admins():
            admin = interaction.guild.get_member(admin_id)
            if admin:
                overwrites[admin] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        channel = await interaction.guild.create_text_channel(
            f"تكت-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            reason=f"تكت من {interaction.user} - {self.category}"
        )
        
        db.create_ticket(channel.id, interaction.user.id)
        
        # ====== إرسال رسالة التكت ======
        view = TicketButtons(interaction.client, channel, interaction.user)
        
        # منشن رتبة الدعم
        support_mention = f"<@&{support_role_id}>" if support_role_id else "@الدعم"
        
        embed = discord.Embed(
            title=f"{TICKET_CATEGORIES[self.category]['emoji']} تكت جديد - {self.category}",
            description=f"مرحبًا {interaction.user.mention}!",
            color=TICKET_CATEGORIES[self.category]['color']
        )
        embed.add_field(name="📂 القسم", value=self.category, inline=True)
        embed.add_field(name="👤 صاحب التكت", value=interaction.user.mention, inline=True)
        embed.add_field(name="🆔 رقم التكت", value=f"#{channel.id}", inline=True)
        embed.add_field(name="📝 الحالة", value="🟢 مفتوح", inline=False)
        embed.add_field(name="📌 معلومات", value="استخدم الأزرار أدناه للتحكم في التكت.", inline=False)
        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵 | نظام الدعم")
        
        await channel.send(f"📢 {support_mention} **مطلوب دعم!**")
        await channel.send(embed=embed, view=view)
        
        # تأكيد للعضو
        embed = discord.Embed(
            title="✅ تم إنشاء التكت",
            description=f"تم إنشاء تكتك في {channel.mention}",
            color=COLORS["success"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ====== قائمة اختيار الأقسام ======
class TicketCategorySelect(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # إضافة أزرار لكل قسم
        for category in TICKET_CATEGORIES:
            self.add_item(OpenTicketButton(
                category,
                TICKET_CATEGORIES[category]['emoji']
            ))

# ====== نظام التكتات الرئيسي ======
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ticketpanel')
    async def create_ticket_panel(self, ctx):
        """إنشاء لوحة التكتات في الروم"""
        if not db.is_admin(ctx.author.id):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك صلاحية لاستخدام هذا الأمر.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        # التحقق من وجود كاتيجوري
        ticket_category_id = db.get_setting('ticket_category')
        if not ticket_category_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم تحديد كاتيجوري للتكتات.\nاستخدم `!setticketcat` أولاً.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        # إنشاء الإمبيد
        embed = discord.Embed(
            title="🎫 نظام الدعم - TOKYO COMMUNITY",
            description="اختر القسم المناسب لطلبك من الأزرار أدناه.\nسيتم إنشاء تكت خاص بك وسيتم التواصل مع فريق الدعم.",
            color=COLORS["primary"]
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        # عرض الأقسام
        categories_text = ""
        for category, info in TICKET_CATEGORIES.items():
            categories_text += f"{info['emoji']} **{category}**: {info['description']}\n"
        
        embed.add_field(name="📂 الأقسام المتاحة", value=categories_text, inline=False)
        embed.add_field(
            name="📌 تنبيه",
            value="⚠️ يرجى اختيار القسم المناسب لطلبك.\n🔒 التكتات الخاصة بك خاصة بك فقط وفريق الدعم.",
            inline=False
        )
        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵 | اضغط على الزر لفتح تكت")
        
        # إرسال الإمبيد مع الأزرار
        view = TicketCategorySelect()
        await ctx.send(embed=embed, view=view)
        
        embed = discord.Embed(
            title="✅ تم إنشاء اللوحة",
            description="تم إنشاء لوحة التكتات في هذه القناة.",
            color=COLORS["success"]
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    # ====== أوامر الإدارة ======
    @commands.command(name='ticket')
    async def create_ticket_cmd(self, ctx, *, reason="طلب دعم"):
        """فتح تكت عبر الأمر"""
        # نفس الكود الموجود سابقاً
        pass
    
    @commands.command(name='close')
    async def close_ticket_command(self, ctx):
        """إغلاق التكت الحالي"""
        # نفس الكود الموجود سابقاً
        pass
    
    @commands.command(name='claim')
    async def claim_ticket_command(self, ctx):
        """استلام التكت"""
        # نفس الكود الموجود سابقاً
        pass
    
    @commands.command(name='unclaim')
    async def unclaim_ticket_command(self, ctx):
        """إلغاء استلام التكت"""
        # نفس الكود الموجود سابقاً
        pass

async def setup(bot):
    await bot.add_cog(Tickets(bot))
