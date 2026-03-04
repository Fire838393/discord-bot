"""
═══════════════════════════════════════════════════════════════════════════════
🤖 SMPIL - DISCORD BOT
Complete Server Management Bot
Server IP: SMPIL.aternos.me:50992
═══════════════════════════════════════════════════════════════════════════════
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime
from collections import defaultdict
import os

# ═══════════════════════════════════════════════════════════════════════════════
# KEEP-ALIVE (for Replit hosting)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from flask import Flask
    from threading import Thread

    app = Flask('')

    @app.route('/')
    def home():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SMPIL Bot - Online</title>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    color: white;
                }
                .container {
                    text-align: center;
                    background: rgba(255,255,255,0.05);
                    padding: 50px;
                    border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.1);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
                }
                h1 { font-size: 3em; margin: 0; color: #e94560; }
                .status { color: #00ff88; font-size: 1.5em; margin: 20px 0; }
                .info { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin-top: 20px; }
                .ip { color: #e94560; font-size: 1.2em; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚔️ SMPIL</h1>
                <div class="status">✅ BOT ONLINE</div>
                <div class="info">
                    <p><strong>SMPIL Minecraft Server</strong></p>
                    <p class="ip">SMPIL.aternos.me:50992</p>
                    <p>Keep this URL in UptimeRobot to stay online 24/7</p>
                </div>
            </div>
        </body>
        </html>
        """

    def run():
        app.run(host='0.0.0.0', port=8080)

    def keep_alive():
        t = Thread(target=run)
        t.daemon = True
        t.start()
        print("✅ Keep-alive web server started on port 8080")

    KEEP_ALIVE_ENABLED = True

except ImportError:
    print("⚠️  Flask not installed - Keep-alive disabled")
    def keep_alive():
        pass
    KEEP_ALIVE_ENABLED = False

# ═══════════════════════════════════════════════════════════════════════════════
# BOT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

user_message_times = defaultdict(list)
user_warnings = defaultdict(int)

