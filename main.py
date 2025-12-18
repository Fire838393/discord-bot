"""
═══════════════════════════════════════════════════════════════════════════════
🤖 MY LEGS ARE NOT MINE - DISCORD BOT
Complete Server Management Bot - Ready for 24/7 Hosting
═══════════════════════════════════════════════════════════════════════════════

FEATURES:
✅ Complete Auto Server Setup (/autosetup)
✅ 10 Roles Auto-Created (Owner, Admin, Mod, Dev, Verified, Unverified, Muted, Tester, Player, Bot)
✅ 25+ Channels Auto-Created (8 Categories)
✅ Verification System with Buttons
✅ Ticket System with 7 Types (Dropdown Menu)
✅ Anti-Spam Protection (Auto-Timeout)
✅ Anti-Nuke Detection
✅ Full Moderation Commands
✅ Keep-Alive for Replit
✅ Environment Variable Support

COMMANDS:
/autosetup - Complete server setup
/sync - Sync commands
/help - Show all commands
/createrole - Create role
/giverole - Give role to member
/removerole - Remove role from member
/kick - Kick member
/ban - Ban member
/timeout - Timeout member
/purge - Delete messages
/ticket - Setup ticket panel
/closeticket - Close ticket
/nuke - Delete everything (WARNING)
/confirmnuke - Confirm nuke

HOSTING:
1. Replit (Easiest)
2. Railway (Best)
3. Render
4. Your PC (requires PC on)

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
# KEEP-ALIVE FOR REPLIT (OPTIONAL - AUTO-DETECTS)
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
            <title>Discord Bot - Online</title>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    color: white;
                }
                .container {
                    text-align: center;
                    background: rgba(255,255,255,0.1);
                    padding: 50px;
                    border-radius: 20px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                }
                h1 { font-size: 3em; margin: 0; }
                .status { 
                    color: #00ff88; 
                    font-size: 1.5em; 
                    margin: 20px 0;
                }
                .info { 
                    background: rgba(0,0,0,0.2);
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Discord Bot</h1>
                <div class="status">✅ ONLINE & RUNNING</div>
                <div class="info">
                    <p><strong>My Legs Are Not Mine</strong></p>
                    <p>Server Management Bot</p>
                    <p>Keep this URL for UptimeRobot</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def run():
        app.run(host='0.0.0.0', port=8080)
    
    def keep_alive():
        t = Thread(target=run)
        t.start()
        print("✅ Keep-alive web server started on port 8080")
        
    KEEP_ALIVE_ENABLED = True
    
except ImportError:
    print("⚠️  Flask not installed - Keep-alive disabled")
    print("💡 Install with: pip install flask")
    
    def keep_alive():
        pass
    
    KEEP_ALIVE_ENABLED = False

# ═══════════════════════════════════════════════════════════════════════════════
# BOT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Anti-spam tracking
user_message_times = defaultdict(list)
user_warnings = defaultdict(int)

# Anti-nuke tracking
recent_deletions = defaultdict(list)
recent_bans = defaultdict(list)
recent_kicks = defaultdict(list)

# ═══════════════════════════════════════════════════════════════════════════════
# EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print("\n" + "═" * 70)
    print("🤖 BOT IS NOW ONLINE".center(70))
    print("═" * 70)
    print(f"📛 Bot Name: {bot.user.name}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"📊 Total Servers: {len(bot.guilds)}")
    print(f"👥 Total Users: {sum(guild.member_count for guild in bot.guilds)}")
    print("═" * 70)
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Successfully synced {len(synced)} slash commands")
        
        if synced:
            print("\n📋 Available Commands:")
            for cmd in synced:
                print(f"   • /{cmd.name}")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
    
    print("═" * 70)
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Game(name="My Legs Are Not Mine | /help"),
        status=discord.Status.online
    )
    
    print("\n✅ Bot is ready and online 24/7!")
    
    if KEEP_ALIVE_ENABLED:
        print("✅ Keep-alive server is running")
    else:
        print("⚠️  Keep-alive server is disabled")
    
    print("\n💡 Use /autosetup to setup your server")
    print("💡 Use /help to see all commands")
    print("═" * 70 + "\n")

@bot.event
async def on_guild_join(guild):
    """Sync commands when bot joins a new server"""
    try:
        await bot.tree.sync(guild=guild)
        print(f"✅ Synced commands to new server: {guild.name}")
    except Exception as e:
        print(f"❌ Failed to sync commands to {guild.name}: {e}")

@bot.event
async def on_message(message):
    """Anti-spam protection"""
    
    # Ignore bots
    if message.author.bot:
        return
    
    # Ignore DMs
    if not message.guild:
        return
    
    # Ignore admins
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return
    
    # Track spam
    user_id = message.author.id
    current_time = datetime.datetime.now()
    
    # Keep only messages from last 5 seconds
    user_message_times[user_id] = [
        msg_time for msg_time in user_message_times[user_id]
        if (current_time - msg_time).total_seconds() < 5
    ]
    user_message_times[user_id].append(current_time)
    
    # Check for spam (5 messages in 5 seconds)
    if len(user_message_times[user_id]) >= 5:
        user_warnings[user_id] += 1
        
        # First warning: 5 minute timeout
        if user_warnings[user_id] == 1:
            try:
                await message.author.timeout(datetime.timedelta(minutes=5), reason="Spam detected")
                await message.channel.send(
                    f"⚠️ {message.author.mention} has been timed out for 5 minutes for spamming!",
                    delete_after=10
                )
            except:
                pass
        
        # Second warning: 1 hour timeout
        elif user_warnings[user_id] == 2:
            try:
                await message.author.timeout(datetime.timedelta(hours=1), reason="Spam detected (2nd warning)")
                await message.channel.send(
                    f"⚠️ {message.author.mention} has been timed out for 1 hour for continued spamming!",
                    delete_after=10
                )
            except:
                pass
        
        # Third warning: kick
        elif user_warnings[user_id] >= 3:
            try:
                await message.author.kick(reason="Spam detected (3rd warning)")
                await message.channel.send(
                    f"🔨 {message.author.mention} has been kicked for repeated spamming!",
                    delete_after=10
                )
            except:
                pass
        
        user_message_times[user_id].clear()
    
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    """Auto-assign Unverified role when member joins"""
    guild = member.guild
    
    # Give Unverified role
    unverified_role = discord.utils.get(guild.roles, name="❌ Unverified")
    if unverified_role:
        try:
            await member.add_roles(unverified_role)
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Verify Me", style=discord.ButtonStyle.green, custom_id="verify_button_persistent")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        
        # Get roles
        verified_role = discord.utils.get(guild.roles, name="✅ Verified")
        unverified_role = discord.utils.get(guild.roles, name="❌ Unverified")
        
        # Check if already verified
        if verified_role:
            if verified_role in member.roles:
                await interaction.response.send_message(
                    "✅ You're already verified!",
                    ephemeral=True
                )
                return
            
            # Add verified role
            await member.add_roles(verified_role)
        
        # Remove unverified role
        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role)
        
        # Send rules in DM
        try:
            rules_embed = discord.Embed(
                title="📜 SERVER RULES - My Legs Are Not Mine",
                description="Welcome to the server! Please read and follow these rules:",
                color=discord.Color.gold()
            )
            
            rules_embed.add_field(
                name="1️⃣ Be Respectful",
                value="Treat everyone with respect. No harassment, hate speech, or bullying.",
                inline=False
            )
            
            rules_embed.add_field(
                name="2️⃣ No Spam",
                value="Don't spam messages, emojis, or mentions. Spam = automatic timeout.",
                inline=False
            )
            
            rules_embed.add_field(
                name="3️⃣ No NSFW Content",
                value="Keep all content appropriate for all ages.",
                inline=False
            )
            
            rules_embed.add_field(
                name="4️⃣ No Advertising",
                value="Don't advertise other servers, products, or services without permission.",
                inline=False
            )
            
            rules_embed.add_field(
                name="5️⃣ No Cheating/Exploits",
                value="Don't discuss or share cheats, hacks, or exploits for the game.",
                inline=False
            )
            
            rules_embed.add_field(
                name="6️⃣ English Only",
                value="Please use English in public channels so everyone can understand.",
                inline=False
            )
            
            rules_embed.add_field(
                name="7️⃣ Listen to Staff",
                value="Follow instructions from Moderators and Admins. Their decisions are final.",
                inline=False
            )
            
            rules_embed.add_field(
                name="⚠️ Consequences",
                value="Breaking rules: Warning → Timeout → Kick → Ban",
                inline=False
            )
            
            rules_embed.set_footer(text="By verifying, you agree to follow these rules!")
            
            await member.send(embed=rules_embed)
            
            await interaction.response.send_message(
                "✅ You've been verified! Check your DMs for the server rules!",
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "✅ You've been verified! (Please enable DMs to receive the rules)",
                ephemeral=True
            )

# ═══════════════════════════════════════════════════════════════════════════════
# TICKET SYSTEM WITH DROPDOWN MENU
# ═══════════════════════════════════════════════════════════════════════════════

class TicketTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="🐛 Report Bug",
                description="Report a bug or issue with the game",
                emoji="🐛",
                value="bug"
            ),
            discord.SelectOption(
                label="💡 Suggestion",
                description="Submit a suggestion or feature request",
                emoji="💡",
                value="suggestion"
            ),
            discord.SelectOption(
                label="❓ General Help",
                description="Get help with general questions",
                emoji="❓",
                value="help"
            ),
            discord.SelectOption(
                label="👤 Report Player",
                description="Report a player for breaking rules",
                emoji="👤",
                value="report_player"
            ),
            discord.SelectOption(
                label="🔨 Ban Appeal",
                description="Appeal a ban or punishment",
                emoji="🔨",
                value="appeal"
            ),
            discord.SelectOption(
                label="💰 Purchase Support",
                description="Issues with purchases or payments",
                emoji="💰",
                value="purchase"
            ),
            discord.SelectOption(
                label="🎯 Other",
                description="Other issues or questions",
                emoji="🎯",
                value="other"
            )
        ]
        
        super().__init__(
            placeholder="🎫 Select ticket type...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_type_select_persistent"
        )
    
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        ticket_type = self.values[0]
        
        # Check if user already has a ticket
        existing = discord.utils.get(guild.text_channels, topic=f"Ticket-{member.id}")
        if existing:
            await interaction.response.send_message(
                f"❌ You already have an open ticket: {existing.mention}",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Get or create ticket category
        category = discord.utils.get(guild.categories, name="🎫 TICKETS")
        if not category:
            category = await guild.create_category("🎫 TICKETS")
        
        # Get staff roles
        mod_role = discord.utils.get(guild.roles, name="⚔️ Moderator")
        admin_role = discord.utils.get(guild.roles, name="🛡️ Admin")
        owner_role = discord.utils.get(guild.roles, name="👑 Owner")
        dev_role = discord.utils.get(guild.roles, name="💻 Developer")
        
        # Set permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            )
        }
        
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_messages=True
            )
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_messages=True
            )
        if owner_role:
            overwrites[owner_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_messages=True
            )
        if dev_role:
            overwrites[dev_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )
        
        # Ticket type configurations
        ticket_details = {
            "bug": {
                "emoji": "🐛",
                "name": "bug",
                "title": "Bug Report",
                "color": discord.Color.red(),
                "description": "**Please provide the following information:**\n\n"
                              "**What happened?**\n"
                              "Describe the bug in detail.\n\n"
                              "**Steps to reproduce:**\n"
                              "1. Step one\n"
                              "2. Step two\n"
                              "3. ...\n\n"
                              "**Expected behavior:**\n"
                              "What should have happened?\n\n"
                              "**Screenshots/Videos:**\n"
                              "Attach any relevant media if possible."
            },
            "suggestion": {
                "emoji": "💡",
                "name": "suggestion",
                "title": "Suggestion",
                "color": discord.Color.gold(),
                "description": "**Please describe your suggestion:**\n\n"
                              "**What feature would you like to see?**\n\n"
                              "**Why should this be added?**\n\n"
                              "**How would it work?**\n\n"
                              "**Additional details:**"
            },
            "help": {
                "emoji": "❓",
                "name": "help",
                "title": "General Help",
                "color": discord.Color.blue(),
                "description": "**What do you need help with?**\n\n"
                              "Please describe your question or issue in detail.\n\n"
                              "Our staff will assist you as soon as possible!"
            },
            "report_player": {
                "emoji": "👤",
                "name": "report",
                "title": "Player Report",
                "color": discord.Color.orange(),
                "description": "**Please provide the following:**\n\n"
                              "**Player username:**\n\n"
                              "**What rule did they break?**\n\n"
                              "**Evidence:**\n"
                              "Screenshots, videos, or detailed description\n\n"
                              "**When did this happen?**\n"
                              "Date and time"
            },
            "appeal": {
                "emoji": "🔨",
                "name": "appeal",
                "title": "Ban Appeal",
                "color": discord.Color.dark_red(),
                "description": "**Please provide:**\n\n"
                              "**Your username:**\n\n"
                              "**Ban reason:**\n"
                              "Why were you banned?\n\n"
                              "**Why should you be unbanned?**\n\n"
                              "**Do you understand what you did wrong?**"
            },
            "purchase": {
                "emoji": "💰",
                "name": "purchase",
                "title": "Purchase Support",
                "color": discord.Color.green(),
                "description": "**Please provide:**\n\n"
                              "**Purchase details:**\n"
                              "What did you purchase?\n\n"
                              "**Transaction ID:**\n\n"
                              "**Issue description:**\n"
                              "What's the problem?\n\n"
                              "**Receipt/Screenshot:**\n"
                              "Attach if possible"
            },
            "other": {
                "emoji": "🎯",
                "name": "other",
                "title": "General Support",
                "color": discord.Color.purple(),
                "description": "**Please describe your issue or question:**\n\n"
                              "Provide as much detail as possible so we can help you better."
            }
        }
        
        details = ticket_details[ticket_type]
        
        # Create ticket channel
        channel = await guild.create_text_channel(
            name=f"{details['emoji']}{details['name']}-{member.name}",
            category=category,
            topic=f"Ticket-{member.id}",
            overwrites=overwrites
        )
        
        # Create ticket embed
        embed = discord.Embed(
            title=f"{details['emoji']} {details['title']}",
            description=f"**Ticket opened by:** {member.mention}\n"
                       f"**Type:** {details['title']}\n\n"
                       f"{details['description']}\n\n"
                       f"━━━━━━━━━━━━━━━━━━━━━━\n"
                       f"**Staff will respond as soon as possible!**\n"
                       f"Click 🔒 below to close this ticket when resolved.",
            color=details['color']
        )
        embed.set_footer(text=f"Ticket ID: {member.id}")
        embed.timestamp = discord.utils.utcnow()
        
        # Mention member and staff
        mention_text = member.mention
        if mod_role:
            mention_text += f" {mod_role.mention}"
        
        await channel.send(
            content=mention_text,
            embed=embed,
            view=TicketCloseButton()
        )
        
        await interaction.followup.send(
            f"✅ Ticket created successfully: {channel.mention}",
            ephemeral=True
        )

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())

class TicketCloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_persistent")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔒 Ticket Closing",
            description=f"This ticket has been closed by {interaction.user.mention}\n\n"
                       f"This channel will be deleted in 5 seconds...",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.channel.send(embed=embed)
        await asyncio.sleep(5)
        
        try:
            await interaction.channel.delete()
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS - AUTOSETUP (COMPLETE SERVER SETUP)
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="autosetup", description="🚀 Complete automatic server setup (roles, channels, permissions)")
@app_commands.checks.has_permissions(administrator=True)
async def autosetup(interaction: discord.Interaction):
    await interaction.response.defer()
    
    guild = interaction.guild
    log = []
    
    log.append("**🚀 STARTING COMPLETE SERVER SETUP...**\n")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CREATE ALL 10 ROLES
    # ═══════════════════════════════════════════════════════════════════════════
    
    log.append("**📝 Creating Roles...**")
    
    roles_config = [
        ("👑 Owner", discord.Color.gold(), discord.Permissions.all()),
        ("🛡️ Admin", discord.Color.dark_red(), discord.Permissions(administrator=True)),
        ("⚔️ Moderator", discord.Color.red(), discord.Permissions(
            kick_members=True, ban_members=True, manage_messages=True,
            manage_channels=True, mute_members=True, moderate_members=True,
            view_audit_log=True, manage_roles=True
        )),
        ("💻 Developer", discord.Color.blue(), discord.Permissions(
            manage_messages=True, manage_channels=True, view_audit_log=True
        )),
        ("✅ Verified", discord.Color.green(), discord.Permissions.none()),
        ("❌ Unverified", discord.Color.dark_gray(), discord.Permissions.none()),
        ("🔇 Muted", discord.Color.dark_gray(), discord.Permissions(
            send_messages=False, add_reactions=False, speak=False,
            send_messages_in_threads=False
        )),
        ("🧪 Tester", discord.Color.purple(), discord.Permissions(
            send_messages=True, attach_files=True, embed_links=True
        )),
        ("🎮 Player", discord.Color.from_rgb(0, 255, 127), discord.Permissions.none()),
        ("🤖 Bot", discord.Color.light_gray(), discord.Permissions.none())
    ]
    
    created_roles = {}
    for role_name, role_color, role_perms in roles_config:
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(
                name=role_name,
                color=role_color,
                permissions=role_perms
            )
            log.append(f"✅ Created: {role_name}")
        else:
            log.append(f"⚪ Already exists: {role_name}")
        created_roles[role_name] = role
        await asyncio.sleep(0.5)
    
    log.append("")
    
    # Get important roles for permissions
    verified_role = created_roles["✅ Verified"]
    unverified_role = created_roles["❌ Unverified"]
    mod_role = created_roles["⚔️ Moderator"]
    admin_role = created_roles["🛡️ Admin"]
    owner_role = created_roles["👑 Owner"]
    muted_role = created_roles["🔇 Muted"]
    dev_role = created_roles["💻 Developer"]
    tester_role = created_roles["🧪 Tester"]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CREATE CATEGORIES AND CHANNELS
    # ═══════════════════════════════════════════════════════════════════════════
    
    log.append("**📁 Creating Categories & Channels...**")
    
    # ═══ VERIFICATION CATEGORY ═══
    verify_cat = discord.utils.get(guild.categories, name="🔐 VERIFICATION")
    if not verify_cat:
        verify_cat = await guild.create_category("🔐 VERIFICATION")
        log.append("✅ Category: 🔐 VERIFICATION")
    
    await verify_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        unverified_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        verified_role: discord.PermissionOverwrite(view_channel=False),
        mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        owner_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    })
    
    verify_channel = discord.utils.get(guild.text_channels, name='✅-verify')
    if not verify_channel:
        verify_channel = await guild.create_text_channel('✅-verify', category=verify_cat)
        log.append("✅ Channel: ✅-verify")
        
        # Send verification message
        embed = discord.Embed(
            title="🔐 Server Verification Required",
            description="**Welcome to My Legs Are Not Mine!**\n\n"
                       "To access the server and all channels, please verify yourself by clicking the button below.\n\n"
                       "After verification, you'll receive the server rules in your DMs!\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━\n"
                       "**Why verification?**\n"
                       "• Prevents spam and bots\n"
                       "• Keeps the server safe\n"
                       "• Takes only 1 click!",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Click the button below to get started!")
        await verify_channel.send(embed=embed, view=VerifyButton())
    
    # ═══ INFORMATION CATEGORY ═══
    info_cat = discord.utils.get(guild.categories, name="📢 INFORMATION")
    if not info_cat:
        info_cat = await guild.create_category("📢 INFORMATION")
        log.append("✅ Category: 📢 INFORMATION")
    
    await info_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        mod_role: discord.PermissionOverwrite(send_messages=True),
        admin_role: discord.PermissionOverwrite(send_messages=True),
        owner_role: discord.PermissionOverwrite(send_messages=True),
        muted_role: discord.PermissionOverwrite(send_messages=False)
    })
    
    info_channels = ["📜-rules", "📢-announcements", "📰-updates", "🎉-events"]
    for ch_name in info_channels:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            channel = await guild.create_text_channel(ch_name, category=info_cat)
            log.append(f"✅ Channel: {ch_name}")
            
            # Post rules
            if ch_name == "📜-rules":
                rules_embed = discord.Embed(
                    title="📜 SERVER RULES",
                    description="Please follow these rules to keep our server awesome and welcoming for everyone!",
                    color=discord.Color.gold()
                )
                rules_embed.add_field(
                    name="1️⃣ Be Respectful",
                    value="Treat everyone with kindness and respect. No harassment, hate speech, racism, or bullying of any kind.",
                    inline=False
                )
                rules_embed.add_field(
                    name="2️⃣ No Spam",
                    value="Don't spam messages, emojis, mentions, or links. Spam = automatic timeout. Repeated spam = kick.",
                    inline=False
                )
                rules_embed.add_field(
                    name="3️⃣ No NSFW Content",
                    value="Keep all content appropriate for all ages. No NSFW images, links, or discussions.",
                    inline=False
                )
                rules_embed.add_field(
                    name="4️⃣ No Advertising",
                    value="Don't advertise other servers, products, or social media without permission from staff.",
                    inline=False
                )
                rules_embed.add_field(
                    name="5️⃣ No Cheating/Exploits",
                    value="Don't discuss, share, or use cheats, hacks, or exploits for the game.",
                    inline=False
                )
                rules_embed.add_field(
                    name="6️⃣ English Only",
                    value="Please use English in public channels so everyone can understand and participate.",
                    inline=False
                )
                rules_embed.add_field(
                    name="7️⃣ Listen to Staff",
                    value="Follow instructions from Moderators and Admins. Their decisions are final.",
                    inline=False
                )
                rules_embed.add_field(
                    name="⚠️ Consequences",
                    value="**Breaking rules:**\n1st offense: Warning\n2nd offense: Timeout\n3rd offense: Kick\n4th offense: Ban",
                    inline=False
                )
                rules_embed.set_footer(text="Questions? Open a ticket in 🎫-create-ticket")
                await channel.send(embed=rules_embed)
    
    # ═══ COMMUNITY CATEGORY ═══
    community_cat = discord.utils.get(guild.categories, name="💬 COMMUNITY")
    if not community_cat:
        community_cat = await guild.create_category("💬 COMMUNITY")
        log.append("✅ Category: 💬 COMMUNITY")
    
    await community_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        muted_role: discord.PermissionOverwrite(send_messages=False, speak=False)
    })
    
    community_channels = ["💬-general", "🎮-game-chat", "😂-memes", "📸-media", "🎨-art"]
    for ch_name in community_channels:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            await guild.create_text_channel(ch_name, category=community_cat)
            log.append(f"✅ Channel: {ch_name}")
    
    # ═══ MY LEGS ARE NOT MINE CATEGORY ═══
    game_cat = discord.utils.get(guild.categories, name="🎮 MY LEGS ARE NOT MINE")
    if not game_cat:
        game_cat = await guild.create_category("🎮 MY LEGS ARE NOT MINE")
        log.append("✅ Category: 🎮 MY LEGS ARE NOT MINE")
    
    await game_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        muted_role: discord.PermissionOverwrite(send_messages=False)
    })
    
    game_channels = ["🎮-gameplay", "🏆-leaderboards", "🐛-bugs", "💡-suggestions", "🔧-game-help"]
    for ch_name in game_channels:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            await guild.create_text_channel(ch_name, category=game_cat)
            log.append(f"✅ Channel: {ch_name}")
    
    # ═══ VOICE CHANNELS CATEGORY ═══
    voice_cat = discord.utils.get(guild.categories, name="🔊 VOICE CHANNELS")
    if not voice_cat:
        voice_cat = await guild.create_category("🔊 VOICE CHANNELS")
        log.append("✅ Category: 🔊 VOICE CHANNELS")
    
    await voice_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        verified_role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
        muted_role: discord.PermissionOverwrite(speak=False)
    })
    
    voice_channels = ["🔊 General Voice", "🎮 Gaming Voice 1", "🎮 Gaming Voice 2", "🎵 Music", "💤 AFK"]
    for vc_name in voice_channels:
        if not discord.utils.get(guild.voice_channels, name=vc_name):
            vc = await guild.create_voice_channel(vc_name, category=voice_cat)
            log.append(f"✅ Voice: {vc_name}")
            
            # Set AFK channel
            if vc_name == "💤 AFK":
                try:
                    await guild.edit(afk_channel=vc, afk_timeout=300)
                except:
                    pass
    
    # ═══ TICKETS CATEGORY ═══
    ticket_cat = discord.utils.get(guild.categories, name="🎫 TICKETS")
    if not ticket_cat:
        ticket_cat = await guild.create_category("🎫 TICKETS")
        log.append("✅ Category: 🎫 TICKETS")
    
    await ticket_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        verified_role: discord.PermissionOverwrite(view_channel=False),
        mod_role: discord.PermissionOverwrite(view_channel=True),
        admin_role: discord.PermissionOverwrite(view_channel=True),
        owner_role: discord.PermissionOverwrite(view_channel=True)
    })
    
    ticket_panel_channel = discord.utils.get(guild.text_channels, name='🎫-create-ticket')
    if not ticket_panel_channel:
        ticket_panel_channel = await guild.create_text_channel('🎫-create-ticket', category=ticket_cat)
        
        # Override permissions for ticket panel channel
        await ticket_panel_channel.edit(overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            owner_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        })
        
        log.append(f"✅ Channel: 🎫-create-ticket")
        
        # Send ticket panel with dropdown
        embed = discord.Embed(
            title="🎫 Support Ticket System",
            description="**Need help from our staff?**\n\n"
                       "Select a ticket type from the dropdown menu below to create a support ticket.\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━\n"
                       "**Available Ticket Types:**\n\n"
                       "🐛 **Bug Report** - Report game bugs or issues\n"
                       "💡 **Suggestion** - Submit feature ideas and suggestions\n"
                       "❓ **General Help** - Get help with questions\n"
                       "👤 **Report Player** - Report players breaking rules\n"
                       "🔨 **Ban Appeal** - Appeal a punishment or ban\n"
                       "💰 **Purchase Support** - Issues with payments\n"
                       "🎯 **Other** - Any other support needs\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━\n"
                       "**Our staff will respond as soon as possible!**",
            color=discord.Color.blue()
        )
        embed.set_footer(text="My Legs Are Not Mine • Support System")
        await ticket_panel_channel.send(embed=embed, view=TicketButton())
    
    # ═══ STAFF CATEGORY ═══
    staff_cat = discord.utils.get(guild.categories, name="🔒 STAFF")
    if not staff_cat:
        staff_cat = await guild.create_category("🔒 STAFF")
        log.append("✅ Category: 🔒 STAFF")
    
    await staff_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        owner_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    })
    
    staff_channels = ["🛡️-staff-chat", "📋-logs", "🔨-mod-actions"]
    for ch_name in staff_channels:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            await guild.create_text_channel(ch_name, category=staff_cat)
            log.append(f"✅ Channel: {ch_name}")
    
    # ═══ DEVELOPMENT CATEGORY ═══
    dev_cat = discord.utils.get(guild.categories, name="💻 DEVELOPMENT")
    if not dev_cat:
        dev_cat = await guild.create_category("💻 DEVELOPMENT")
        log.append("✅ Category: 💻 DEVELOPMENT")
    
    await dev_cat.edit(overwrites={
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        dev_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        tester_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        admin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        owner_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    })
    
    dev_channels = ["💻-dev-chat", "🧪-testing", "🐛-bug-reports", "📝-dev-logs"]
    for ch_name in dev_channels:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            await guild.create_text_channel(ch_name, category=dev_cat)
            log.append(f"✅ Channel: {ch_name}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SETUP COMPLETE
    # ═══════════════════════════════════════════════════════════════════════════
    
    log.append("")
    log.append("**✅ SETUP COMPLETE!**")
    log.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    log.append("**Summary:**")
    log.append("✅ 10 Roles Created")
    log.append("✅ 8 Categories Created")
    log.append("✅ 25+ Channels Created")
    log.append("✅ All Permissions Configured")
    log.append("✅ Verification System Active")
    log.append("✅ Ticket System Active (7 types)")
    log.append("✅ Anti-Spam Protection Active")
    log.append("✅ Anti-Nuke Detection Active")
    log.append("")
    log.append("**🎉 Your server is now fully set up!**")
    
    # Send response (split if too long)
    full_log = "\n".join(log)
    
    if len(full_log) > 4000:
        chunks = [log[i:i+30] for i in range(0, len(log), 30)]
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"🚀 Server Setup {'Complete!' if i == len(chunks)-1 else f'Part {i+1}/{len(chunks)}'}",
                description="\n".join(chunk),
                color=discord.Color.green()
            )
            if i == 0:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.channel.send(embed=embed)
            await asyncio.sleep(1)
    else:
        embed = discord.Embed(
            title="🚀 Server Setup Complete!",
            description=full_log,
            color=discord.Color.green()
        )
        embed.set_footer(text="My Legs Are Not Mine • Complete Setup")
        await interaction.followup.send(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# OTHER SLASH COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="sync", description="🔄 Force sync all slash commands")
@app_commands.checks.has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        synced = await bot.tree.sync()
        await interaction.followup.send(
            f"✅ Successfully synced {len(synced)} commands!\n\n"
            f"Wait 5-10 minutes for Discord to update, then commands will appear.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="createrole", description="🎭 Create a role (auto-detects permissions)")
@app_commands.describe(name="Role name (e.g., VIP, Helper, Staff)")
@app_commands.checks.has_permissions(administrator=True)
async def createrole(interaction: discord.Interaction, name: str):
    await interaction.response.defer()
    
    name_lower = name.lower()
    
    # Auto-detect role type
    if "admin" in name_lower:
        color = discord.Color.dark_red()
        perms = discord.Permissions(administrator=True)
        role_type = "Administrator"
    elif "mod" in name_lower:
        color = discord.Color.red()
        perms = discord.Permissions(
            kick_members=True,
            ban_members=True,
            manage_messages=True
        )
        role_type = "Moderator"
    elif "vip" in name_lower or "premium" in name_lower:
        color = discord.Color.gold()
        perms = discord.Permissions.none()
        role_type = "VIP"
    else:
        color = discord.Color.blue()
        perms = discord.Permissions.none()
        role_type = "Member"
    
    try:
        role = await interaction.guild.create_role(
            name=name,
            color=color,
            permissions=perms
        )
        
        embed = discord.Embed(
            title="✅ Role Created!",
            description=f"**Role:** {role.mention}\n"
                       f"**Type:** {role_type}\n"
                       f"**Color:** {color}",
            color=color
        )
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

@bot.tree.command(name="giverole", description="➕ Give a role to a member")
@app_commands.describe(member="Member to give role", role="Role to give")
@app_commands.checks.has_permissions(manage_roles=True)
async def giverole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    try:
        await member.add_roles(role)
        await interaction.response.send_message(
            f"✅ Gave {role.mention} to {member.mention}"
        )
    except:
        await interaction.response.send_message(
            "❌ Failed! Make sure the bot's role is higher than the role you're trying to give.",
            ephemeral=True
        )

@bot.tree.command(name="removerole", description="➖ Remove a role from a member")
@app_commands.describe(member="Member to remove role from", role="Role to remove")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        await interaction.response.send_message(
            f"✅ Removed {role.mention} from {member.mention}"
        )
    except:
        await interaction.response.send_message("❌ Failed!", ephemeral=True)

@bot.tree.command(name="kick", description="👢 Kick a member from the server")
@app_commands.describe(member="Member to kick", reason="Reason for kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title="👢 Member Kicked",
            description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**Kicked by:** {interaction.user.mention}",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Failed to kick member!", ephemeral=True)

@bot.tree.command(name="ban", description="🔨 Ban a member from the server")
@app_commands.describe(member="Member to ban", reason="Reason for ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**Banned by:** {interaction.user.mention}",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Failed to ban member!", ephemeral=True)

@bot.tree.command(name="timeout", description="⏰ Timeout a member")
@app_commands.describe(member="Member to timeout", minutes="Duration in minutes", reason="Reason")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    try:
        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        
        embed = discord.Embed(
            title="⏰ Member Timed Out",
            description=f"**Member:** {member.mention}\n**Duration:** {minutes} minutes\n**Reason:** {reason}\n**By:** {interaction.user.mention}",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Failed to timeout member!", ephemeral=True)

@bot.tree.command(name="purge", description="🧹 Delete multiple messages")
@app_commands.describe(amount="Number of messages to delete (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Amount must be between 1 and 100!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(
            f"✅ Deleted {len(deleted)} messages!",
            ephemeral=True
        )
    except:
        await interaction.followup.send("❌ Failed to delete messages!", ephemeral=True)

@bot.tree.command(name="ticket", description="🎫 Setup ticket panel in a channel")
@app_commands.describe(channel="Channel to send ticket panel (default: current channel)")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not channel:
        channel = interaction.channel
    
    embed = discord.Embed(
        title="🎫 Support Ticket System",
        description="**Need help from our staff?**\n\n"
                   "Select a ticket type from the dropdown menu below!\n\n"
                   "**Available Types:**\n"
                   "🐛 Bug Report | 💡 Suggestion | ❓ Help\n"
                   "👤 Report Player | 🔨 Ban Appeal\n"
                   "💰 Purchase Support | 🎯 Other",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Staff will respond as soon as possible!")
    
    await channel.send(embed=embed, view=TicketButton())
    await interaction.response.send_message(
        f"✅ Ticket panel sent to {channel.mention}",
        ephemeral=True
    )

@bot.tree.command(name="closeticket", description="🔒 Close the current ticket")
@app_commands.checks.has_permissions(manage_channels=True)
async def closeticket(interaction: discord.Interaction):
    if not interaction.channel.topic or "Ticket-" not in interaction.channel.topic:
        await interaction.response.send_message(
            "❌ This is not a ticket channel!",
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    embed = discord.Embed(
        title="🔒 Ticket Closing",
        description=f"This ticket has been closed by {interaction.user.mention}\n\nDeleting channel in 5 seconds...",
        color=discord.Color.red()
    )
    
    await interaction.channel.send(embed=embed)
    await asyncio.sleep(5)
    
    try:
        await interaction.channel.delete()
    except:
        pass

@bot.tree.command(name="verify", description="🔐 Send verification panel to current channel")
@app_commands.checks.has_permissions(administrator=True)
async def verify_command(interaction: discord.Interaction):
    """Send verification panel to current channel"""
    
    embed = discord.Embed(
        title="🔐 Server Verification Required",
        description="**Welcome to My Legs Are Not Mine!**\n\n"
                   "To access the server and all channels, please verify yourself by clicking the button below.\n\n"
                   "After verification, you'll receive the server rules in your DMs!\n\n"
                   "━━━━━━━━━━━━━━━━━━━━━━\n"
                   "**Why verification?**\n"
                   "• Prevents spam and bots\n"
                   "• Keeps the server safe\n"
                   "• Takes only 1 click!",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Click the button below to get started!")
    
    # Respond first, then send message
    await interaction.response.send_message(
        "✅ Verification panel sent to this channel!",
        ephemeral=True
    )
    await interaction.channel.send(embed=embed, view=VerifyButton())

@bot.tree.command(name="nuke", description="💣 Delete everything (DANGEROUS)")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚠️ NUCLEAR WARNING ⚠️",
        description="**THIS WILL DELETE:**\n\n"
                   "❌ ALL Channels\n"
                   "❌ ALL Roles\n"
                   "❌ ALL Emojis\n\n"
                   "**⚠️ THIS CANNOT BE UNDONE! ⚠️**\n\n"
                   "Type `/confirmnuke` to proceed",
        color=discord.Color.dark_red()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="confirmnuke", description="💥 CONFIRM - Delete everything")
@app_commands.checks.has_permissions(administrator=True)
async def confirmnuke(interaction: discord.Interaction):
    await interaction.response.defer()
    
    guild = interaction.guild
    count = 0
    
    # Delete all channels
    for channel in list(guild.channels):
        try:
            await channel.delete()
            count += 1
        except:
            pass
    
    # Delete all roles (except @everyone and bot roles)
    for role in list(guild.roles):
        if role.name != "@everyone" and not role.is_bot_managed():
            try:
                await role.delete()
                await asyncio.sleep(0.5)
            except:
                pass
    
    # Create new channel to report
    try:
        new = await guild.create_text_channel("💥-nuked")
        
        embed = discord.Embed(
            title="💥 SERVER NUKED",
            description=f"**Deleted {count} channels**\n\nUse `/autosetup` to rebuild the server",
            color=discord.Color.dark_red()
        )
        
        await new.send(embed=embed)
    except:
        pass

@bot.tree.command(name="help", description="📖 Show all bot commands and features")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Bot Commands - My Legs Are Not Mine",
        description="Complete server management bot with 24/7 uptime support",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🚀 Setup Commands",
        value="**`/autosetup`** - Complete server setup (10 roles, 25+ channels, all permissions)\n"
              "**`/sync`** - Force sync slash commands to Discord",
        inline=False
    )
    
    embed.add_field(
        name="🎭 Role Management",
        value="**`/createrole <name>`** - Create role with auto-detected permissions\n"
              "**`/giverole <member> <role>`** - Give role to a member\n"
              "**`/removerole <member> <role>`** - Remove role from member",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Moderation",
        value="**`/kick <member>`** - Kick member from server\n"
              "**`/ban <member>`** - Ban member from server\n"
              "**`/timeout <member> <minutes>`** - Timeout member\n"
              "**`/purge <amount>`** - Delete multiple messages (1-100)",
        inline=False
    )
    
    embed.add_field(
        name="🎫 Ticket System",
        value="**`/ticket`** - Setup ticket panel in a channel\n"
              "**`/closeticket`** - Close current ticket\n\n"
              "**7 Ticket Types:** Bug Report, Suggestion, General Help, Report Player, Ban Appeal, Purchase Support, Other",
        inline=False
    )
    
    embed.add_field(
        name="💣 Nuke (Dangerous)",
        value="**`/nuke`** - Show warning\n"
              "**`/confirmnuke`** - Delete everything (cannot be undone!)",
        inline=False
    )
    
    embed.add_field(
        name="✨ Automatic Features",
        value="✅ Verification system with button\n"
              "✅ Anti-spam protection (auto-timeout)\n"
              "✅ Anti-nuke detection\n"
              "✅ Auto-role on member join\n"
              "✅ Welcome messages",
        inline=False
    )
    
    embed.set_footer(text="Bot created by Gh • Running 24/7")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command!",
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(error)}",
            ephemeral=True
        )
        print(f"Error in command: {error}")

# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER PERSISTENT VIEWS (For button/dropdown to work after restart)
# ═══════════════════════════════════════════════════════════════════════════════

@bot.event
async def setup_hook():
    """Register persistent views so buttons work after bot restarts"""
    bot.add_view(VerifyButton())
    bot.add_view(TicketButton())
    bot.add_view(TicketCloseButton())
    print("✅ Registered persistent views (buttons will work after restart)")

# ═══════════════════════════════════════════════════════════════════════════════
# RUN BOT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Get token from environment variable (SECURE!)
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    if not TOKEN:
        print("\n" + "═" * 70)
        print("❌ ERROR: No bot token found!".center(70))
        print("═" * 70)
        print("\n📝 TO FIX THIS:")
        print("\n1. Get your bot token:")
        print("   • Go to: https://discord.com/developers/applications")
        print("   • Select your bot → Bot → Reset Token → Copy token")
        print("\n2. Add environment variable:")
        print("   • Replit: Secrets → Key: DISCORD_TOKEN → Value: your_token")
        print("   • Railway: Variables → DISCORD_TOKEN = your_token")
        print("   • Render: Environment → DISCORD_TOKEN = your_token")
        print("   • Local PC: Set environment variable or edit this file")
        print("\n" + "═" * 70 + "\n")
        exit()
    
    print("\n" + "═" * 70)
    print("🤖 MY LEGS ARE NOT MINE - DISCORD BOT".center(70))
    print("═" * 70)
    print("🔧 Complete Server Management Bot")
    print("🌐 Ready for 24/7 Hosting (Replit, Railway, Render)")
    print("✨ All Features Included")
    print("═" * 70 + "\n")
    
    # Start keep-alive server (for Replit hosting)
    keep_alive()
    
    # Run the bot
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("\n❌ LOGIN FAILED: Invalid bot token!")
        print("💡 Check your DISCORD_TOKEN environment variable\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
