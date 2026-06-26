import discord
from discord.ext import commands
from discord.ui import Button, View
import datetime
import asyncio
from config import COLORS, TICKET_OPEN_MESSAGE, TICKET_CLOSE_MESSAGE
from database import Database

db = Database()

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
        await asyncio.sleep(5)
        await self.ticket_channel.delete()
    
    @discord.ui.button(label="📩 استلام التكت", style=discord.ButtonStyle.primary, custom_id="claim_ticket")
    async def claim_button(self, interaction: discord.Interaction, button: Button):
        if not db.is_admin(interaction.user.id):
            return await interaction.response.send_message("❌ فقط الأدمن يمكنهم استلام التكتات.", ephemeral=True)
        
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
        if not db.is_admin(interaction.user.id):
            return await interaction.response.send_message("❌ فقط الأدمن يمكنهم استخدام هذا الزر.", ephemeral=True)
        
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

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ticket')
    async def create_ticket(self, ctx, *, reason="طلب دعم"):
        # جلب الإعدادات
        ticket_category_id = db.get_setting('ticket_category')
        support_role_id = db.get_setting('support_role')
        
        if not ticket_category_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم يتم تحديد كاتيجوري للتكتات بعد.\nاستخدم الأمر `!setticketcat #كاتيجوري`",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        # التحقق من التكتات المفتوحة
        open_tickets = db.get_open_tickets()
        for ticket in open_tickets:
            if ticket[1] == ctx.author.id:
                channel = ctx.guild.get_channel(ticket[0])
                if channel:
                    embed = discord.Embed(
                        title="❌ لديك تكت مفتوح بالفعل",
                        description=f"لديك تكت مفتوح في {channel.mention}",
                        color=COLORS["danger"]
                    )
                    return await ctx.send(embed=embed, ephemeral=True)
        
        # إنشاء الروم
        category = ctx.guild.get_channel(int(ticket_category_id))
        if not category:
            embed = discord.Embed(
                title="❌ خطأ",
                description="الكاتيجوري المحددة غير موجودة. استخدم `!setticketcat` مرة أخرى.",
                color=COLORS["danger"]
            )
            return await ctx.send(embed=embed)
        
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # إضافة صلاحيات رتبة الدعم
        if support_role_id:
            support_role = ctx.guild.get_role(int(support_role_id))
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        channel = await ctx.guild.create_text_channel(
            f"تكت-{ctx.author.name}",
            category=category,
            overwrites=overwrites,
            reason=f"تكت من {ctx.author}"
        )
        
        db.create_ticket(channel.id, ctx.author.id)
        
        view = TicketButtons(self.bot, channel, ctx.author)
        
        embed = discord.Embed(
            title="🎫 تكت جديد",
            description=f"مرحبًا {ctx.author.mention}!",
            color=COLORS["primary"]
        )
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="الحالة", value="🟢 مفتوح")
        embed.set_footer(text="TOKYO COMMUNITY 🇯🇵 | استخدم الأزرار للتحكم")
        
        support_role_mention = f"<@&{support_role_id}>" if support_role_id else "الدعم"
        await channel.send(
            TICKET_OPEN_MESSAGE.format(
                support_role=support_role_mention,
                member=ctx.author.mention
            )
        )
        await channel.send(embed=embed, view=view)
        
        embed = discord.Embed(
            title="✅ تم إنشاء التكت",
            description=f"تم إنشاء تكتك في {channel.mention}",
            color=COLORS["success"]
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.command(name='close')
    async def close_ticket_command(self, ctx):
        ticket_data = db.get_ticket(ctx.channel.id)
        if not ticket_data:
            return await ctx.send("❌ هذه القناة ليست تكت.", ephemeral=True)
        
        user_id = ticket_data[1]
        assigned_to = ticket_data[3]
        
        is_owner = ctx.author.id == user_id
        is_assigned = ctx.author.id == assigned_to if assigned_to else False
        is_admin = db.is_admin(ctx.author.id)
        
        if not (is_owner or is_assigned or is_admin):
            return await ctx.send("❌ ليس لديك صلاحية لإغلاق هذا التكت.", ephemeral=True)
        
        db.close_ticket(ctx.channel.id)
        
        embed = discord.Embed(
            title="🔒 تم إغلاق التكت",
            description="سيتم حذف هذه القناة خلال 5 ثواني.",
            color=COLORS["danger"]
        )
        await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await ctx.channel.delete()
    
    @commands.command(name='claim')
    async def claim_ticket_command(self, ctx):
        if not db.is_admin(ctx.author.id):
            return await ctx.send("❌ فقط الأدمن يمكنهم استلام التكتات.", ephemeral=True)
        
        ticket_data = db.get_ticket(ctx.channel.id)
        if not ticket_data:
            return await ctx.send("❌ هذه القناة ليست تكت.", ephemeral=True)
        
        if ticket_data[3]:
            return await ctx.send(f"❌ هذا التكت تم استلامه بالفعل بواسطة <@{ticket_data[3]}>.", ephemeral=True)
        
        db.assign_ticket(ctx.channel.id, ctx.author.id)
        
        embed = discord.Embed(
            title="✅ تم استلام التكت",
            description=f"تم استلام التكت بواسطة {ctx.author.mention}",
            color=COLORS["success"]
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='unclaim')
    async def unclaim_ticket_command(self, ctx):
        if not db.is_admin(ctx.author.id):
            return await ctx.send("❌ فقط الأدمن يمكنهم استخدام هذا الأمر.", ephemeral=True)
        
        ticket_data = db.get_ticket(ctx.channel.id)
        if not ticket_data:
            return await ctx.send("❌ هذه القناة ليست تكت.", ephemeral=True)
        
        if ticket_data[3] != ctx.author.id:
            return await ctx.send("❌ أنت لست المستلم لهذا التكت.", ephemeral=True)
        
        db.unassign_ticket(ctx.channel.id)
        
        embed = discord.Embed(
            title="🔄 تم إلغاء الاستلام",
            description=f"تم إلغاء استلام التكت بواسطة {ctx.author.mention}",
            color=COLORS["warning"]
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
