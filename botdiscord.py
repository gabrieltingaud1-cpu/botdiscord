import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

MON_ID = 1106997195980427354

# ================================
#           GÉNÉRAL
# ================================

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

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