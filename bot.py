import discord
import logging
import requests as r
from json import loads
from modules.teachers.teachers import Monika
from modules.music.player import Player
from modules.Volby.Volby import Voter

TOKEN = "ODE4ODk5MjkxMDQ4Mzc4NDIx.YEexZQ.KnLZNtYCxu-pwBQzqWAx7oRGoQo"
debug = False

DELETE_TIME = 20.0
ADMIN = 470490558713036801
guild_ids = [498423239119208448]

if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


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
        intents = discord.Intents.all()
        self.guild = None
        self.admin = None
        self.Monika = Monika()
        self.Player = Player()
        self.Voter = None
        self.active_role = None
        self.klacek_role = None
        self.ready = False
        super().__init__(intents=intents, loop=None, **options)

    async def on_ready(self):
        logging.info("I'm ready! {0.name}".format(self.user))

        self.guild: discord.Guild = await self.fetch_guild(498423239119208448)
        logging.info("Connected to {0}".format(self.guild.name))

        self.admin: discord.Member = await self.guild.fetch_member(ADMIN)
        logging.info("Admin is: {0}".format(self.admin.name))

        role = self.guild.get_role(802247704423825478)
        channel = self.get_channel(802259577588547604)
        self.Voter = Voter(role, self.guild, channel, self)

        self.active_role = discord.utils.find(lambda r: r.id == 827625682833637389, self.guild.roles)
        self.klacek_role = discord.utils.find(lambda r: r.id == 770453970165694545, self.guild.roles)
        self.ready = True

    async def on_message(self, message: discord.Message):

        if message.author == self.user:
            return

        if not self.ready:
            return

        try:
            await self.check_activity(message)
        except AttributeError:
            pass

        if message.content.startswith("-nick"):
            logging.debug("Passed onto nickname changer")
            await change_nick(message)
            return

        if message.content.startswith("-among"):
            logging.debug("Passed onto Among Us fc")
            await among_get_active(message.channel)
            return

        if message.content.startswith("!exit!") and message.author == self.admin:
            try:
                await message.channel.send("Jdu spát")
                await self.Player.voice_client.disconnect()
            except AttributeError:
                pass
            await self.close()
            exit(0)

        await self.Voter.handle_message(message)
        await self.Monika.handleMessage(message)
        await self.Player.handle_message(message)

        return

    async def check_activity(self, message: discord.Message) -> None:

        if self.klacek_role in message.author.roles and message.author.status == discord.Status.offline and self.active_role in message.author.roles:
            await message.author.remove_roles(self.active_role, reason="Neviditelný status")
            return
        elif self.klacek_role in message.author.roles and message.author.status == discord.Status.online and self.active_role not in message.author.roles:
            await message.author.add_roles(self.active_role, reason="Viditelný status")
            return
        return


bot = Bot()
bot.run(TOKEN)
