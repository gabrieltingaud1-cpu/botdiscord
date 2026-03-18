import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import os

# ══════════════════════════════════════════
#   CONFIG — token chargé depuis .env
# ══════════════════════════════════════════
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ══════════════════════════════════════════
#   STRUCTURE DU SERVEUR
# ══════════════════════════════════════════
STRUCTURE = [
    {
        "categorie": "📢 INFORMATIONS",
        "salons": [
            {"nom": "📜│règles",          "type": "texte", "desc": "Règles du serveur"},
            {"nom": "📣│annonces",         "type": "texte", "desc": "Annonces importantes"},
            {"nom": "👋│bienvenue",        "type": "texte", "desc": "Accueil des nouveaux membres"},
            {"nom": "🎭│rôles",            "type": "texte", "desc": "Choisis tes rôles ici"},
        ]
    },
    {
        "categorie": "💬 GÉNÉRAL",
        "salons": [
            {"nom": "💬│général",          "type": "texte", "desc": "Discussion générale"},
            {"nom": "😂│memes",            "type": "texte", "desc": "Partage tes memes"},
            {"nom": "📸│médias",           "type": "texte", "desc": "Photos, vidéos, captures"},
            {"nom": "🎵│musique",          "type": "texte", "desc": "Partage ta musique"},
            {"nom": "🔊│vocal-général",    "type": "vocal"},
            {"nom": "🎙️│détente",          "type": "vocal"},
        ]
    },
    {
        "categorie": "🎮 GAMING",
        "salons": [
            {"nom": "🎮│gaming-général",   "type": "texte", "desc": "Tout sur le gaming"},
            {"nom": "🚀│rocket-league",    "type": "texte", "desc": "Rocket League"},
            {"nom": "🏆│fortnite",         "type": "texte", "desc": "Fortnite"},
            {"nom": "🔫│fps",              "type": "texte", "desc": "CS2, Valorant, etc."},
            {"nom": "⚔️│rpg-aventure",     "type": "texte", "desc": "RPG et jeux d'aventure"},
            {"nom": "🎯│recherche-joueurs", "type": "texte", "desc": "LFG — cherche des coéquipiers"},
            {"nom": "🎮│gaming-vocal",     "type": "vocal"},
            {"nom": "🕹️│gaming-vocal-2",   "type": "vocal"},
        ]
    },
    {
        "categorie": "💻 CODE & TECH",
        "salons": [
            {"nom": "💻│code-général",     "type": "texte", "desc": "Programmation générale"},
            {"nom": "🐍│python",           "type": "texte", "desc": "Python"},
            {"nom": "🟨│javascript",       "type": "texte", "desc": "JavaScript / TypeScript"},
            {"nom": "🌐│web",              "type": "texte", "desc": "HTML, CSS, frameworks web"},
            {"nom": "🤖│ia-ml",            "type": "texte", "desc": "Intelligence artificielle & ML"},
            {"nom": "🛠️│projets",          "type": "texte", "desc": "Montre tes projets"},
            {"nom": "❓│aide-code",         "type": "texte", "desc": "Pose tes questions de code"},
            {"nom": "🖥️│tech-vocal",       "type": "vocal"},
        ]
    },
    {
        "categorie": "🌟 COMMUNAUTÉ",
        "salons": [
            {"nom": "💡│suggestions",      "type": "texte", "desc": "Propose des idées"},
            {"nom": "📊│sondages",         "type": "texte", "desc": "Votes et sondages"},
            {"nom": "🏅│présentations",    "type": "texte", "desc": "Présente-toi ici"},
            {"nom": "📰│partage",          "type": "texte", "desc": "Articles, liens intéressants"},
        ]
    },
    {
        "categorie": "🔧 MODÉRATION",
        "salons": [
            {"nom": "🔨│logs",             "type": "texte", "desc": "Logs de modération (privé)"},
            {"nom": "📋│rapports",         "type": "texte", "desc": "Signalements (privé)"},
        ]
    },
]

ROLES = [
    {"nom": "👑 Admin",       "couleur": discord.Color.red(),    "permissions": discord.Permissions.all()},
    {"nom": "🛡️ Modérateur",  "couleur": discord.Color.orange(), "permissions": discord.Permissions(
        kick_members=True, ban_members=True, manage_messages=True, mute_members=True
    )},
    {"nom": "⭐ VIP",         "couleur": discord.Color.gold(),   "permissions": discord.Permissions.none()},
    {"nom": "🎮 Gamer",       "couleur": discord.Color.green(),  "permissions": discord.Permissions.none()},
    {"nom": "💻 Développeur", "couleur": discord.Color.blue(),   "permissions": discord.Permissions.none()},
    {"nom": "🌱 Membre",      "couleur": discord.Color.teal(),   "permissions": discord.Permissions.none()},
]

