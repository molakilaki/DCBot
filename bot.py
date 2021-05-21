import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import logging
import requests as r
from datetime import datetime, timezone, timedelta
from json import loads
from modules.teachers.teachers import Monika
from modules.music.player import Player
from modules.pipa.pipa import Hostinsky
from modules.countdown import Countdown
import os
from os.path import join, dirname
from dotenv import load_dotenv

debug = False

DELETE_TIME = 20.0
ADMIN = 470490558713036801
tzone = timezone(timedelta(hours=-2))

if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="-", owner_id=ADMIN, intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("TOKEN")


@bot.command(name="nick")
@commands.guild_only()
async def change_nick(ctx: commands.Context, target: discord.Member, *, nick: str = None):
    """změní nick zadanému hráčovi"""
    nick = nick.strip()
    if len(nick) > 32:
        await ctx.send("Přezdívka může mít maximálně 32 charakterů", delete_after=DELETE_TIME)
        return
    before = target.display_name
    try:
        await target.edit(nick=nick, reason="Změnil {0.author.name} v kanálu {0.channel.name}".format(ctx))
    except discord.Forbidden:
        await ctx.send("Nemám právo měnit tuto přezdívku")
    else:
        await ctx.send("Změněno z '{0}' na '{1}' uživatelem `{2}`".format(before, nick, ctx.author.name))
    return


@bot.command(name="among")
async def among_get_active(ctx: commands.Context):
    """Vypíše počet aktivních Among Us hráčů na Steamu"""
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?format=json&appid=945360"
    info = r.get(url)
    if info.status_code != 200:
        await ctx.send("Chyba při získávání informací od Steamu", delete_after=DELETE_TIME)
        return
    info = loads(info.text)
    stats = info["response"]
    embed = discord.Embed(title="Among Us", colour=discord.Colour.from_rgb(197, 17, 17), timestamp=datetime.now(tz=tzone))
    embed.set_thumbnail(url="https://cdn.akamai.steamstatic.com/steam/apps/945360/header.jpg?t=1619622456")
    embed.description = "{0} aktivních hráčů".format(stats["player_count"])
    await ctx.send(embed=embed)
    return


@bot.command(name="ping")
async def pong(ctx: commands.Context):
    await ctx.send("Pong " + str(int(bot.latency * 1000)) + "ms")


@bot.command(name="exit", hidden=True)
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    await ctx.send("Jdu spát")
    for guild in bot.guilds:
        if guild.voice_client:
            await guild.voice_client.disconnect()
    await bot.close()
    exit(0)


@bot.command(name="source", aliases=["src"])
async def print_source(ctx: commands.Context):
    """Odkaz na zdrojový kód bota"""
    await ctx.send("https://github.com/stepech/DCBot")


@bot.event
async def on_ready():
    logging.info("I'm ready! {0.name}".format(bot.user))
    for guild in await bot.fetch_guilds().flatten():
        logging.info("Connected to {0}".format(guild.name))

    admin: discord.User = await bot.fetch_user(bot.owner_id)
    logging.info("Owner is: {0}".format(admin.name))
    logging.info("---------")
    logging.info("°°Ready°°")


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if bot.get_guild(498423239119208448).get_role(770453970165694545) not in before.roles:
        return
    role: discord.Role = bot.get_guild(498423239119208448).get_role(827625682833637389)
    try:
        if before.status == discord.Status.offline and after.status is not before.status:
            await after.add_roles(role, reason="Viditelný status")
        elif before.status != after.status and after.status == discord.Status.offline:
            await after.remove_roles(role, reason="Je offline/neviditelný")
    except discord.NotFound:
        pass


@bot.event
async def on_command_error(ctx: commands.Context, exc: commands.CommandError):
    if isinstance(exc, commands.MemberNotFound):
        await ctx.send("Uživatel nebyl nalezen")
    elif isinstance(exc, commands.MissingRequiredArgument):
        await ctx.send("Špatné formátování příkazu. Nedodány veškeré argumenty")
    elif isinstance(exc, commands.CommandNotFound):
        pass
    elif isinstance(exc, commands.NoPrivateMessage):
        await ctx.send("Nelze použít v soukromém chatu")
    elif isinstance(exc, commands.CheckFailure):
        pass
    else:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        await ctx.send("<@" + str(470490558713036801) + ">, chyba")
        raise exc


@slash.slash(name="ping", description="Pong")
async def _ping(ctx: SlashContext):
    await pong(ctx)


@slash.slash(name="among", description="Aktivní počet Among Us hráčů na Steamu")
async def _among(ctx: SlashContext):
    await among_get_active(ctx)


@slash.slash(name="nick", description="Změní nick uživateli",
             options=[create_option(name="user",
                                    description="Cíl kterému měníš přezdívku",
                                    option_type=6,
                                    required=True),
                      create_option(name="nick",
                                    description="nová přezdívka",
                                    option_type=3,
                                    required=False)])
async def _nick(ctx: SlashContext, user, nick=None):
    await change_nick(ctx, target=user, nick=nick)


@slash.slash(name="exit", description="Vypne bota, může použít jen stepech")
@commands.is_owner()
async def _shutdown(ctx: SlashContext):
    await shutdown(ctx)


@slash.slash(name="source", description="Odkaz na zdrojový kód bota")
async def _print_source(ctx: SlashContext):
    await print_source(ctx)


bot.add_cog(Countdown(bot))
bot.add_cog(Monika(bot))
#bot.add_cog(Player(bot))
bot.add_cog(Hostinsky(bot))
bot.run(TOKEN)
