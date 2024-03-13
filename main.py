import discord
import random
import asyncio
import datetime
import os
from discord.ext import commands, tasks
from server import stay_alive
from atizitate import atizitate
from fifa_cards import cards

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


def is_owner_or_predator(ctx):
    return ctx.author.id == ctx.guild.owner_id or discord.utils.get(
        ctx.author.roles, name="Predator") is not None


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(
        name="mit den neuen Besitzern"))
    current = datetime.datetime.now()
    print(f'Logged in as {bot.user.name}')
    print(f"Aktuelle Uhrzeit: {current.strftime('%H:%M:%S')}")

    # Automatisch die Guild ID abfragen und verwenden
    guild = bot.guilds[0]
    print(f"Guild ID: {guild.id}")

    change_channel_name.start(guild)
    reset_channel_name.start(guild)


@tasks.loop(seconds=1)
async def change_channel_name(guild):
    now = datetime.datetime.now()
    if now.hour == 22 and now.minute == 0:
        channel = discord.utils.get(guild.voice_channels, name="Talk")
        if channel:
            new_name = "Games"
            await channel.edit(name=new_name)


@tasks.loop(seconds=1)
async def reset_channel_name(guild):
    now = datetime.datetime.now()
    if now.hour == 4 and now.minute == 0:
        channel = discord.utils.get(guild.voice_channels, name="Games")
        if channel:
            await channel.edit(name="Talk")


@bot.command(help='Zeigt diese Liste an Befehlen an')
async def help(ctx):
    command_list = [
        f'!{command.name} - _{command.help}_' for command in bot.commands
        if not command.hidden
    ]
    commands_string = '\n'.join(command_list)

    dm_channel = await ctx.author.create_dm()
    await dm_channel.send(
        f'**Hier ist eine Liste mit verfügbaren Befehlen:**\n\n{commands_string}'
    )


@bot.command(help='Bewertet Profilbilder')
async def rate(ctx, user: discord.Member):
    if user.id == 543122703884746753:  # Ersetze DEIN_BENUTZER_ID mit der ID des speziellen Benutzers
        rating = 11  # Eine spezielle Bewertung für den bestimmten Benutzer
        rating_text = "Zurecht Server Mommy.."
    elif user.id == 1078392099847819314:
        rating = 0
        rating_text = "Junge er hat einfach Hamster pb... SCHREIE"
    elif user.id == 1090705015720652881:
        rating = 11
        rating_text = "Hä Ati halt? Ganz klar"
    elif user.id == 228511446739320832:
        rating = 11
        rating_text = "Frank halt einfach Player.. Ganz klares Ding"
    else:
        rating = random.randint(1, 10)
        rating_text = {
            1: "Bahh..",
            2: "Weiß ich jz nicht...",
            3: "Muss nicht..",
            4: "Hmpf naja",
            5: "Okay..",
            6: "Solide",
            7: "Stabil",
            8: "Ehrlich stark",
            9: "Puh 🥵",
            10: "Einfach perfekt! 🥵🔥"
        }.get(rating)

    embed = discord.Embed(title=f'Profilbild von {user.display_name}',
                          color=discord.Color.blue())
    embed.set_image(url=user.avatar_url)
    await ctx.send(embed=embed)

    await ctx.send(
        f'Ich bewerte {user.mention}`s Profilbild mit {rating}/10 - {rating_text}'
    )


@bot.command(help='Zeigt zufälliges Zitat von Ati')
async def atizitat(ctx):
    zitat = random.choice(atizitate)
    await ctx.send(zitat)


@bot.command()
async def packopening(ctx):
    discrete_choices = []
    cumulative_weight = 0
    for bild, gewichtung in cards:
        cumulative_weight += gewichtung
        discrete_choices.append((bild, cumulative_weight))

    random_value = random.random()

    selected_filename = next(bild
                             for bild, cumulative_weight in discrete_choices
                             if random_value <= cumulative_weight)

    selected_gewichtung = next(gewichtung for bild, gewichtung in cards
                               if bild == selected_filename)

    if selected_gewichtung <= 0.048:
        await ctx.send(f'**🔥🔥 WALKOUT 🔥🔥**')

    bilder_ordner = "fifa_cards"
    selected_bild_path = os.path.join(bilder_ordner, selected_filename)

    with open(selected_bild_path, "rb") as file:
        bild = discord.File(file)
        await ctx.send(file=bild)


@bot.command()
@commands.check(is_owner_or_predator)
async def spind(ctx, user: discord.Member):
    desired_role_name = "Spind von Davy Jones"

    role = discord.utils.get(ctx.guild.roles, name=desired_role_name)
    if not role:
        await ctx.send(
            f'Die Rolle "{desired_role_name}" existiert nicht auf diesem Server.'
        )
        return

    try:
        if role in user.roles:
            await user.remove_roles(role, reason="Gewünschte Rolle entfernt")
            await ctx.send(
                f'{user.name} hat den Spind von Davy Jones verlassen')
        else:
            original_roles = user.roles[1:]

            await user.edit(roles=[ctx.guild.default_role])

            await user.add_roles(role, reason="Gewünschte Rolle zugewiesen")

            await user.add_roles(
                *original_roles,
                reason="Ursprüngliche Rollen wiederhergestellt")

            await ctx.send(
                f'{user.name} wurde in den Spind von Davy Jones gesteckt.')
    except discord.Forbidden:
        await ctx.send(
            "Der Bot hat nicht die Berechtigung, Rollen zu verwalten.")
    except discord.HTTPException:
        await ctx.send(
            "Ein Fehler ist aufgetreten. Bitte überprüfe die Bot-Berechtigungen und versuche es erneut."
        )


stay_alive()

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

bot.run(DISCORD_TOKEN)
