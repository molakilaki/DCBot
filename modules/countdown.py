import discord
from discord.ext import tasks, commands
import datetime
import asyncio


class Countdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message = None
        self.tzone = datetime.timezone(datetime.timedelta(hours=-2))
        self.maturita_start = datetime.datetime(2021, 6, 1, 5, tzinfo=self.tzone)
        self.maturita_end = datetime.datetime(2021, 6, 7, 11, tzinfo=self.tzone)
        self.mozolov = datetime.datetime(2021, 6, 25, 13, tzinfo=self.tzone)
        self.ragnarok = datetime.datetime(2021, 6, 29, 21, tzinfo=self.tzone)
        self.past = datetime.datetime(2014, 9, 1, tzinfo=self.tzone)
        self.countdown.start()

    @tasks.loop(hours=1)
    async def countdown(self):
        now = datetime.datetime.now(tz=self.tzone)
        embed = discord.Embed(title="__Endgame__")
        embed.timestamp = now
        embed.set_footer(text="stepech")
        embed.description = "Máme spolu za sebou " + str((now - self.past).days) + " dní"
        embed.set_image(url="https://media1.tenor.com/images/4a9ab37a73e888867267c16b700ec3dd/tenor.gif?itemid=14938794")
        if abs(self.ragnarok - now) == self.ragnarok - now:
            colour = discord.Colour.blue()
            if abs(self.mozolov - now) == self.mozolov - now:
                colour = discord.Colour.green()
                if abs(self.maturita_end - now) == self.maturita_end - now:
                    colour = discord.Colour.orange()
                    if abs(self.maturita_start - now) == self.maturita_start - now:
                        colour = discord.Colour.red()
                        hodnota = str((self.maturita_start - now).days) + "d, " + str(int((self.maturita_start - now).seconds / 3600)) + "h"
                        embed.add_field(name="Maturita", value=hodnota)
                    else:
                        hodnota = str((self.maturita_end - now).days) + "d, " + str(int((self.maturita_end - now).seconds / 3600)) + "h"
                        embed.add_field(name="Konec maturity", value=hodnota)
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