# ══════════════════════════════════════════
#   BOT
# ══════════════════════════════════════════
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ══════════════════════════════════════════
#   DONNÉES EN MÉMOIRE
# ══════════════════════════════════════════
xp_data = {}
warnings_data = {}
msg_count = {}


# ══════════════════════════════════════════
#   ÉVÉNEMENTS
# ══════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash commande(s) synchronisée(s)")
    except Exception as e:
        print(f"❌ Erreur sync slash : {e}")
    print("👉 Utilise !setup ou /aide dans ton serveur !")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    uid = str(message.author.id)
    msg_count[uid] = msg_count.get(uid, 0) + 1
    if uid not in xp_data:
        xp_data[uid] = {"xp": 0, "level": 1}
    xp_data[uid]["xp"] += 5
    xp_needed = xp_data[uid]["level"] * 100
    if xp_data[uid]["xp"] >= xp_needed:
        xp_data[uid]["xp"] -= xp_needed
        xp_data[uid]["level"] += 1
        embed = discord.Embed(
            title="⬆️ Level Up !",
            description=f"Félicitations {message.author.mention} ! Tu es maintenant **niveau {xp_data[uid]['level']}** !",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)
    await bot.process_commands(message)


# ══════════════════════════════════════════
#   SLASH COMMAND /aide
# ══════════════════════════════════════════
def is_admin_user(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator or \
           any(r.name in ["👑 Admin", "🛡️ Modérateur"] for r in interaction.user.roles)


@bot.tree.command(name="aide", description="Affiche la liste des commandes")
async def slash_aide(interaction: discord.Interaction):
    est_admin = is_admin_user(interaction)

    embed = discord.Embed(title="📋 Commandes du bot", color=discord.Color.blurple())

    embed.add_field(name="🌍 Commandes de base", value=(
        "`!help` — Affiche cette aide\n"
        "`!ping` — Latence du bot\n"
        "`!hello` — Le bot te salue\n"
        "`!rank [@membre]` — Niveau et XP\n"
        "`!xp [@membre]` — Même chose que !rank\n"
        "`!userinfos [@membre]` — Infos sur un membre\n"
        "`!serveurinfos` — Infos sur le serveur\n"
        "`!avatar [@membre]` — Avatar d'un membre\n"
        "`!msg [@membre]` — Nombre de messages\n"
    ), inline=False)

    if est_admin:
        embed.add_field(name="🔒 Commandes admin", value=(
            "`!kick @membre [raison]` — Expulser\n"
            "`!ban @membre [raison]` — Bannir\n"
            "`!unban pseudo#0000` — Débannir\n"
            "`!mute @membre [raison]` — Rendre muet\n"
            "`!unmute @membre` — Retirer le mute\n"
            "`!warn @membre [raison]` — Avertir\n"
            "`!warnings @membre` — Voir les avertissements\n"
            "`!lock` — Verrouiller le salon\n"
            "`!unlock` — Déverrouiller le salon\n"
        ), inline=False)
        embed.set_footer(text="Tu vois les commandes admin car tu es Admin/Modérateur ✅")
    else:
        embed.set_footer(text="Préfixe : !")

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ══════════════════════════════════════════
#   COMMANDE SETUP
# ══════════════════════════════════════════
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild
    print("⏳ Démarrage du setup...")

    print("🗑️ Nettoyage des salons existants...")
    for channel in guild.channels:
        try:
            await channel.delete()
        except Exception:
            pass

    print("🗑️ Nettoyage des rôles existants...")
    for role in guild.roles:
        if role.name != "@everyone" and not role.managed:
            try:
                await role.delete()
            except Exception:
                pass

    print("🎭 Création des rôles...")
    roles_crees = {}
    for r in ROLES:
        role = await guild.create_role(
            name=r["nom"],
            color=r["couleur"],
            permissions=r["permissions"],
            hoist=True,
            mentionable=True
        )
        roles_crees[r["nom"]] = role
        print(f"   ✅ Rôle créé : {r['nom']}")
        await asyncio.sleep(0.5)

    role_mod = roles_crees.get("🛡️ Modérateur")

    for i, cat in enumerate(STRUCTURE):
        print(f"📁 Création : {cat['categorie']} ({i+1}/{len(STRUCTURE)})...")
        overwrites = {}
        if "MODÉRATION" in cat["categorie"]:
            overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False)}
            if role_mod:
                overwrites[role_mod] = discord.PermissionOverwrite(read_messages=True)

        categorie = await guild.create_category(cat["categorie"], overwrites=overwrites)
        for salon in cat["salons"]:
            if salon["type"] == "texte":
                await categorie.create_text_channel(salon["nom"], topic=salon.get("desc", ""), overwrites=overwrites)
            else:
                await categorie.create_voice_channel(salon["nom"], overwrites=overwrites)
            print(f"   💬 Salon créé : {salon['nom']}")
            await asyncio.sleep(0.4)

    for channel in guild.text_channels:
        if "bienvenue" in channel.name:
            embed = discord.Embed(
                title="👋 Bienvenue sur le serveur !",
                description=(
                    "Bienvenue dans notre communauté gaming & code !\n\n"
                    "📜 Lis les **règles** avant de commencer\n"
                    "🎭 Récupère tes **rôles** pour accéder aux salons\n"
                    "💬 Présente-toi dans **#présentations**\n\n"
                    "Bonne ambiance à tous ! 🚀"
                ),
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed)
            break

    print("✅ Serveur créé avec succès !")
    print(f"📁 {len(STRUCTURE)} catégories | 💬 {sum(len(c['salons']) for c in STRUCTURE)} salons | 🎭 {len(ROLES)} rôles")