# ═══════════════════════════════════════════════════════════════════════════════
# EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print("\n" + "═" * 70)
    print("⚔️  SMPIL BOT IS NOW ONLINE".center(70))
    print("═" * 70)
    print(f"📛 Bot Name: {bot.user.name}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"📊 Servers: {len(bot.guilds)}")
    print("═" * 70)
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing: {e}")
    await bot.change_presence(
        activity=discord.Game(name="SMPIL.aternos.me:50992 | /help"),
        status=discord.Status.online
    )
    print("✅ Bot ready!\n" + "═" * 70)

@bot.event
async def setup_hook():
    bot.add_view(VerifyButton())
    bot.add_view(ApplicationButton())
    bot.add_view(ApplicationReviewButtons())
    bot.add_view(TicketButton())
    bot.add_view(TicketCloseButton())
    print("✅ Registered persistent views")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.guild:
        return
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return

    user_id = message.author.id
    current_time = datetime.datetime.now()

    user_message_times[user_id] = [
        t for t in user_message_times[user_id]
        if (current_time - t).total_seconds() < 5
    ]
    user_message_times[user_id].append(current_time)

    if len(user_message_times[user_id]) >= 5:
        user_warnings[user_id] += 1
        if user_warnings[user_id] == 1:
            try:
                await message.author.timeout(datetime.timedelta(minutes=5), reason="Spam")
                await message.channel.send(f"⚠️ {message.author.mention} timed out 5 minutes for spam!", delete_after=10)
            except:
                pass
        elif user_warnings[user_id] == 2:
            try:
                await message.author.timeout(datetime.timedelta(hours=1), reason="Spam x2")
                await message.channel.send(f"⚠️ {message.author.mention} timed out 1 hour for spam!", delete_after=10)
            except:
                pass
        elif user_warnings[user_id] >= 3:
            try:
                await message.author.kick(reason="Spam x3")
                await message.channel.send(f"🔨 {message.author.mention} kicked for repeated spam!", delete_after=10)
            except:
                pass
        user_message_times[user_id].clear()

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    guild = member.guild
    # Give unverified role
    unverified = discord.utils.get(guild.roles, name="❌ Unverified")
    if unverified:
        try:
            await member.add_roles(unverified)
        except:
            pass
    # Welcome message
    general = discord.utils.get(guild.text_channels, name='💬-general')
    if general:
        embed = discord.Embed(
            title="⚔️ Welcome to SMPIL!",
            description=f"Hey {member.mention}! Welcome to the server!\n\n"
                       f"**Server IP:** `SMPIL.aternos.me:50992`\n\n"
                       f"Go to <#verify> to get access to all channels!",
            color=discord.Color.from_rgb(233, 69, 96)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Member #{guild.member_count}")
        try:
            await general.send(embed=embed)
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Verify Me", style=discord.ButtonStyle.green, custom_id="smpil_verify_persistent")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        verified_role = discord.utils.get(guild.roles, name="✅ Verified")
        unverified_role = discord.utils.get(guild.roles, name="❌ Unverified")

        if verified_role and verified_role in member.roles:
            await interaction.response.send_message("✅ You're already verified!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            if verified_role:
                await member.add_roles(verified_role)
            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role)
        except Exception as e:
            await interaction.followup.send(f"❌ Could not assign roles: {e}", ephemeral=True)
            return

        try:
            rules_embed = discord.Embed(
                title="📜 SMPIL SERVER RULES",
                description="Welcome to SMPIL! Please read all the rules:",
                color=discord.Color.from_rgb(233, 69, 96)
            )
            rules_embed.add_field(name="1️⃣ No XRay", value="No xray texture packs or hacks. You will be banned.", inline=False)
            rules_embed.add_field(name="2️⃣ No Hacks", value="No reach hacks, fly hacks, or any cheat client.", inline=False)
            rules_embed.add_field(name="3️⃣ No Duping", value="No item duplication or exploit abuse. Bannable offense.", inline=False)
            rules_embed.add_field(name="4️⃣ No Anchors/End Crystals in PVP", value="These are banned in PVP combat.", inline=False)
            rules_embed.add_field(name="5️⃣ No Thorns", value="Thorns enchantment is banned on armor.", inline=False)
            rules_embed.add_field(name="6️⃣ No Griefing/Stealing", value="Don't steal from or grief other players (unless there's an active war).", inline=False)
            rules_embed.add_field(name="7️⃣ No Minimaps", value="Minimaps are banned.", inline=False)
            rules_embed.add_field(name="8️⃣ Don't Know the Seed", value="Knowing/using the seed to find structures is bannable.", inline=False)
            rules_embed.add_field(name="9️⃣ No Combat Logging", value="Don't log out during PVP. You'll die and drop items.", inline=False)
            rules_embed.add_field(name="🔟 Respect Others", value="No harassment, hate speech, or bullying.", inline=False)
            rules_embed.add_field(name="⚠️ Punishment System", value="Warning → Kick → Temp Ban → Permanent Ban", inline=False)
            rules_embed.set_footer(text="SMPIL.aternos.me:50992 • By verifying you agree to follow these rules!")
            await member.send(embed=rules_embed)
            await interaction.followup.send("✅ Verified! Check your DMs for the server rules!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("✅ Verified! (Enable DMs to receive the server rules)", ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TICKET SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class TicketTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🐛 Report Bug", description="Report a bug or issue", emoji="🐛", value="bug"),
            discord.SelectOption(label="💡 Suggestion", description="Suggest a feature or idea", emoji="💡", value="suggestion"),
            discord.SelectOption(label="❓ General Help", description="Get help with something", emoji="❓", value="help"),
            discord.SelectOption(label="👤 Report Player", description="Report a player breaking rules", emoji="👤", value="report_player"),
            discord.SelectOption(label="🔨 Ban Appeal", description="Appeal a ban or punishment", emoji="🔨", value="appeal"),
            discord.SelectOption(label="⚔️ PVP Dispute", description="Dispute a PVP or combat issue", emoji="⚔️", value="pvp"),
            discord.SelectOption(label="🎯 Other", description="Anything else", emoji="🎯", value="other"),
        ]
        super().__init__(
            placeholder="🎫 Select ticket type...",
            min_values=1, max_values=1,
            options=options,
            custom_id="smpil_ticket_select_persistent"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        ticket_type = self.values[0]

        existing = discord.utils.get(guild.text_channels, topic=f"Ticket-{member.id}")
        if existing:
            await interaction.response.send_message(f"❌ You already have a ticket open: {existing.mention}", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        category = discord.utils.get(guild.categories, name="🎫 TICKETS")
        if not category:
            category = await guild.create_category("🎫 TICKETS")

        mod_role = discord.utils.get(guild.roles, name="⚔️ Mod")
        admin_role = discord.utils.get(guild.roles, name="🛡️ Admin")
        owner_role = discord.utils.get(guild.roles, name="👑 Owner")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True)
        }
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        if owner_role:
            overwrites[owner_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)

        ticket_info = {
            "bug":           {"emoji": "🐛", "name": "bug",     "title": "Bug Report",     "color": discord.Color.red(),    "desc": "**Describe the bug:**\n\n**Steps to reproduce:**\n\n**What should have happened:**\n\n**Screenshots/evidence:**"},
            "suggestion":    {"emoji": "💡", "name": "suggest", "title": "Suggestion",      "color": discord.Color.gold(),   "desc": "**Your suggestion:**\n\n**Why should this be added:**\n\n**How would it work:**"},
            "help":          {"emoji": "❓", "name": "help",    "title": "General Help",    "color": discord.Color.blue(),   "desc": "**What do you need help with?**\n\nDescribe your question in detail."},
            "report_player": {"emoji": "👤", "name": "report",  "title": "Player Report",   "color": discord.Color.orange(), "desc": "**Player username:**\n\n**What rule did they break:**\n\n**Evidence (screenshots/video):**\n\n**When did this happen:**"},
            "appeal":        {"emoji": "🔨", "name": "appeal",  "title": "Ban Appeal",      "color": discord.Color.dark_red(),"desc": "**Your Minecraft username:**\n\n**Why were you banned:**\n\n**Why should you be unbanned:**\n\n**Do you understand what you did wrong:**"},
            "pvp":           {"emoji": "⚔️", "name": "pvp",     "title": "PVP Dispute",     "color": discord.Color.purple(), "desc": "**What happened:**\n\n**Who was involved:**\n\n**Evidence:**"},
            "other":         {"emoji": "🎯", "name": "other",   "title": "General Support", "color": discord.Color.blurple(),"desc": "**Describe your issue:**"},
        }

        info = ticket_info[ticket_type]
        channel = await guild.create_text_channel(
            name=f"{info['emoji']}{info['name']}-{member.name}",
            category=category,
            topic=f"Ticket-{member.id}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"{info['emoji']} {info['title']}",
            description=f"**Opened by:** {member.mention}\n\n"
                       f"{info['desc']}\n\n"
                       f"━━━━━━━━━━━━━━━━━━━━━━\n"
                       f"Staff will respond soon. Click 🔒 to close when resolved.",
            color=info['color']
        )
        embed.set_footer(text=f"SMPIL • Ticket ID: {member.id}")
        embed.timestamp = discord.utils.utcnow()

        mention = member.mention
        if mod_role:
            mention += f" {mod_role.mention}"

        await channel.send(content=mention, embed=embed, view=TicketCloseButton())
        await interaction.followup.send(f"✅ Ticket created: {channel.mention}", ephemeral=True)

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())

class TicketCloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="smpil_close_ticket_persistent")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        embed = discord.Embed(
            title="🔒 Ticket Closing",
            description=f"Closed by {interaction.user.mention}\n\nDeleting in 5 seconds...",
            color=discord.Color.red()
        )
        await interaction.channel.send(embed=embed)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class ApplicationModal(discord.ui.Modal, title="⚔️ SMPIL Staff Application"):
    ign = discord.ui.TextInput(label="Minecraft IGN", placeholder="Your in-game name...", required=True, max_length=50)
    age = discord.ui.TextInput(label="Your Age", placeholder="How old are you?", required=True, max_length=3)
    position = discord.ui.TextInput(label="Position Applying For", placeholder="Mod, Helper, Admin...", required=True, max_length=50)
    experience = discord.ui.TextInput(label="Staff Experience", placeholder="Previous moderation experience...", required=False, style=discord.TextStyle.paragraph, max_length=500)
    why = discord.ui.TextInput(label="Why Should We Pick You?", placeholder="Tell us why you'd be a good staff member...", required=True, style=discord.TextStyle.paragraph, max_length=500)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user

        try:
            age_num = int(self.age.value)
            if age_num < 13:
                await interaction.followup.send("❌ You must be at least 13 to apply.", ephemeral=True)
                return
        except:
            await interaction.followup.send("❌ Enter a valid age.", ephemeral=True)
            return

        existing = discord.utils.get(guild.text_channels, topic=f"Application-{member.id}")
        if existing:
            await interaction.followup.send(f"❌ You already have an open application: {existing.mention}", ephemeral=True)
            return

        app_category = discord.utils.get(guild.categories, name="📝 APPLICATIONS")
        if not app_category:
            app_category = await guild.create_category("📝 APPLICATIONS")

        mod_role = discord.utils.get(guild.roles, name="⚔️ Mod")
        admin_role = discord.utils.get(guild.roles, name="🛡️ Admin")
        owner_role = discord.utils.get(guild.roles, name="👑 Owner")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True)
        }
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        if owner_role:
            overwrites[owner_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        app_channel = await guild.create_text_channel(
            name=f"📝app-{member.name}",
            category=app_category,
            topic=f"Application-{member.id}",
            overwrites=overwrites
        )

        account_age = (discord.utils.utcnow() - member.created_at).days
        server_age = (discord.utils.utcnow() - member.joined_at).days if member.joined_at else 0

        embed = discord.Embed(
            title="📝 New Staff Application",
            description=f"**Applicant:** {member.mention}\n━━━━━━━━━━━━━━━━━━━━━━",
            color=discord.Color.from_rgb(233, 69, 96)
        )
        embed.add_field(
            name="👤 Player Info",
            value=f"**Discord:** {member.name}\n**IGN:** {self.ign.value}\n**Age:** {self.age.value}\n**Account Age:** {account_age} days\n**In Server:** {server_age} days",
            inline=False
        )
        embed.add_field(
            name="📋 Application",
            value=f"**Position:** {self.position.value}\n**Experience:** {self.experience.value or 'None provided'}\n**Why them:** {self.why.value}",
            inline=False
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Application ID: {member.id}")
        embed.timestamp = discord.utils.utcnow()

        mention_text = f"📢 New Application!\n{member.mention}\n"
        if admin_role:
            mention_text += f"{admin_role.mention}"

        await app_channel.send(content=mention_text, embed=embed, view=ApplicationReviewButtons())

        try:
            dm_embed = discord.Embed(
                title="✅ Application Submitted!",
                description=f"Your SMPIL staff application has been submitted!\n\n"
                           f"**Position:** {self.position.value}\n"
                           f"**Status:** 🟡 Pending Review\n\n"
                           f"Staff will review it soon. Check {app_channel.mention} for updates!\n\n"
                           f"Good luck! 🍀",
                color=discord.Color.green()
            )
            await member.send(embed=dm_embed)
        except:
            pass

        await interaction.followup.send(
            f"✅ Application submitted! Check {app_channel.mention} for updates.",
            ephemeral=True
        )

class ApplicationButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Apply Now", style=discord.ButtonStyle.green, custom_id="smpil_application_persistent")
    async def application_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal())

class ApplicationReviewButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green, custom_id="smpil_app_accept_persistent")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Staff only!", ephemeral=True)
            return

        channel_topic = interaction.channel.topic
        if not channel_topic or "Application-" not in channel_topic:
            await interaction.response.send_message("❌ Cannot find applicant info.", ephemeral=True)
            return

        applicant_id = int(channel_topic.split("Application-")[1])
        applicant = interaction.guild.get_member(applicant_id)

        embed = discord.Embed(
            title="✅ Application Accepted!",
            description=f"**Congratulations {applicant.mention if applicant else 'applicant'}!**\n\n"
                       f"Your application was **ACCEPTED** by {interaction.user.mention}!\n\n"
                       f"A staff member will assign your role shortly. Welcome to the team! 🎉",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

        if applicant:
            try:
                dm = discord.Embed(title="🎉 SMPIL Staff Application Accepted!", description="You've been accepted to the SMPIL staff team! Welcome aboard! 🎉", color=discord.Color.green())
                await applicant.send(embed=dm)
            except:
                pass

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, custom_id="smpil_app_reject_persistent")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Staff only!", ephemeral=True)
            return

        channel_topic = interaction.channel.topic
        if not channel_topic or "Application-" not in channel_topic:
            await interaction.response.send_message("❌ Cannot find applicant info.", ephemeral=True)
            return

        applicant_id = int(channel_topic.split("Application-")[1])
        applicant = interaction.guild.get_member(applicant_id)

        embed = discord.Embed(
            title="❌ Application Rejected",
            description=f"**{applicant.mention if applicant else 'Applicant'}**\n\n"
                       f"Application rejected by {interaction.user.mention}.\n\n"
                       f"You may reapply in 30 days.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

        if applicant:
            try:
                dm = discord.Embed(title="Application Update", description="Your SMPIL staff application was not accepted this time. You can reapply in 30 days. Keep being active! ✨", color=discord.Color.red())
                await applicant.send(embed=dm)
            except:
                pass

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.gray, custom_id="smpil_app_close_persistent")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Staff only!", ephemeral=True)
            return
        await interaction.response.defer()
        embed = discord.Embed(title="🔒 Application Closing", description=f"Closed by {interaction.user.mention}\n\nDeleting in 5 seconds...", color=discord.Color.red())
        await interaction.channel.send(embed=embed)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# AUTOSETUP COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="autosetup", description="🚀 Complete SMPIL server setup")
