import discord
from random import shuffle


class Voter:

    def __init__(self, role: discord.Role, guild: discord.Guild, channel: discord.TextChannel, bot: discord.Client):
        self.role_id = role
        self.guild = guild
        self.channel = channel
        self.bot = bot

        self.voting_now = False
        self.members_voted = []
        self.soudce_votes = []

    async def handle_message(self, message: discord.Message):

        if message.content.startswith("-kome") and self.role_id in message.author.roles:
            if self.voting_now:
                await message.channel.send("Volby už probíhají")
                return
            await self.channel.send("@here byly vyhlášeny volby, hlasujte příkazem vote 'hráč' zaslaným mně do soukromé zprávy")
            await self.channel.send("Volby vyhlásil {0}".format(message.author.name))
            self.voting_now = True
            return

        if message.content.startswith("vote ") and self.voting_now and not message.author.id == 470490558713036801:
            if message.author.id in self.members_voted:
                await message.channel.send("Už jsi volil")
                return
            args = message.content.split(" ", 1)
            target = args[1]
            self.members_voted.append(message.author.id)
            self.soudce_votes.append(target)
            await message.channel.send("Zapsán hlas od {0} pro {1}".format(message.author.name, target))

        if message.content.startswith("-results") and self.voting_now:
            await self.channel.send("@here hráč {0} právě ukončil volby".format(message.author.name))
            shuffle(self.members_voted)
            for vote in self.soudce_votes:
                await self.channel.send("Registrován hlas pro {0}".format(vote))
            self.voting_now = False
            self.members_voted.clear()
            self.soudce_votes.clear()
            return
