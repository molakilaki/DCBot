import discord
from discord.ext import commands

ALKOHOL = ["pivo", "pívo", "pivsoň", "piva", "pivečka", "pivu", "pivem", "pullitřík", "půllitřík", "půllitr",
                  "pivko", "rum ", "vodka", "vodku"]
ELIKURE = ["elikure", "eliška", "kuře", "kure", ]

class Hostinsky(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if "čus" in message.content.lower():
            await message.channel.send("Čest práci soudruhu <@" + str(message.author.id) + ">")

        for key in ALKOHOL:
            if key in message.content.lower():
                await message.channel.send("Už se to nese!! 🍺")
                
        for word in ELIKURE:
            if word in message.content.lower():
                await message.channel.send("Mám chuť na banán")
