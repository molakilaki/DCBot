import discord
import re
import random
import typing
import asyncio

from mathlex import mathlex, compilators, nodes

class Teacher:
    async def sendMessage(self, message: str, webhook: discord.Webhook):
        await webhook.send(message, username=self.username, avatar_url=self.avatar_url)
    
    def handleMessage(self, message: discord.Message):
        pass

def doEasterEggStalin(tokens: typing.List[mathlex.Token]):
    if (random.random() <= 0.1 and len(tokens) == 3 and 
        tokens[0].kind == "number" and tokens[0].data == 2 and 
        tokens[1].kind == "operator" and tokens[1].data == "+" and 
        tokens[2].kind == "number" and tokens[2].data == 2):
        return True

class Monika(Teacher):
    mathRegex = re.compile(r"(([+\-*\/^\d=!><]+|[a-zA-Z]{0,5}\(.*\d.*\))\s*)+")
    MISTAKE_CHANCE = 0.3
    MSG_CALCULATE_TRY = [
        "Dobrý den, %s, nebo ne?",
        "Zdravím, doufám že se máte dobře, %s.",
        "Takže %s, souhlas? Prosím, mluvte se mnou.",
        "%s  :slight_smile:",
        "Tak jak vám to vyšlo? Mně to vyšlo %s.",
        "Hmmm. %s?",
        "Takže správná odpověď ke %s.",
        "Mně to vyšlo %s, souhlas?",
        "Výsledek má být %s.",
        "Je to %s :slight_smile:"
    ]    
    MSG_CALCULATE_CORRECT = [
        "Teda pardon, %s...",
        "Tak mám to dobře nebo ne? Nemám. Správně to je %s.",
        "Vlastně ne, správná odpověď by byla %s.",
        "Teda vlastně %s... já už mám fakt dost...",
        "Teda tady jsem se spletla. Je to %s, ano?",
        ":woman_facepalming: já jsem blbá. Mělo to vyjít %s, jasné?",
        "Počkat, ne... mělo to být %s, ne?",
        "Zapomeňte na to, co jsem předtím říkala! Je to %s! Vždycky to bylo %s!"
    ]
    MSG_DIVIDE_BY_ZERO = [
        "Nulou dělit nemůžete!",
        "Myslím, že už jste dost staří na to, abyste věděli, že nulou se dělit nedá!",
        "To, že nulou nejde dělit, se učí v druhém ročníku základní školy, ne?",
        "Nulou nedělíme...",
        "Vám nikdo neřekl, že nulou nelze dělit?"
    ]
    MSG_TIRED = [
        "Uklidněte se!",
        "Můžete být prosím zticha?",
        "Mě už z vás třeští hlava!",
        ":squid:",
        "Prosím, ztište se.",
        "Už toho mám dnes dost, povíme si to zítra.",
        "Běžte domů.",
        "Nashledanou!",
        "Už jsem na to moc unavená.",
        "Prosím, nechtě mě napospas mým depresím.",
        "Mějte se fanfárově.",
        "Nechme si to na zítra."
    ]
    MSG_ERROR = [
        "Už jsem stará.",
        "Já to nějak nepobírám.",
        "Vy jste si vymyslel vlastní matematiku, viďte?",
        "Zkuste to říct nějak jinak.",
        "Jsem jediná, kdo nechápe, co se tady snažíte říct?",
        "Co je to za klikiháky?",
        "Nejsem si jistá, jestli to co říkáte dává smysl.",
        "Jsem se do toho nějak zamotala."
    ]
    MSG_CHECK_YES = [
        "To je, myslím, správně.",
        "Máte to dobře.",
        "Jestli se nepletu, tak jste to vypočítal dobře.",
        "Ano, tak by to mělo být.",
        "Dobrá práce.",
        "Gratuluji.",
        "Já věděla, že z vás něco bude!",
        "Haleluja!",
        "Je to tak.",
        "Aspoň jeden dává pozor.",
        "Aspoň někdo tady umí počítat.",
        "Ne! Teda vlastně jo!",
        ":slight_smile:",
        "Nechcete to vzít za mě?",
        "Hurá!",
        "Skvěle.",
        "Přesně tak!",
        "Mám z vás radost!",
        "Jste to poslední, co mě drží nad vodou!"
    ]
    MSG_CHECK_NO = [
        "Dnes jsem pohřbila svou naději, že z vás někdy budou užiteční lidé.(20%)",
        "Nějak jste se splet.",
        "Zkuste to znovu.",
        "Teda vy jste mamlas.(30%)",
        ":woman_facepalming: já se z vás zblázním!",
        "Kéž bych dokázala být tak blbá, jako jste vy!(60%)",
        "A nejste vy náhodou dement?(80%)",   
        "Vy už máte taky dost, viďte?",
        "Vaše hloupost prohlubuje moji depresi.(50%)",
        "Dám vám radu: zkuste použít mozek.",
        "Vaše odpověď neodpovídá uznávaným matematickým konvencím.",
        "Snaha byla.",
        "Snaha byla. Teda alespoň doufám.",
        "Vy jste teda jelito.(25%)",
        "Tak znovu a lépe.",
        "Tudy cesta nevede.",
        "Dovoluji si vyjádřit svůj nesouhlas.",
        "Zamyslete se nad tím, co jste právě řekl.",
        "Zkuste se více soustředit.",
        "Jak pravil Einstein: pouze dvě věci jsou nekonečné. Vesmír a lidská hloupost. U té první si však nejsem tak jist. O té druhé jste mě právě ujistil vy!",
        "Vy jste se dneska asi špatně vyspal, že?",
        "Moc rozumu jste teda nepobral.(25%)",
        "Kdybyste dával pozor, tak byste věděl.",
        "A já myslela že já jsem ten dement!(50%)"
    ]
    MSG_SORRY = [
        "Teda omlouvám se, to jsem přehnala.",
        "Pardon, to jsem nechtěla říct.",
        "Omlouvám se, to bylo ode mě hnusné. Ale příště zkuste použít mozek.",
        "Teda neberte si to osobně, ale už toho mám fakt dost.",
        "Bez urážky.",
        "To mě ulítlo. Nic jsem neřekla.",
        "Jak smažu zprávu?",
        "Teda omlouvám se, nechtěla jsem se vás dotknout.",
        "Odpusťte mi. Poslední dobou je toho na mě nějak moc."
    ]

    def __init__(self):
        self.username = "Monika Barešová"
        self.avatar_url = "https://scontent-prg1-1.xx.fbcdn.net/v/t1.0-9/101985663_3227495353947932_6200059714416410624_o.jpg?_nc_cat=102&ccb=2&_nc_sid=09cbfe&_nc_ohc=1bMHrkYViMMAX_vEkC0&_nc_ht=scontent-prg1-1.xx&oh=075d74b112e02a94a166926e7feb9fec&oe=60322A6B"
        self.isProcessingMessage = False
        self.energy = 100
        self.replenishingTask: typing.Optional[asyncio.Task] = None

    async def replenishEnergyAfter10s(self):        
        try:
            await asyncio.sleep(10)
            self.energy = 100
            print("Monča se vyspala")
        except asyncio.CancelledError:
            pass

    def startReplenishingEnergy(self):
        # resetovat Task, který Monče doplní energii

        if self.replenishingTask != None:
            self.replenishingTask.cancel()
        self.replenishingTask = asyncio.create_task(self.replenishEnergyAfter10s())

    async def handleMessage(self, message: discord.Message, webhooks: list):
        if self.isProcessingMessage:
            return
        self.isProcessingMessage = True

        try:
            await self._handleMessage(message, webhooks)
        finally:
            self.isProcessingMessage = False

    async def _handleMessage(self, message: discord.Message, webhooks: list):
        m = Monika.mathRegex.search(message.content)
        if webhooks and m and re.search(r"\d", m.group(0)) and (re.search(r"[a-zA-Z]", m.group(0)) or re.search(r"[+\-*\/=!^<>]", m.group(0))):
            webhook = webhooks[0]

            await asyncio.sleep(random.random() * 2 + 2)

            if self.energy <= 0:
                await self.sendMessage(random.choice(Monika.MSG_TIRED), webhook)
                return

            self.energy -= random.randint(5, 10)
            self.startReplenishingEnergy()

            try:
                group = m.group(0)
                tokens = mathlex.tokenize(group)

                if doEasterEggStalin(tokens):
                    await self.sendMessage("2 + 2 = 5, jak pravil strýc Štalin!", webhook)
                    return

                node = compilators.compileNode(tokens, compilators.COMPILE_ORDER_WITH_COMPARE)

                if node == None:
                    return

                try:
                    result = node()
                except ZeroDivisionError:
                    await self.sendMessage(random.choice(Monika.MSG_DIVIDE_BY_ZERO), webhook)
                    return

                if isinstance(result, bool):
                    # pokud výsledek je ano nebo ne (kontrola příkladu)

                    if result:
                        # MSG_CHECK_YES
                        await self.sendMessage(random.choice(Monika.MSG_CHECK_YES), webhook)
                    else:
                        # MSG_CHECK_NO
                        msg = random.choice(Monika.MSG_CHECK_NO)
                        sorry_chance = 0

                        # u některých MSG_CHECK_NO zpráv je na konci uvedena šance, že se za ně Monča omluví.
                        percent_match = re.search(r"\((\d+)%\)$", msg) 
                        if percent_match:
                            sorry_chance = float(percent_match.group(1)) / 100 # nastavit šanci na omluvu
                            msg = msg[:-len(percent_match.group(0))] # zkrátit message o to, co odpovídá regexu (na konci)

                        await self.sendMessage(msg, webhook)

                        if random.random() <= sorry_chance:
                            # Mončina omluva
                            await asyncio.sleep(random.random() * 2 + 1)
                            await self.sendMessage(random.choice(Monika.MSG_SORRY), webhook)

                elif isinstance(result, float):
                    # pokud výsledek je číslo (výpočet)

                    # MSG_CALCULATE_TRY

                    # pokud je to celé číslo, převést to na celé číslo
                    if result % 1 == 0:
                        result = int(result)

                    # pokud se monča splete, vygenerovat náhodné číslo od -10 do 10 kromě 0, které k výsledku přičtem
                    mistake = 0
                    if random.random() < Monika.MISTAKE_CHANCE:                        
                        while mistake == 0:
                            mistake = random.randint(-10, 10)
                    
                    # první pokus
                    firstTryWhole = m.group(0) + " = " + str(result + mistake)
                    await self.sendMessage(random.choice(Monika.MSG_CALCULATE_TRY) % firstTryWhole, webhook)

                    # oprava (pokud monča udělala chybu)
                    if mistake != 0:
                        await asyncio.sleep(random.random() * 2 + 1)
                        await self.sendMessage(random.choice(Monika.MSG_CALCULATE_CORRECT) % result, webhook)

                else:
                    await self.sendMessage("Teda teď jste mě dostal.", webhook)

            except Exception as ex:
                print("Monča chybovala: %s, %s" % (type(ex).__name__, ex.args))
                await self.sendMessage(random.choice(Monika.MSG_ERROR), webhook)