import discord
from discord.ext import commands

ALKOHOL = ["pivo", "pívo", "pivsoň", "piva", "pivečka", "pivu", "pivem", "pullitřík", "půllitřík", "půllitr",
                  "pivko", "rum ", "vodka", "vodku"]


class Hostinsky(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.played_time = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if "čus" in message.content.lower():
            await message.channel.send("Čest práci soudruhu <@" + str(message.author.id) + ">")

        for key in ALKOHOL:
            if key in message.content.lower():
                await message.channel.send("Už se to nese!! 🍺")