@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu dois être administrateur pour utiliser cette commande.")


# ══════════════════════════════════════════
#   COMMANDES DE BASE
# ══════════════════════════════════════════
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="📋 Commandes du bot", color=discord.Color.blurple())
    embed.add_field(name="🌍 Commandes de base", value=(
        "`!help` — Affiche cette aide\n"
        "`!ping` — Latence du bot\n"
        "`!hello` — Le bot te salue\n"
        "`!rank [@membre]` — Niveau et XP\n"
        "`!xp [@membre]` — Même chose que !rank\n"
        "`!userinfos [@membre]` — Infos sur un membre\n"
        "`!serveurinfos` — Infos sur le serveur\n"
        "`!avatar [@membre]` — Avatar d'un membre\n"
        "`!msg [@membre]` — Nombre de messages\n"
    ), inline=False)
    embed.add_field(name="🔒 Commandes admin", value=(
        "`!kick @membre [raison]` — Expulser\n"
        "`!ban @membre [raison]` — Bannir\n"
        "`!unban pseudo#0000` — Débannir\n"
        "`!mute @membre [raison]` — Rendre muet\n"
        "`!unmute @membre` — Retirer le mute\n"
        "`!warn @membre [raison]` — Avertir\n"
        "`!warnings @membre` — Voir les avertissements\n"
        "`!lock` — Verrouiller le salon\n"
        "`!unlock` — Déverrouiller le salon\n"
    ), inline=False)
    embed.set_footer(text="Préfixe : !")
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    latence = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"Latence : **{latence}ms**",
        color=discord.Color.green() if latence < 100 else discord.Color.orange()
    )
    await ctx.send(embed=embed)


@bot.command()
async def hello(ctx):
    embed = discord.Embed(
        title="👋 Salut !",
        description=f"Bonjour {ctx.author.mention} ! Comment vas-tu aujourd'hui ? 😄",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed)


