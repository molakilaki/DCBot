import discord
import re
import random
import typing
import asyncio

class Teacher:
    async def sendMessage(self, message: str, webhook: discord.Webhook):
        await webhook.send(message, username = self.username, avatar_url = self.avatar_url)
    
    def handleMessage(self, message: discord.Message):
        pass

class Monika(Teacher):
    mathRegex = re.compile("(\d+(\.\d+)?)\s*([\+\-\*\/])\s*(\d+(\.\d+)?)")
    responses = [
        "Dobrý den, %s, nebo ne?",
        "Zdravím, doufám že se máte dobře, %s.",
        "Takže %s, souhlas? Prosím, mluvte se mnou.",
        "%s  :)",
        "Tak jak vám to vyšlo? Mně to vyšlo %s.",
        "Hmmm. %s?"
    ]
    mistakeChance = 0.3
    corrections = [
        "Teda pardon, %s...",
        "Tak mám to dobře nebo ne? Nemám. Správně to je %s.",
        "Vlastně ne, správná odpověď by byla %s.",
        "Teda vlastně %s... já už mám fakt dost..."
    ]
    divisionByZeroErrors = [
        "Nulou dělit nemůžete!",
        "Myslím, že už jste dost staří na to, abyste věděli, že nulou se dělit nedá!",
        "To, že nulou nejde dělit, se učí v druhém ročníku základní školy, ne?"
    ]

    def __init__(self):
        self.username = "Monika Barešová"
        self.avatar_url = "https://scontent-prg1-1.xx.fbcdn.net/v/t1.0-9/101985663_3227495353947932_6200059714416410624_o.jpg?_nc_cat=102&ccb=2&_nc_sid=09cbfe&_nc_ohc=1bMHrkYViMMAX_vEkC0&_nc_ht=scontent-prg1-1.xx&oh=075d74b112e02a94a166926e7feb9fec&oe=60322A6B"

    async def handleMessage(self, message: discord.Message, webhooks: list):
        m = Monika.mathRegex.search(message.content)
        if webhooks and m:
            l = float(m.group(1))
            r = float(m.group(4))

            op = m.group(3)

            if op == "/" and r == 0:
                await self.sendMessage(random.choice(Monika.divisionByZeroErrors), webhooks[0])
                return

            result = {
                "+": lambda: l + r,
                "-": lambda: l - r,
                "*": lambda: l * r,
                "/": lambda: l / r
            }[op]()

            if result % 1 == 0:
                result = int(result)

            doMistake = random.random() <= Monika.mistakeChance
            final = result + (random.randint(-10, 10) if doMistake else 0)
            answer = m.group(0) + " = " + str(final)
            response = random.choice(Monika.responses) % answer

            await self.sendMessage(response, webhooks[0])

            if doMistake:
                correction = random.choice(Monika.corrections) % result
                await asyncio.sleep(random.random() * 2 + 2)
                await self.sendMessage(correction, webhooks[0])

                if final == result:
                    await asyncio.sleep(random.random() * 2 + 2)
                    await self.sendMessage("Teda to bylo vlastně to co jsem původně říkala, že? No vidíte to.", webhooks[0])