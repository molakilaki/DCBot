import discord
from discord.ext import commands

MESSAGE = "Reakcí na tuhle zprávu si přidej roli podle své fakulty:" \
          "\nPro MFF - UK reaguj :one:" \
          "\nPro FIT - ČVUT reaguj :two:" \
          "\nPro odebrání role kontaktuj <@470490558713036801> nebo <@273172762330267650>"


class Grouper(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message: discord.Message = None
        self.fit_role = None
        self.mff_role = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.message: discord.Message = await self.bot.get_channel(856895425339457549).fetch_message(856896578920906802)
        self.fit_role: discord.Role = self.bot.get_guild(856893883174486036).get_role(856896843232968744)
        self.mff_role: discord.Role = self.bot.get_guild(856893883174486036).get_role(856897105628626985)

        await self.message.edit(content=MESSAGE)

        needs_reactions = ["1️⃣", "2️⃣"]

        for reaction in self.message.reactions:
            if reaction.me:
                needs_reactions.remove(reaction.emoji)

        for reaction in needs_reactions:
            await self.message.add_reaction(reaction)

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
        else:
            await user.send("Trolíš mě vole?")
