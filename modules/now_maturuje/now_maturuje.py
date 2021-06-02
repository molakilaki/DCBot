import datetime
import discord
from discord.ext import commands, tasks

import os
from modules.now_maturuje import schedule_reader

tzinfo = datetime.timezone(datetime.timedelta(0, 7200))

subjects = {
    "čj": " Českého jazyka",
    "m": " Matematiky",
    "bi": " Biologie",
    "ch": " Chemie",
    "fj": " Francouzského jazyka",
    "aj": " Anglického jazyka",
    "ivt": " Informatiky",
    "nj": " Německého jazyka",
    "fy": " Fyziky",
    "zsv": "e Základů společenských věd",
    "dg": " Deskriptivní geometrie",
    "vv": " Výtvarné výchovy",
    "d": " Dějepisu",
    "hv": " Hudební výchovy",
    "z": "e Zeměpisu",
    "tv": " Tělesné výchovy"
}


schedule = schedule_reader.read_schedule(
    # chceme vzít soubor ve stejném adresáři, v němž je aktuální modul:
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedule.csv") 
)


class Student:
    def __init__(self, name: str):
        self.name: str = name  # Jméno studenta
        self.subjects: list[str] = []  # Seznam předmětů ze kterých student maturuje
        self.times: list[datetime.datetime] = []  # Individuální časy společně s dny každého testu
        d = 0
        for day in schedule.values():
            d += 1
            for exam_blok in day:
                if exam_blok[0] == self.name:
                    self.subjects.append(exam_blok[1])
                    self.times.append(datetime.datetime(2021, 6, d, int(exam_blok[2]), int(exam_blok[3]), tzinfo=tzinfo))
        self.perma_subjects = self.subjects.copy()
        self.times.sort()

    def __str__(self):
        return self.name

    def __gt__(self, other):
        return self.times[0] > other.times[0]

    def __lt__(self, other):
        return not self.__gt__(other)

    def is_today(self, day: int) -> bool:
        return self.times[0].day <= day

    def is_done(self) -> bool:
        return self.times == []

    def get_next_time(self) -> datetime.datetime:
        if self.times:
            return self.times[0]

    def get_next_subject(self) -> str:
        if self.subjects:
            return self.subjects[0]

    def get_subjects(self) -> list:
        return self.perma_subjects

    def check(self):
        del self.times[0]
        del self.subjects[0]


class Displayer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.students = []
        students_checked = []
        self.days = []
        try:
            for day in schedule.values():
                for exam_blok in day:
                    if exam_blok[0] not in students_checked:
                        self.students.append(Student(exam_blok[0]))
                        students_checked.append(exam_blok[0])
        except RuntimeError:
            self.cog_unload()
            return
        except FileNotFoundError:
            self.cog_unload()
            return

        self.students.sort()
        self.message = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.message: discord.Message = await self.bot.get_channel(839882036407828480).fetch_message(846147778878373918)
        self.core.start()

    @tasks.loop(minutes=1)
    async def core(self):
        embed = discord.Embed(title="Maturita")
        now = datetime.datetime.now(tz=tzinfo)
        embed.timestamp = now

        while (now - self.students[0].get_next_time()) > datetime.timedelta(0, 900):  # Kontrola jestli už je u zkoušky 15 minut
            self.students[0].check()
            if self.students[0].is_done():  # Kontrola jestli to byla jeho poslední zkouška
                del self.students[0]
            self.students.sort()
        if len(self.students) == 0:
            embed.title = "Všichni odmaturovali"
            embed.colour = discord.Colour.orange()
            await self.message.edit(embed=embed)
            return

        if not self.students[0].is_today(now.day):
            embed = self.next_tomorrow(embed)
        else:
            embed = self.normal_run(embed)

        embed.set_footer(text="stepech & vidmartin")
        await self.message.edit(content=None, embed=embed)

    def next_tomorrow(self, embed: discord.Embed) -> discord.Embed:
        """V přípaadě že daný den již nikdo nematuruje, připraví speciální zprávu"""
        description = "Dnes už nikdo nematuruje"
        embed.description = description

        # Přidá následujícího maturanta
        embed.add_field(name="Dále pokračuje", value="Z" + subjects[self.students[0].get_next_subject()])
        embed.add_field(name=str(self.students[0]), value=str(self.students[0].get_next_time().day) + ". června - " + get_correct_time(self.students[0].get_next_time()))

        # Přidá pár studentů která maturují později
        students = ""
        for i in range(1, 4):
            try:
                students += str(self.students[i]) + " z" + subjects[self.students[i].get_next_subject()] + "\n"
            except IndexError:
                break
        if students != "":
            embed.add_field(name="Později", value=students, inline=False)
        embed.colour = discord.Colour.dark_gold()
        return embed

    def normal_run(self, embed: discord.Embed) -> discord.Embed:
        """Výpočet pro normální maturitní část dne"""
        embed = embed
        embed = correct_title(embed, self.students[0])

        # Správně nastaví popis zprávy podle předmětů ze kterých se maturuje
        desc = "Z" + subjects[self.students[0].get_next_subject()] + "\n"
        f_subjects = "`" + self.students[0].perma_subjects[0]
        for subj in self.students[0].perma_subjects[1:]:
            f_subjects += " ~ " + subj
        desc += "Celkem maturuje z " + f_subjects + "`"
        embed.description = desc

        # Pochytá výjimky v případě že je student poslední/poslední v daný den
        if len(self.students) == 1:
            embed.add_field(name=str(self.students[0]) + " je poslední", value="Hodně štěstí v budoucím životě")
            return embed
        if not self.students[1].is_today(self.students[0].get_next_time().day):
            embed.add_field(name="Další maturující je zítra", value=str(self.students[1]) + " z" + subjects[self.students[1].get_next_subject()], inline=False)
            return embed

        # Přidá následujícího studenta
        embed.add_field(name="Následuje", value=str(self.students[1]))
        embed.add_field(name="Maturuje", value="Z"+subjects[self.students[1].get_next_subject()])
        embed.add_field(name="Začátek", value="V " + get_correct_time(self.students[1].get_next_time()))

        # Přidá pár studentů nakonec, kteří maturují později
        students = ""
        for i in range(2, 5):
            try:
                students += str(self.students[i]) + " z" + subjects[self.students[i].get_next_subject()] + "\n"
            except IndexError:
                break
        if students != "":
            embed.add_field(name="Později", value=students, inline=False)

        return embed


def get_correct_time(time: datetime.datetime) -> str:
    """Vezme si čas ve formátu datetime a vrátí string HH.MM"""
    hour = str(time.hour)
    if time.minute < 10:
        minute = "0" + str(time.minute)
    else:
        minute = str(time.minute)
    return hour + ":" + minute


def correct_title(embed: discord.Embed, student: Student) -> discord.Embed:
    """Upraví titul zprávy v případě že se student teprve maturovat chystá"""
    embed = embed
    now = datetime.datetime.now(tz=tzinfo)
    if now < student.get_next_time():
        title = str(student) + " se chystá maturovat v " + get_correct_time(student.get_next_time())
    else:
        title = "Právě maturuje " + str(student)
    embed.title = title
    return embed
