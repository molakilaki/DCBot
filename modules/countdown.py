import discord
from discord.ext import tasks, commands
import datetime
import asyncio

tzone = datetime.timezone(datetime.timedelta(0, 7200))


class Countdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message = None
        self.mozolov = datetime.datetime(2021, 6, 25, 16, tzinfo=tzone)
        self.ragnarok = datetime.datetime(2021, 6, 30, 0, 0, tzinfo=tzone)
        self.past = datetime.datetime(2014, 9, 1, tzinfo=tzone)
        self.countdown.start()

    @tasks.loop(hours=1)
    async def countdown(self):
        now = datetime.datetime.now(tz=tzone)
        embed = discord.Embed(title="__Endgame__")
        embed.timestamp = now
        embed.set_footer(text="stepech")
        embed.description = "Máme spolu za sebou " + str((now - self.past).days) + " dní"
        embed.set_image(url="https://media1.tenor.com/images/4a9ab37a73e888867267c16b700ec3dd/tenor.gif?itemid=14938794")
        if abs(self.ragnarok - now) == self.ragnarok - now > datetime.timedelta(seconds=3500):
            colour = discord.Colour.blue()
            if abs(self.mozolov - now) == self.mozolov - now > datetime.timedelta(seconds=3500):
                colour = discord.Colour.green()
                hodnota = str((self.mozolov - now).days) + "d, " + str(int((self.mozolov - now).seconds / 3600)) + "h"
                embed.add_field(name="Mozolov", value=hodnota)
            hodnota = str((self.ragnarok - now).days) + "d, " + str(int((self.ragnarok - now).seconds / 3600)) + "h"
            embed.add_field(name="Ragnarok", value=hodnota)
        else:
            embed.title = "😭"
            embed.add_field(name="Rád jsem vás poznal", value="Snad se ještě někdy uvidíme")
            colour = discord.Colour.gold()
        embed.colour = colour
        await self.message.edit(content=None, embed=embed)

    @countdown.before_loop
    async def before_cd(self):
        await self.bot.wait_until_ready()
        self.message: discord.Message = await self.bot.get_channel(839882036407828480).fetch_message(839890990856536116)
        await asyncio.sleep((59 - datetime.datetime.now().minute) * 60 + 61 - datetime.datetime.now().second)
