import discord
import logging
import requests as r
from json import loads
from modules.teachers.teachers import Monika
from modules.music.player import Player

TOKEN = "ODAxODg5MTExNzQ0NzA4NjQx.YAnPbg.I9PjsuAQF1Tj4HkXbWtKHQ7zmts"
debug = True

DELETE_TIME = 20.0
ADMIN = 470490558713036801

if debug:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)


async def change_nick(msg: discord.Message):
    if len(msg.content.split()) < 3:
        await msg.channel.send("Příkaz se zadává ve formátu: '-nick @cíl přezdívka'", delete_after=DELETE_TIME)
        return
    args = msg.content.split(" ", 2)
    if not (args[1].startswith("<@") and args[1].endswith(">") and msg.mentions):
        await msg.channel.send("Druhý argument musí být uživatel, jehož jméno měníš.", delete_after=DELETE_TIME)
        return
    target = msg.mentions[0]
    nick = args[2]
    nick = nick.strip()
    if len(nick) > 32:
        await msg.channel.send("Přezdívka může mít maximálně 32 charakterů", delete_after=DELETE_TIME)
        return
    if nick.lower() == "none" or nick.lower() == "off" or nick.lower() == "clear":
        nick = None
    try:
        before = target.display_name
        await target.edit(nick=nick, reason="Změnil {0.author.name} v kanálu {0.channel.name}".format(msg))
        if not nick:
            nick = target.name
        await msg.channel.send("Změněno z '{0}' na '{1}'".format(before, nick))
    except discord.Forbidden:
        await msg.channel.send("Bohužel, tahle přezdívka pořád nejde měnit")
    except discord.HTTPException:
        print("Chyba při připojování na straně Discordu")
    return


async def among_get_active(channel):
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?format=json&appid=945360"
    info = r.get(url)
    if info.status_code != 200:
        await channel.send("Chyba při získávání informací od Steamu")
    info = loads(info.text)
    stats = info["response"]
    response = "Among Us právě hraje {0} hráčů".format(stats["player_count"])
    await channel.send(response)
    return


class Bot(discord.Client):

    def __init__(self, **options):
        intents = discord.Intents.default()
        self.guild = None
        self.admin = ADMIN
        self.Monika = Monika()
        self.Player = Player()
        super().__init__(intents=intents, loop=None, **options)

    async def on_ready(self):
        logging.info("I'm ready! {0.name}".format(self.user))

        async for guild in self.fetch_guilds(limit=1):
            self.guild: discord.Guild = guild
        logging.info("Connected to {0}".format(self.guild.name))

        self.admin: discord.Member = await self.guild.fetch_member(self.admin)
        logging.info("Admin is: {0}".format(self.admin.name))

    async def on_message(self, message: discord.Message):
        logging.debug("Registered message", message.content)

        if message.author == self.user:
            return

        if message.content.startswith("-nick"):
            logging.debug("Passed onto nickname changer")
            await change_nick(message)
            return

        if message.content.startswith("-among"):
            logging.debug("Passed onto Among Us fc")
            await among_get_active(message.channel)
            return

        if message.content.startswith("!exit!") and message.author == self.admin:
            await message.channel.send("Jdu spát")
            exit("Exited via command on discord")

        await self.Monika.handleMessage(message)


Bot().run(TOKEN)
