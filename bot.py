import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import random
import json
import aiohttp

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

MON_ID = 1106997195980427354

# ================================
#         SYSTÈME XP
# ================================

def charger_xp():
    if os.path.exists("xp.json"):
        with open("xp.json", "r") as f:
            return json.load(f)
    return {}

def sauvegarder_xp(data):
    with open("xp.json", "w") as f:
        json.dump(data, f)

def xp_pour_niveau(niveau):
    return niveau * 100

xp_data = charger_xp()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)

    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "niveau": 1}

    xp_data[user_id]["xp"] += random.randint(5, 15)
    niveau_actuel = xp_data[user_id]["niveau"]
    xp_necessaire = xp_pour_niveau(niveau_actuel)

    if xp_data[user_id]["xp"] >= xp_necessaire:
        xp_data[user_id]["xp"] -= xp_necessaire
        xp_data[user_id]["niveau"] += 1
        nouveau_niveau = xp_data[user_id]["niveau"]
        await message.channel.send(f"🎉 Félicitations {message.author.mention} ! Tu es passé au **niveau {nouveau_niveau}** !")

    sauvegarder_xp(xp_data)
    await bot.process_commands(message)

# ================================
#           GÉNÉRAL
# ================================

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    await bot.tree.sync()
    print("Commandes slash synchronisées !")

@bot.event
async def on_member_join(member):
    salon = discord.utils.get(member.guild.text_channels, name="bienvenue")
    if salon:
        embed = discord.Embed(
            title=f"Bienvenue sur {member.guild.name} ! 🎉",
            description=f"Salut {member.mention} ! Bienvenue sur le serveur !\nOn est maintenant **{member.guild.member_count}** membres !",
            color=0x00bfff
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await salon.send(embed=embed)

@bot.tree.command(name="ping", description="Voir la latence du bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong ! 🏓 {round(bot.latency * 1000)}ms")

@bot.tree.command(name="hello", description="Le bot te dit bonjour")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Salut ! 👋")

@bot.tree.command(name="help", description="Voir toutes les commandes disponibles")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Commandes du bot 📋", color=0x00bfff)
    embed.add_field(
        name="🌟 Général",
        value="`/ping` `/hello` `/help`",
        inline=False
    )
    embed.add_field(
        name="🎮 Jeux",
        value="`/pile_ou_face` `/de` `/rps` `/chiffre` `/deviner`",
        inline=False
    )
    embed.add_field(
        name="⭐ Niveaux",
        value="`/niveau` `/classement`",
        inline=False
    )
    embed.add_field(
        name="📝 Utilitaires",
        value="`/resume_chat`",
        inline=False
    )
    if interaction.user.id == MON_ID:
        embed.add_field(
            name="🔨 Modération (propriétaire uniquement)",
            value="`/kick` `/ban` `/mute` `/unmute` `/clear`",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

# ================================
#           NIVEAUX
# ================================

@bot.tree.command(name="niveau", description="Voir le niveau d'un membre")
@app_commands.describe(membre="Le membre dont tu veux voir le niveau")
async def niveau(interaction: discord.Interaction, membre: discord.Member = None):
    membre = membre or interaction.user
    user_id = str(membre.id)

    if user_id not in xp_data:
        await interaction.response.send_message(f"{membre.mention} n'a pas encore de XP !")
        return

    xp = xp_data[user_id]["xp"]
    niv = xp_data[user_id]["niveau"]
    xp_necessaire = xp_pour_niveau(niv)

    embed = discord.Embed(title=f"Niveau de {membre.name}", color=0x00bfff)
    embed.add_field(name="🏆 Niveau", value=str(niv), inline=True)
    embed.add_field(name="✨ XP", value=f"{xp}/{xp_necessaire}", inline=True)
    embed.set_thumbnail(url=membre.avatar.url if membre.avatar else membre.default_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="classement", description="Voir le classement XP du serveur")
async def classement(interaction: discord.Interaction):
    if not xp_data:
        await interaction.response.send_message("Personne n'a encore de XP !")
        return

    tries = sorted(xp_data.items(), key=lambda x: (x[1]["niveau"], x[1]["xp"]), reverse=True)

    embed = discord.Embed(title="🏆 Classement XP", color=0x00bfff)
    medailles = ["🥇", "🥈", "🥉"]

    for i, (user_id, data) in enumerate(tries[:10]):
        membre = interaction.guild.get_member(int(user_id))
        if membre:
            medaille = medailles[i] if i < 3 else f"**#{i+1}**"
            embed.add_field(
                name=f"{medaille} {membre.name}",
                value=f"Niveau {data['niveau']} • {data['xp']} XP",
                inline=False
            )

    await interaction.response.send_message(embed=embed)

# ================================
#           UTILITAIRES
# ================================

@bot.tree.command(name="resume_chat", description="Résume les 50 derniers messages du salon")
async def resume_chat(interaction: discord.Interaction):
    try:
        await interaction.response.defer()

        messages = []
        async for message in interaction.channel.history(limit=50):
            if not message.author.bot and message.content:
                messages.append(f"{message.author.name}: {message.content}")

        messages.reverse()

        if not messages:
            await interaction.followup.send("❌ Aucun message à résumer !")
            return

        conversation = "\n".join(messages)

        groq_key = os.getenv('GROQ_KEY')
        if not groq_key:
            await interaction.followup.send("❌ Erreur : clé GROQ_KEY manquante dans le fichier .env !")
            return

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "max_tokens": 500,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es un assistant qui résume des conversations Discord en français de façon claire et concise."
                        },
                        {
                            "role": "user",
                            "content": f"Résume cette conversation Discord en 5 lignes maximum :\n\n{conversation}"
                        }
                    ]
                }
            ) as resp:
                if resp.status != 200:
                    erreur_text = await resp.text()
                    await interaction.followup.send(f"❌ Erreur API Groq (status {resp.status}) : {erreur_text}")
                    return
                data = await resp.json()
                resume = data["choices"][0]["message"]["content"]

        embed = discord.Embed(title="📝 Résumé du chat", description=resume, color=0x00bfff)
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur inattendue : {e}")

