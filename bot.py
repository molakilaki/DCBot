import discord
import logging
import requests as r
from json import loads
from asyncio import sleep
from modules.teachers.teachers import Monika
from modules.music.player import Player
from modules.Volby.Volby import Voter
import re

TOKEN = "ODE4ODk5MjkxMDQ4Mzc4NDIx.YEexZQ.KnLZNtYCxu-pwBQzqWAx7oRGoQo"
debug = False

DELETE_TIME = 20.0
ADMIN = 470490558713036801

FILTERED_MUSIC = ["2oAZlBN2CmNieXmJ1bQDYL", "JjmMUy49mV8"]

if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)


async def change_nick(msg: discord.Message):
    if len(msg.content.split()) < 3:
        await msg.channel.send("Příkaz se zadává ve formátu: '-nick @cíl přezdívka'", delete_after=DELETE_TIME)
        return
    args = msg.content.split(" ", 2)
    if not (args[1].startswith("<@") and args[1].endswith(">") and msg.mentions):
        await msg.channel.send("Příkaz se zadává ve formátu: '-nick @cíl přezdívka'", delete_after=DELETE_TIME)
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
        return
    info = loads(info.text)
    stats = info["response"]
    await channel.send("Among Us právě hraje {0} hráčů".format(stats["player_count"]))
    return


class Bot(discord.Client):

    def __init__(self, **options):
        intents = discord.Intents.default()
        self.guild = None
        self.admin = ADMIN
        self.Monika = Monika()
        # self.Player = Player()
        self.Voter = None
        super().__init__(intents=intents, loop=None, **options)

    async def on_ready(self):
        logging.info("I'm ready! {0.name}".format(self.user))

        self.guild: discord.Guild = await self.fetch_guild(498423239119208448)
        logging.info("Connected to {0}".format(self.guild.name))

        self.admin: discord.Member = await self.guild.fetch_member(self.admin)
        logging.info("Admin is: {0}".format(self.admin.name))

        role = discord.utils.find(lambda r: r.name == 'Majn', self.guild.roles)
        channel = self.get_channel(802259577588547604)
        self.Voter = Voter(role, self.guild, channel, self)

    async def on_message(self, message: discord.Message):

        if message.author == self.user:
            return

        if message.embeds:
            await self.check_riptide(message)
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
            await self.close()
            exit(0)

        await self.Voter.handle_message(message)
        await self.Monika.handleMessage(message)
        # await self.Player.handle_message(message)

    async def check_riptide(self, message):
        embeds: list[discord.Embed] = message.embeds
        for music in FILTERED_MUSIC:
            for embed in embeds:
                target = embed.description
                try:
                    if "Now playing" not in embed.title:
                        return
                except TypeError:
                    return
                if music in target:
                    fallback_channel = message.author.voice.channel
                    fuj = self.get_channel(820089925440766026)
                    pattern = re.split("@|>", target)
                    traitor: discord.Member = await self.guild.fetch_member(int(pattern[1]))
                    await message.author.move_to(fuj)
                    await traitor.move_to(fuj)
                    await traitor.send(content="Tohleto tady neprovozujeme, brčálníku!")
                    await sleep(210)
                    try:
                        await message.author.move_to(fallback_channel)
                    except discord.HTTPException:
                        pass
                    return
        return


Bot().run(TOKEN)