@bot.command()
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    uid = str(member.id)
    if uid not in xp_data:
        xp_data[uid] = {"xp": 0, "level": 1}
    data = xp_data[uid]
    xp_needed = data["level"] * 100
    embed = discord.Embed(title=f"⭐ Rang de {member.display_name}", color=discord.Color.gold())
    embed.add_field(name="Niveau", value=f"**{data['level']}**", inline=True)
    embed.add_field(name="XP", value=f"**{data['xp']} / {xp_needed}**", inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def xp(ctx, member: discord.Member = None):
    await rank(ctx, member)


@bot.command()
async def userinfos(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    embed = discord.Embed(title=f"👤 Infos de {member.display_name}", color=member.color)
    embed.add_field(name="Pseudo", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="A rejoint le", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name=f"Rôles ({len(roles)})", value=" ".join(roles) if roles else "Aucun", inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def serveurinfos(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"🏠 {guild.name}", color=discord.Color.blurple())
    embed.add_field(name="Propriétaire", value=guild.owner.mention, inline=True)
    embed.add_field(name="Membres", value=guild.member_count, inline=True)
    embed.add_field(name="Salons", value=len(guild.channels), inline=True)
    embed.add_field(name="Rôles", value=len(guild.roles), inline=True)
    embed.add_field(name="Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Avatar de {member.display_name}", color=discord.Color.blurple())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="msg")
async def msg_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    uid = str(member.id)
    count = msg_count.get(uid, 0)
    embed = discord.Embed(
        title="💬 Messages",
        description=f"{member.mention} a envoyé **{count}** message(s) depuis que le bot est en ligne.",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed)


# ══════════════════════════════════════════
#   COMMANDES ADMIN
# ══════════════════════════════════════════
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or \
               any(r.name in ["👑 Admin", "🛡️ Modérateur"] for r in ctx.author.roles)
    return commands.check(predicate)


@bot.command()
@is_admin()
async def kick(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    await member.kick(reason=raison)
    embed = discord.Embed(title="👢 Membre expulsé", color=discord.Color.orange())
    embed.add_field(name="Membre", value=str(member), inline=True)
    embed.add_field(name="Par", value=ctx.author.mention, inline=True)
    embed.add_field(name="Raison", value=raison, inline=False)
    await ctx.send(embed=embed)

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage : `!kick @membre [raison]`")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def ban(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    await member.ban(reason=raison)
    embed = discord.Embed(title="🔨 Membre banni", color=discord.Color.red())
    embed.add_field(name="Membre", value=str(member), inline=True)
    embed.add_field(name="Par", value=ctx.author.mention, inline=True)
    embed.add_field(name="Raison", value=raison, inline=False)
    await ctx.send(embed=embed)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage : `!ban @membre [raison]`")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def unban(ctx, *, username):
    banned = [entry async for entry in ctx.guild.bans()]
    for entry in banned:
        if str(entry.user) == username:
            await ctx.guild.unban(entry.user)
            embed = discord.Embed(
                title="✅ Membre débanni",
                description=f"**{username}** a été débanni.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return
    await ctx.send(f"❌ Aucun banni trouvé avec le nom `{username}`.")

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def mute(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    role_mute = discord.utils.get(ctx.guild.roles, name="🔇 Mute")
    if not role_mute:
        role_mute = await ctx.guild.create_role(name="🔇 Mute")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role_mute, send_messages=False, speak=False)
    await member.add_roles(role_mute, reason=raison)
    embed = discord.Embed(title="🔇 Membre muté", color=discord.Color.dark_gray())
    embed.add_field(name="Membre", value=member.mention, inline=True)
    embed.add_field(name="Par", value=ctx.author.mention, inline=True)
    embed.add_field(name="Raison", value=raison, inline=False)
    await ctx.send(embed=embed)

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage : `!mute @membre [raison]`")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def unmute(ctx, member: discord.Member):
    role_mute = discord.utils.get(ctx.guild.roles, name="🔇 Mute")
    if role_mute and role_mute in member.roles:
        await member.remove_roles(role_mute)
        embed = discord.Embed(
            title="🔊 Membre démute",
            description=f"{member.mention} peut de nouveau parler.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {member.mention} n'est pas muté.")

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def warn(ctx, member: discord.Member, *, raison="Aucune raison fournie"):
    uid = str(member.id)
    if uid not in warnings_data:
        warnings_data[uid] = []
    warnings_data[uid].append({"raison": raison, "par": str(ctx.author)})
    nb = len(warnings_data[uid])
    embed = discord.Embed(title="⚠️ Avertissement", color=discord.Color.yellow())
    embed.add_field(name="Membre", value=member.mention, inline=True)
    embed.add_field(name="Par", value=ctx.author.mention, inline=True)
    embed.add_field(name="Raison", value=raison, inline=False)
    embed.set_footer(text=f"Total d'avertissements : {nb}")
    await ctx.send(embed=embed)

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage : `!warn @membre [raison]`")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def warnings(ctx, member: discord.Member):
    uid = str(member.id)
    warns = warnings_data.get(uid, [])
    embed = discord.Embed(title=f"⚠️ Avertissements de {member.display_name}", color=discord.Color.yellow())
    if not warns:
        embed.description = "Aucun avertissement."
    else:
        for i, w in enumerate(warns, 1):
            embed.add_field(name=f"Warn #{i}", value=f"Raison : {w['raison']}\nPar : {w['par']}", inline=False)
    await ctx.send(embed=embed)

@warnings.error
async def warnings_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(
        title="🔒 Salon verrouillé",
        description=f"Le salon {ctx.channel.mention} a été verrouillé par {ctx.author.mention}.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@lock.error
async def lock_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


@bot.command()
@is_admin()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(
        title="🔓 Salon déverrouillé",
        description=f"Le salon {ctx.channel.mention} a été déverrouillé par {ctx.author.mention}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@unlock.error
async def unlock_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")


bot.run(TOKEN)
