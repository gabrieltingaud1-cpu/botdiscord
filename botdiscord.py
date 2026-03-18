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

@bot.tree.command(name="resume-chat", description="Résume les 50 derniers messages du salon")
async def resume_chat(interaction: discord.Interaction):
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

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_KEY')}",
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
            data = await resp.json()
            resume = data["choices"][0]["message"]["content"]

    embed = discord.Embed(title="📝 Résumé du chat", description=resume, color=0x00bfff)
    await interaction.followup.send(embed=embed)

@bot.command()
async def classement(ctx):
    if not xp_data:
        await ctx.send("Personne n'a encore de XP !")
        return

    tries = sorted(xp_data.items(), key=lambda x: (x[1]["niveau"], x[1]["xp"]), reverse=True)

    embed = discord.Embed(title="🏆 Classement XP", color=0x00bfff)
    medailles = ["🥇", "🥈", "🥉"]

    for i, (user_id, data) in enumerate(tries[:10]):
        membre = ctx.guild.get_member(int(user_id))
        if membre:
            medaille = medailles[i] if i < 3 else f"**#{i+1}**"
            embed.add_field(
                name=f"{medaille} {membre.name}",
                value=f"Niveau {data['niveau']} • {data['xp']} XP",
                inline=False
            )

    await ctx.send(embed=embed)

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

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong ! 🏓 {round(bot.latency * 1000)}ms")

@bot.command()
async def hello(ctx):
    await ctx.send("Salut ! 👋")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Commandes du bot 📋", color=0x00bfff)
    embed.add_field(name="🌟 Général", value="`!ping` `!hello` `!help`", inline=False)
    embed.add_field(name="🎮 Jeux", value="`!pile_ou_face` `!dé` `!rps <pierre/feuille/ciseaux>` `!chiffre` `!deviner <nombre>`", inline=False)
    embed.add_field(name="⭐ Niveaux", value="`/niveau` `!classement`", inline=False)
    embed.add_field(name="📝 Utilitaires", value="`/resume-chat`", inline=False)
    if ctx.author.id == MON_ID:
        embed.add_field(name="🔨 Modération", value="`!kick <membre>` `!ban <membre>` `!mute <membre>` `!unmute <membre>` `!clear <nombre>`", inline=False)
    await ctx.send(embed=embed)

# ================================
#           JEUX
# ================================

@bot.command()
async def pile_ou_face(ctx):
    await ctx.send(random.choice(["Pile ! 🪙", "Face ! 🪙"]))

@bot.command()
async def dé(ctx):
    await ctx.send(f"🎲 Tu as lancé un **{random.randint(1, 6)}** !")

@bot.command()
async def rps(ctx, choix: str):
    choix = choix.lower()
    options = ["pierre", "feuille", "ciseaux"]

    if choix not in options:
        await ctx.send("Choisis entre `pierre`, `feuille` ou `ciseaux` !")
        return

    bot_choix = random.choice(options)

    if choix == bot_choix:
        result = "Égalité ! 🤝"
    elif (choix == "pierre" and bot_choix == "ciseaux") or \
         (choix == "feuille" and bot_choix == "pierre") or \
         (choix == "ciseaux" and bot_choix == "feuille"):
        result = "Tu as gagné ! 🎉"
    else:
        result = "Tu as perdu ! 😢"

    await ctx.send(f"Tu as choisi **{choix}**, moi **{bot_choix}** → {result}")

parties = {}

@bot.command()
async def chiffre(ctx):
    parties[ctx.author.id] = random.randint(1, 100)
    await ctx.send("J'ai choisi un chiffre entre 1 et 100, devine avec `!deviner <nombre>` !")

@bot.command()
async def deviner(ctx, nombre: int):
    if ctx.author.id not in parties:
        await ctx.send("Lance d'abord une partie avec `!chiffre` !")
        return

    secret = parties[ctx.author.id]

    if nombre < secret:
        await ctx.send("📈 C'est plus grand !")
    elif nombre > secret:
        await ctx.send("📉 C'est plus petit !")
    else:
        await ctx.send(f"🎉 Bravo ! C'était bien **{secret}** !")
        del parties[ctx.author.id]

# ================================
#         MODÉRATION
# ================================

def proprietaire_uniquement():
    async def predicate(ctx):
        if ctx.author.id != MON_ID:
            await ctx.send("❌ Tu n'as pas la permission de faire ça !")
            return False
        return True
    return commands.check(predicate)

@bot.command()
@proprietaire_uniquement()
async def kick(ctx, membre: discord.Member, *, raison="Aucune raison"):
    await membre.kick(reason=raison)
    await ctx.send(f"👢 **{membre}** a été kick. Raison : {raison}")

@bot.command()
@proprietaire_uniquement()
async def ban(ctx, membre: discord.Member, *, raison="Aucune raison"):
    await membre.ban(reason=raison)
    await ctx.send(f"🔨 **{membre}** a été banni. Raison : {raison}")

@bot.command()
@proprietaire_uniquement()
async def mute(ctx, membre: discord.Member):
    role_mute = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role_mute:
        role_mute = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role_mute, send_messages=False, speak=False)

    await membre.add_roles(role_mute)
    await ctx.send(f"🔇 **{membre}** a été mute !")

@bot.command()
@proprietaire_uniquement()
async def unmute(ctx, membre: discord.Member):
    role_mute = discord.utils.get(ctx.guild.roles, name="Muted")
    if role_mute in membre.roles:
        await membre.remove_roles(role_mute)
        await ctx.send(f"🔊 **{membre}** a été unmute !")
    else:
        await ctx.send(f"{membre} n'est pas mute !")

@bot.command()
@proprietaire_uniquement()
async def clear(ctx, nombre: int):
    await ctx.channel.purge(limit=nombre + 1)
    await ctx.send(f"🗑️ {nombre} messages supprimés !", delete_after=3)

# ================================
#         ERREURS
# ================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membre introuvable !")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Il manque un argument à ta commande !")

bot.run(os.getenv("TOKEN"))