@app_commands.checks.has_permissions(administrator=True)
async def autosetup(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    log = []
    log.append("**🚀 SETTING UP SMPIL SERVER...**\n")

    # ROLES
    log.append("**📝 Creating Roles...**")
    roles_config = [
        ("👑 Owner",    discord.Color.gold(),                  discord.Permissions.all()),
        ("🛡️ Admin",    discord.Color.dark_red(),              discord.Permissions(administrator=True)),
        ("⚔️ Mod",      discord.Color.red(),                   discord.Permissions(kick_members=True, ban_members=True, manage_messages=True, moderate_members=True, view_audit_log=True)),
        ("🤝 Helper",   discord.Color.blue(),                  discord.Permissions(manage_messages=True)),
        ("💎 VIP+",     discord.Color.from_rgb(255, 215, 0),   discord.Permissions.none()),
        ("💠 VIP",      discord.Color.from_rgb(0, 191, 255),   discord.Permissions.none()),
        ("✅ Verified",  discord.Color.green(),                 discord.Permissions.none()),
        ("❌ Unverified",discord.Color.dark_gray(),             discord.Permissions.none()),
        ("🔇 Muted",    discord.Color.dark_gray(),             discord.Permissions(send_messages=False, add_reactions=False, speak=False)),
        ("🤖 Bot",      discord.Color.light_gray(),            discord.Permissions.none()),
    ]

    created_roles = {}
    for role_name, role_color, role_perms in roles_config:
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name, color=role_color, permissions=role_perms)
            log.append(f"✅ Created: {role_name}")
        else:
            log.append(f"⚪ Exists: {role_name}")
        created_roles[role_name] = role
        await asyncio.sleep(0.3)

    verified_role  = created_roles["✅ Verified"]
    unverified_role= created_roles["❌ Unverified"]
    mod_role       = created_roles["⚔️ Mod"]
    admin_role     = created_roles["🛡️ Admin"]
    owner_role     = created_roles["👑 Owner"]
    muted_role     = created_roles["🔇 Muted"]

    log.append("\n**📁 Creating Channels...**")

    # INFORMATION category
    info_cat = discord.utils.get(guild.categories, name="📢 INFORMATION")
    if not info_cat:
        info_cat = await guild.create_category("📢 INFORMATION")
    await info_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        admin_role: discord.PermissionOverwrite(send_messages=True),
        owner_role: discord.PermissionOverwrite(send_messages=True),
        muted_role: discord.PermissionOverwrite(send_messages=False),
    })

    info_channels = ["📜-rules", "📢-announcements", "📰-updates", "🎉-events", "🌐-server-info"]
    for ch_name in info_channels:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            ch = await guild.create_text_channel(ch_name, category=info_cat)
            log.append(f"✅ #{ch_name}")
            if ch_name == "📜-rules":
                await ch.send("""@everyone **SMPIL SERVER RULES**

**1.** No XRay or texture packs that give an unfair advantage
**2.** No hacks — fly, reach, kill aura, etc.
**3.** No item duping or exploit abuse — bannable offense
**4.** Anchors and End Crystals are NOT allowed in PVP
**5.** Thorns enchantment is banned
**6.** No griefing or stealing from others (unless active war)
**7.** Minimaps are banned
**8.** Knowing/using the server seed to find structures is bannable
**9.** Don't combat log — you will die and drop your items
**10.** Respect all players — no harassment or hate speech
**11.** If recording, no hardcore texture packs and follow the server lore
**12.** Listen to staff — their decisions are final

**Punishment:** Warning → Kick → Temp Ban → Permanent Ban
**Server IP:** `SMPIL.aternos.me:50992`""")
            if ch_name == "🌐-server-info":
                info_embed = discord.Embed(
                    title="⚔️ SMPIL Minecraft Server",
                    description="Welcome to SMPIL!",
                    color=discord.Color.from_rgb(233, 69, 96)
                )
                info_embed.add_field(name="🌐 Server IP", value="`SMPIL.aternos.me`", inline=True)
                info_embed.add_field(name="🔌 Port", value="`50992`", inline=True)
                info_embed.add_field(name="📦 Version", value="Java 1.21.1", inline=True)
                info_embed.add_field(name="🎮 Type", value="SMP (Survival Multiplayer)", inline=True)
                info_embed.add_field(name="🗺️ World", value="Custom SMP World", inline=True)
                info_embed.add_field(name="⚙️ Plugins", value="Skript, EssentialsX, Vault", inline=True)
                await ch.send(embed=info_embed)

    # COMMUNITY category
    community_cat = discord.utils.get(guild.categories, name="💬 COMMUNITY")
    if not community_cat:
        community_cat = await guild.create_category("💬 COMMUNITY")
    await community_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        muted_role: discord.PermissionOverwrite(send_messages=False, speak=False),
    })
    for ch_name in ["💬-general", "💭-chat", "😂-memes", "📸-screenshots", "🎮-gameplay"]:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            await guild.create_text_channel(ch_name, category=community_cat)
            log.append(f"✅ #{ch_name}")

    # VERIFY category
    verify_cat = discord.utils.get(guild.categories, name="🔐 VERIFY")
    if not verify_cat:
        verify_cat = await guild.create_category("🔐 VERIFY")
    await verify_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        unverified_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
    })
    verify_ch = discord.utils.get(guild.text_channels, name="✅-verify")
    if not verify_ch:
        verify_ch = await guild.create_text_channel("✅-verify", category=verify_cat)
        log.append("✅ #✅-verify")
        embed = discord.Embed(
            title="🔐 SMPIL Verification",
            description="**Welcome to SMPIL!**\n\n"
                       "Click the button below to verify and get access to all channels.\n\n"
                       "After verifying you'll receive the server rules in your DMs!\n\n"
                       "**Server IP:** `SMPIL.aternos.me:50992`",
            color=discord.Color.from_rgb(233, 69, 96)
        )
        embed.set_footer(text="SMPIL • One click to get started!")
        await verify_ch.send(embed=embed, view=VerifyButton())

    # VOICE category
    voice_cat = discord.utils.get(guild.categories, name="🔊 VOICE")
    if not voice_cat:
        voice_cat = await guild.create_category("🔊 VOICE")
    await voice_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        verified_role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
        muted_role: discord.PermissionOverwrite(speak=False),
    })
    for vc_name in ["🔊 General", "⚔️ PVP Squad", "🏗️ Building", "💤 AFK"]:
        if not discord.utils.get(guild.voice_channels, name=vc_name):
            vc = await guild.create_voice_channel(vc_name, category=voice_cat)
            log.append(f"✅ 🔊 {vc_name}")
            if "AFK" in vc_name:
                try:
                    await guild.edit(afk_channel=vc, afk_timeout=300)
                except:
                    pass

    # TICKETS category
    ticket_cat = discord.utils.get(guild.categories, name="🎫 TICKETS")
    if not ticket_cat:
        ticket_cat = await guild.create_category("🎫 TICKETS")
    await ticket_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        mod_role: discord.PermissionOverwrite(view_channel=True),
        admin_role: discord.PermissionOverwrite(view_channel=True),
        owner_role: discord.PermissionOverwrite(view_channel=True),
    })
    ticket_panel_ch = discord.utils.get(guild.text_channels, name="🎫-create-ticket")
    if not ticket_panel_ch:
        ticket_panel_ch = await guild.create_text_channel("🎫-create-ticket", category=ticket_cat)
        await ticket_panel_ch.edit(overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            owner_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        })
        log.append("✅ #🎫-create-ticket")
        embed = discord.Embed(
            title="🎫 SMPIL Support Tickets",
            description="**Need help from staff?**\n\n"
                       "Select a ticket type from the dropdown below.\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━\n"
                       "🐛 Bug Report\n"
                       "💡 Suggestion\n"
                       "❓ General Help\n"
                       "👤 Report Player\n"
                       "🔨 Ban Appeal\n"
                       "⚔️ PVP Dispute\n"
                       "🎯 Other\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━\n"
                       "Staff will respond as soon as possible!",
            color=discord.Color.from_rgb(233, 69, 96)
        )
        embed.set_footer(text="SMPIL.aternos.me:50992")
        await ticket_panel_ch.send(embed=embed, view=TicketButton())

    # STAFF category
    staff_cat = discord.utils.get(guild.categories, name="🛡️ STAFF")
    if not staff_cat:
        staff_cat = await guild.create_category("🛡️ STAFF")
    await staff_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        owner_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    })
    for ch_name in ["💬-staff-chat", "📋-staff-logs", "🔨-punishments"]:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            await guild.create_text_channel(ch_name, category=staff_cat)
            log.append(f"✅ #{ch_name}")

    log.append("\n**✅ SMPIL SETUP COMPLETE!**")
    log.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    log.append("✅ 10 Roles Created")
    log.append("✅ 5 Categories Created")
    log.append("✅ 20+ Channels Created")
    log.append("✅ Verification System Active")
    log.append("✅ Ticket System Active")
    log.append("✅ Anti-Spam Active")
    log.append(f"\n**Server IP: `SMPIL.aternos.me:50992`**")

    full_log = "\n".join(log)
    embed = discord.Embed(
        title="🚀 SMPIL Server Setup Complete!",
        description=full_log[:4000],
        color=discord.Color.from_rgb(233, 69, 96)
    )
    embed.set_footer(text="SMPIL • Server Setup")
    await interaction.followup.send(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# MODERATION COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="kick", description="👢 Kick a member")
@app_commands.describe(member="Member to kick", reason="Reason")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title="👢 Member Kicked", description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**By:** {interaction.user.mention}", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Failed to kick!", ephemeral=True)

