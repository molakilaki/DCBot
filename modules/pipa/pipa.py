import asyncio

import discord
from discord.ext import commands

ALKOHOL = ["pivo", "pívo", "pivsoň", "piva", "pivečka", "pivu", "pivem", "pullitřík", "půllitřík", "půllitr",
                  "pivko", "rum ", "vodka", "vodku"]


class Hostinsky(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.played_time = 0
        self.timer = None

    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.announcer(470490558713036801))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if "čus" in message.content.lower():
            await message.channel.send("Čest práci soudruhu <@" + str(message.author.id) + ">")

        for key in ALKOHOL:
            if key in message.content.lower():
                await message.channel.send("Už se to nese!! 🍺")

    @commands.command(name="jelimán", hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def give_technik(self, ctx: commands.Context):
        role = self.bot.get_guild(765898623610912809).get_role(783695649488633877)
        try:
            await ctx.author.add_roles(role, reason="Je to borec a tuhle roli si kurva zaslouží!!!")
        except discord.NotFound:
            await ctx.send("Musíš si o ní napsat na správným serveru")

    @commands.Cog.listener()
    async def on_member_update(self, bef: discord.Member, aft: discord.Member):
        if not bef.id == 470490558713036801:
            return

        befact = None
        aftact = None
        for act in bef.activities:
            if act.type == discord.ActivityType.playing:
                befact = act
                break
        for act in aft.activities:
            if act.type == discord.ActivityType.playing:
                aftact = act
                break

        if befact == aftact:
            return
        elif befact is None and (self.timer is None or self.timer.done()):
            self.timer = asyncio.create_task(self.count_oskaros())
        elif aftact is None and self.timer is not None:
            self.timer.cancel()

    async def count_oskaros(self):
        try:
            while True:
                self.played_time = self.played_time + 1
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def announcer(self, memid: int):
        oskar: discord.User = await self.bot.fetch_user(memid)
        while True:
            embed = discord.Embed(title="Tvé dnešní kalící skóre")
            embed.add_field(name="Nahráno", value=str(int(self.played_time/60))+" minut")
            if self.played_time > 14400:
                embed.add_field(name="Dnešní skore", value="Jsi totální závislák")
                embed.colour = discord.Colour.dark_red()
            elif self.played_time > 7200:
                embed.add_field(name="Dnešní skore", value="Tohle je ztráta času i tvého života")
                embed.colour = discord.Colour.dark_orange()
            elif self.played_time > 3600:
                embed.add_field(name="Dnešní skore", value="Hochu, je to s tebou nic moc")
                embed.colour = discord.Colour.gold()
            elif self.played_time > 1800:
                embed.add_field(name="Dnešní skore", value="Představ si kolik jiných věcí jsi mohl dělat...")
                embed.colour = discord.Colour.green()
            else:
                embed.add_field(name="Gratuluji k úspěchu!!!", value="Jen tak dál, to musel být produktivní den")
                embed.colour = discord.Colour.lighter_grey()
            await oskar.send(embed=embed)
            self.played_time = 0
            await asyncio.sleep(86400)