# ================================
#           JEUX
# ================================

@bot.tree.command(name="pile_ou_face", description="Lance une pièce")
async def pile_ou_face(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(["Pile ! 🪙", "Face ! 🪙"]))

@bot.tree.command(name="de", description="Lance un dé à 6 faces")
async def de(interaction: discord.Interaction):
    await interaction.response.send_message(f"🎲 Tu as lancé un **{random.randint(1, 6)}** !")

@bot.tree.command(name="rps", description="Pierre, feuille, ciseaux contre le bot")
@app_commands.describe(choix="Ton choix : pierre, feuille ou ciseaux")
@app_commands.choices(choix=[
    app_commands.Choice(name="Pierre", value="pierre"),
    app_commands.Choice(name="Feuille", value="feuille"),
    app_commands.Choice(name="Ciseaux", value="ciseaux"),
])
async def rps(interaction: discord.Interaction, choix: str):
    options = ["pierre", "feuille", "ciseaux"]
    bot_choix = random.choice(options)

    if choix == bot_choix:
        result = "Égalité ! 🤝"
    elif (choix == "pierre" and bot_choix == "ciseaux") or \
         (choix == "feuille" and bot_choix == "pierre") or \
         (choix == "ciseaux" and bot_choix == "feuille"):
        result = "Tu as gagné ! 🎉"
    else:
        result = "Tu as perdu ! 😢"

    await interaction.response.send_message(f"Tu as choisi **{choix}**, moi **{bot_choix}** → {result}")

parties = {}

@bot.tree.command(name="chiffre", description="Lance une partie de devinette (chiffre entre 1 et 100)")
async def chiffre(interaction: discord.Interaction):
    parties[interaction.user.id] = random.randint(1, 100)
    await interaction.response.send_message("J'ai choisi un chiffre entre 1 et 100, devine avec `/deviner` !")

@bot.tree.command(name="deviner", description="Devine le chiffre secret")
@app_commands.describe(nombre="Ton nombre à deviner")
async def deviner(interaction: discord.Interaction, nombre: int):
    if interaction.user.id not in parties:
        await interaction.response.send_message("Lance d'abord une partie avec `/chiffre` !")
        return

    secret = parties[interaction.user.id]

    if nombre < secret:
        await interaction.response.send_message("📈 C'est plus grand !")
    elif nombre > secret:
        await interaction.response.send_message("📉 C'est plus petit !")
    else:
        await interaction.response.send_message(f"🎉 Bravo ! C'était bien **{secret}** !")
        del parties[interaction.user.id]

# ================================
#         MODÉRATION
# ================================

def est_proprietaire(interaction: discord.Interaction) -> bool:
    return interaction.user.id == MON_ID

@bot.tree.command(name="kick", description="Kick un membre du serveur")
@app_commands.describe(membre="Le membre à kick", raison="La raison du kick")
async def kick(interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison"):
    if not est_proprietaire(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission de faire ça !", ephemeral=True)
        return
    await membre.kick(reason=raison)
    await interaction.response.send_message(f"👢 **{membre}** a été kick. Raison : {raison}")

@bot.tree.command(name="ban", description="Ban un membre du serveur")
@app_commands.describe(membre="Le membre à ban", raison="La raison du ban")
async def ban(interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison"):
    if not est_proprietaire(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission de faire ça !", ephemeral=True)
        return
    await membre.ban(reason=raison)
    await interaction.response.send_message(f"🔨 **{membre}** a été banni. Raison : {raison}")

@bot.tree.command(name="mute", description="Mute un membre du serveur")
@app_commands.describe(membre="Le membre à mute")
async def mute(interaction: discord.Interaction, membre: discord.Member):
    if not est_proprietaire(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission de faire ça !", ephemeral=True)
        return

    role_mute = discord.utils.get(interaction.guild.roles, name="Muted")
    if not role_mute:
        role_mute = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(role_mute, send_messages=False, speak=False)

    await membre.add_roles(role_mute)
    await interaction.response.send_message(f"🔇 **{membre}** a été mute !")

@bot.tree.command(name="unmute", description="Unmute un membre du serveur")
@app_commands.describe(membre="Le membre à unmute")
async def unmute(interaction: discord.Interaction, membre: discord.Member):
    if not est_proprietaire(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission de faire ça !", ephemeral=True)
        return

    role_mute = discord.utils.get(interaction.guild.roles, name="Muted")
    if role_mute in membre.roles:
        await membre.remove_roles(role_mute)
        await interaction.response.send_message(f"🔊 **{membre}** a été unmute !")
    else:
        await interaction.response.send_message(f"{membre} n'est pas mute !")

@bot.tree.command(name="clear", description="Supprimer des messages dans le salon")
@app_commands.describe(nombre="Nombre de messages à supprimer")
async def clear(interaction: discord.Interaction, nombre: int):
    if not est_proprietaire(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission de faire ça !", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=nombre)
    await interaction.followup.send(f"🗑️ {nombre} messages supprimés !", ephemeral=True)

# ================================
#         ERREURS
# ================================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRequiredArgument):
        await interaction.response.send_message("❌ Il manque un argument à ta commande !", ephemeral=True)
    elif isinstance(error, app_commands.MemberNotFound):
        await interaction.response.send_message("❌ Membre introuvable !", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Une erreur est survenue : {error}", ephemeral=True)

bot.run(os.getenv("TOKEN"))