@bot.tree.command(name="ban", description="🔨 Ban a member")
@app_commands.describe(member="Member to ban", reason="Reason")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 Member Banned", description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**By:** {interaction.user.mention}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Failed to ban!", ephemeral=True)

@bot.tree.command(name="timeout", description="⏰ Timeout a member")
@app_commands.describe(member="Member to timeout", minutes="Duration in minutes", reason="Reason")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    try:
        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        embed = discord.Embed(title="⏰ Member Timed Out", description=f"**Member:** {member.mention}\n**Duration:** {minutes} minutes\n**Reason:** {reason}\n**By:** {interaction.user.mention}", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Failed!", ephemeral=True)

@bot.tree.command(name="purge", description="🧹 Delete messages")
@app_commands.describe(amount="Number of messages (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Between 1 and 100!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Deleted {len(deleted)} messages!", ephemeral=True)

@bot.tree.command(name="giverole", description="➕ Give a role to a member")
@app_commands.describe(member="Member", role="Role to give")
@app_commands.checks.has_permissions(manage_roles=True)
async def giverole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ Gave {role.mention} to {member.mention}")
    except:
        await interaction.response.send_message("❌ Failed! Make sure bot role is higher.", ephemeral=True)

@bot.tree.command(name="removerole", description="➖ Remove a role from a member")
@app_commands.describe(member="Member", role="Role to remove")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        await interaction.response.send_message(f"✅ Removed {role.mention} from {member.mention}")
    except:
        await interaction.response.send_message("❌ Failed!", ephemeral=True)

@bot.tree.command(name="sync", description="🔄 Sync slash commands")
@app_commands.checks.has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    synced = await bot.tree.sync()
    await interaction.followup.send(f"✅ Synced {len(synced)} commands! Wait 5 mins for Discord to update.", ephemeral=True)

@bot.tree.command(name="ticket", description="🎫 Send ticket panel to a channel")
@app_commands.describe(channel="Channel (default: current)")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_cmd(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not channel:
        channel = interaction.channel
    embed = discord.Embed(title="🎫 SMPIL Support", description="Select a ticket type from the dropdown below!", color=discord.Color.from_rgb(233, 69, 96))
    await channel.send(embed=embed, view=TicketButton())
    await interaction.response.send_message(f"✅ Ticket panel sent to {channel.mention}", ephemeral=True)

@bot.tree.command(name="verify", description="🔐 Send verification panel")
@app_commands.checks.has_permissions(administrator=True)
async def verify_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔐 SMPIL Verification",
        description="Click the button below to verify and get access to all channels!\n\n**Server IP:** `SMPIL.aternos.me:50992`",
        color=discord.Color.from_rgb(233, 69, 96)
    )
    await interaction.response.send_message("✅ Sent!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=VerifyButton())

@bot.tree.command(name="application", description="📝 Send staff application panel")
@app_commands.checks.has_permissions(administrator=True)
async def application_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📝 SMPIL Staff Applications",
        description="**Want to join the SMPIL staff team?**\n\n"
                   "Click Apply Now to start!\n\n"
                   "**We're looking for:**\n"
                   "• Moderators ⚔️\n"
                   "• Helpers 🤝\n\n"
                   "**Requirements:**\n"
                   "• 13+ years old\n"
                   "• Active on the server\n"
                   "• Mature and responsible",
        color=discord.Color.from_rgb(233, 69, 96)
    )
    await interaction.response.send_message("✅ Sent!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=ApplicationButton())

@bot.tree.command(name="serverip", description="🌐 Show the SMPIL server IP")
async def serverip(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ SMPIL Server IP",
        description="**Join SMPIL now!**",
        color=discord.Color.from_rgb(233, 69, 96)
    )
    embed.add_field(name="🌐 IP", value="`SMPIL.aternos.me`", inline=True)
    embed.add_field(name="🔌 Port", value="`50992`", inline=True)
    embed.add_field(name="📦 Version", value="Java 1.21.1", inline=True)
    embed.set_footer(text="See you in the server!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="📖 Show all commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ SMPIL Bot Commands",
        description="**Server IP:** `SMPIL.aternos.me:50992`",
        color=discord.Color.from_rgb(233, 69, 96)
    )
    embed.add_field(name="🚀 Setup", value="`/autosetup` - Full server setup\n`/sync` - Sync commands", inline=False)
    embed.add_field(name="🔐 Systems", value="`/verify` - Send verify panel\n`/ticket` - Send ticket panel\n`/application` - Send staff app panel", inline=False)
    embed.add_field(name="🎭 Roles", value="`/giverole` - Give role\n`/removerole` - Remove role", inline=False)
    embed.add_field(name="🛡️ Moderation", value="`/kick` `/ban` `/timeout` `/purge`", inline=False)
    embed.add_field(name="🌐 Info", value="`/serverip` - Show server IP\n`/help` - This menu", inline=False)
    embed.add_field(name="✨ Auto Features", value="✅ Anti-spam (auto-timeout)\n✅ Welcome messages\n✅ Auto unverified role on join", inline=False)
    embed.set_footer(text="SMPIL.aternos.me:50992")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission!", ephemeral=True)
    else:
        try:
            await interaction.response.send_message(f"❌ Error: {str(error)}", ephemeral=True)
        except:
            pass
        print(f"Command error: {error}")

# ═══════════════════════════════════════════════════════════════════════════════
# RUN BOT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # PUT YOUR BOT TOKEN HERE
    TOKEN = os.environ.get("DISCORD_TOKEN", "MTQ3ODg1NTk0MTEwODY2MjQyMw.GqTwFX.1HmTz1o5m9dglEJHkuYQ3L5IZqFplPJoJg0JKU")

    print("\n" + "═" * 70)
    print("⚔️  SMPIL DISCORD BOT".center(70))
    print("═" * 70)
    print("🌐 Server: SMPIL.aternos.me:50992")
    print("═" * 70 + "\n")

    keep_alive()

    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("\n❌ INVALID TOKEN! Change TOKEN in the code.\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
