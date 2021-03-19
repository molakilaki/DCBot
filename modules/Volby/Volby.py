import discord
from random import shuffle
from asyncio import sleep


class Voter:

    def __init__(self, role: discord.Role, guild: discord.Guild, channel: discord.TextChannel, bot: discord.Client):
        self.role = role
        self.guild = guild
        self.channel = channel
        self.bot = bot

        self.voting_now = False
        self.members_voted = []
        self.soudce_votes = []
        self.filtered_votes = []

    async def handle_message(self, message: discord.Message):

        if message.content.startswith("-kome") and self.role in message.author.roles:
            if self.voting_now:
                await message.channel.send("Volby už probíhají")
                return
            await self.channel.send(
                "@here byly vyhlášeny volby, hlasujte příkazem vote 'hráč' zaslaným mně do soukromé zprávy")
            await self.channel.send("Volby vyhlásil {0}".format(message.author.name))
            self.voting_now = True
            return

        if message.content.startswith("vote ") and self.voting_now:
            if message.author.id in self.members_voted:
                await message.channel.send("Už jsi volil")
                return
            if message.author in self.filtered_votes:
                await message.channel.send("Jsi v seznamu nominovaných. Nemůžeš v těchto volbách volit.")
                return
            args = message.content.split(" ", 1)
            target = args[1]
            self.members_voted.append(message.author.id)
            self.soudce_votes.append(target)
            await message.channel.send("Zapsán hlas od {0} pro {1}".format(message.author.name, target))
            return

        if message.content.startswith("-results") and self.voting_now and self.role in message.author.roles:
            await self.channel.send("@here hráč {0} právě ukončil volby".format(message.author.name))
            shuffle(self.soudce_votes)
            for vote in self.soudce_votes:
                await self.channel.send("Registrován hlas pro {0}".format(vote))
                await sleep(2)
            await self.channel.send("To jsou všechny registrované hlasy")
            self.voting_now = False
            self.members_voted.clear()
            self.soudce_votes.clear()
            if self.filtered_votes:
                self.filtered_votes.clear()
                await self.channel.send("Nominace vyresetovány pro příští volby")
            return

        if message.content.startswith("-nominuji") and not self.voting_now and self.role in message.author.roles:
            for mention in message.mentions:
                self.filtered_votes.append(mention)
                await self.channel.send("Nominován {0}. Nominaci provedl {1}".format(mention.display_name, message.author.name))
            if len(self.filtered_votes) > 2:
                await self.channel.send("Bacha, seznam nominovaných je delší než má být.\nMažu všechny nominované lidi a nominuj je prosím znova.")
                self.filtered_votes.clear()
            return
        return