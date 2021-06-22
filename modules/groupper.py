import discord
from discord.ext import commands

MESSAGE = "Reakcí na tuhle zprávu si přidej roli podle své fakulty:" \
          "\nPro MFF - UK reaguj :one:" \
          "\nPro FIT - ČVUT reaguj :two:" \
          "\nPro FIT - VUT reaguj :three:"


class Grouper(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message: discord.Message = None
        self.fit_role = None
        self.vut_role = None
        self.mff_role = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.message: discord.Message = await self.bot.get_channel(856895425339457549).fetch_message(856896578920906802)
        self.fit_role: discord.Role = self.bot.get_guild(856893883174486036).get_role(856896843232968744)
        self.vut_role: discord.Role = self.bot.get_guild(856893883174486036).get_role(856897029091229716)
        self.mff_role: discord.Role = self.bot.get_guild(856893883174486036).get_role(856897105628626985)

        await self.message.edit(content=MESSAGE)

        needs_reactions = ["1️⃣", "2️⃣", "3️⃣"]

        for reaction in self.message.reactions:
            if reaction.me:
                needs_reactions.remove(reaction.emoji)

        for reaction in needs_reactions:
            await self.message.add_reaction(reaction)
        print("loaded")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        emoji = payload.emoji
        user = payload.member
        if payload.message_id != self.message.id:
            return
        if emoji.name == "1️⃣":
            await user.add_roles(self.mff_role)
        elif emoji.name == "2️⃣":
            await user.add_roles(self.fit_role)
        elif emoji.name == "3️⃣":
            await user.add_roles(self.vut_role)
        else:
            await user.send("Trolíš mě vole?")
