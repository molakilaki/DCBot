import datetime
import discord
from discord.ext import commands, tasks

tzinfo = datetime.timezone(datetime.timedelta(0, 7200))

subjects: dict[str, str] = {
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


schedule: dict[int, list[list[str, str, int, int]]] = {
    1: [
        ["Jakub Šépka", "čj", 8, 0],
        ["Štěpán Pechman", "m", 8, 15],
        ["Šimon Taněv", "m", 8, 30],
        ["Emma Sternbergová", "m", 8, 45],
        ["Anaïs Ariadne Dix", "bi", 9, 0],
        ["Adéla Škvorová", "bi", 9, 15],
        ["Hana Tvrdá", "bi", 9, 30],
        ["Barbora Lubovská", "bi", 9, 45],
        ["Emma Sternbergová", "bi", 10, 0],
        ["Jakub Šépka", "bi", 10, 15],
        ["Anaïs Ariadne Dix", "ch", 10, 30],
        ["Adéla Škvorová", "ch", 10, 45],
        ["Hana Tvrdá", "ch", 11, 00],
        ["Barbora Lubovská", "ch", 11, 15],
        ["Emma Sternbergová", "ch", 11, 30],
        ["Jakub Šépka", "ch", 11, 45],
        ["Anaïs Ariadne Dix", "fj", 12, 30],
        ["Jakub Šépka", "aj", 12, 45],
        ["Adéla Škvorová", "aj", 13, 00],
        ["Štěpán Pechman", "aj", 13, 15],
        ["Šimon Taněv", "aj", 13, 30],
        ["Barbora Lubovská", "aj", 13, 45],
        ["Emma Sternbergová", "aj", 14, 00],
        ["Hana Tvrdá", "aj", 14, 15],
        ["Anaïs Ariadne Dix", "čj", 14, 35],
        ["Adéla Škvorová", "čj", 14, 55],
        ["Barbora Lubovská", "čj", 15, 15],
        ["Emma Sternbergová", "čj", 15, 35],
        ["Štěpán Pechman", "ivt", 15, 55],
        ["Šimon Taněv", "ivt", 16, 20]
    ],
    2: [
        ["Veronika Lišková", "ch", 7, 45],
        ["Dominik Soudil", "ch", 8, 00],
        ["Matěj Havlík", "ch", 8, 15],
        ["Michal Hložánek", "ch", 8, 30],
        ["Diana Katlinskaya", "ch", 8, 45],
        ["Helena Kouwen", "ch", 9, 0],
        ["Jasmína Branná", "ch", 9, 15],
        ["Vojtěch Boháček", "ch", 9, 30],
        ["Dominik Soudil", "bi", 9, 45],
        ["Matěj Havlík", "bi", 10, 0],
        ["Veronika Lišková", "bi", 10, 15],
        ["Diana Katlinskaya", "bi", 10, 30],
        ["Michal Hložánek", "bi", 10, 45],
        ["Helena Kouwen", "bi", 11, 0],
        ["Jasmína Branná", "bi", 11, 15],
        ["Vojtěch Boháček", "nj", 11, 30],
        ["Veronika Lišková", "nj", 11, 45],
        ["Dominik Soudil", "nj", 12, 00],
        ["Matěj Havlík", "aj", 12, 55],
        ["Michal Hložánek", "aj", 13, 10],
        ["Helena Kouwen", "aj", 13, 25],
        ["Jasmína Branná", "aj", 13, 40],
        ["Veronika Lišková", "čj", 14, 00],
        ["Dominik Soudil", "čj", 14, 20],
        ["Matěj Havlík", "čj", 14, 40],
        ["Michal Hložánek", "čj", 15, 00],
        ["Helena Kouwen", "čj", 15, 20],
        ["Jasmína Branná", "čj", 15, 40],
        ["Vojtěch Boháček", "čj", 16, 00]
    ],
    3: [
        ["Michal Poskočil", "aj", 7, 45],
        ["Eliška Kurečková", "aj", 8, 00],
        ["Martin Korba", "aj", 8, 15],
        ["Lea Bilá", "aj", 8, 30],
        ["Martin Vidmar", "aj", 8, 45],
        ["Matyáš Valigura", "aj", 9, 0],
        ["Michal Poskočil", "fy", 9, 15],
        ["Eliška Kurečková", "fy", 9, 30],
        ["Martin Korba", "fy", 9, 45],
        ["Lea Bilá", "zsv", 10, 5],
        ["Eva Závadová", "zsv", 10, 30],
        ["Jan Herczeg", "zsv", 10, 50],
        ["Dominika Hörnerová", "zsv", 11, 45],
        ["Eva Závadová", "nj", 12, 45],
        ["Jan Herczeg", "nj", 13, 00],
        ["Dominika Hörnerová", "aj", 13, 15],
        ["Eva Závadová", "aj", 13, 30],
        ["Jan Herczeg", "aj", 13, 45],
        ["Matyáš Valigura", "čj", 14, 5],
        ["Martin Korba", "čj", 14, 25],
        ["Eva Závadová", "čj", 14, 45],
        ["Dominika Hörnerová", "vv", 15, 5],
        ["Martin Vidmar", "ivt", 15, 30],
        ["Matyáš Valigura", "dg", 15, 55]
    ],
    4: [
        ["Natalia Eiseltová", "nj", 8, 00],
        ["Klára Sieglová", "nj", 8, 15],
        ["Klára Jeřábková", "nj", 8, 30],
        ["Anton Achedžak", "nj", 8, 45],
        ["Anna Adelaide Leschová", "d", 9, 0],
        ["Klára Maříková", "čj", 9, 20],
        ["Klára Sieglová", "čj", 9, 40],
        ["Marlene Kenclová", "čj", 10, 0],
        ["Anna Adelaide Leschová", "čj", 10, 20],
        ["Klára Jeřábková", "aj", 10, 35],
        ["Natalia Eiseltová", "aj", 10, 50],
        ["Klára Sieglová", "aj", 11, 5],
        ["Anna Adelaide Leschová", "aj", 11, 20],
        ["Klára Maříková", "hv", 11, 45],
        ["Marlene Kenclová", "aj", 12, 45],
        ["Anton Achedžak", "aj", 13, 0],
        ["Natalia Eiseltová", "bi", 13, 15],
        ["Klára Jeřábková", "z", 13, 30],
        ["Klára Sieglová", "z", 13, 45],
        ["Marlene Kenclová", "z", 14, 0],
        ["Anna Adelaide Leschová", "z", 14, 15],
        ["Klára Maříková", "tv", 14, 40]
    ]
}


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
                    self.times.append(datetime.datetime(2021, 6, d, exam_blok[2], exam_blok[3], tzinfo=tzinfo))
        self.perma_subjects = self.subjects
        self.times.sort()

    def __str__(self):
        return self.name

    def __gt__(self, other):
        return self.times[0] > other.times[0]

    def __lt__(self, other):
        return not self.__gt__(other)

    def is_today(self, day: int) -> bool:
        return self.times[0].day == day

    def is_done(self) -> bool:
        return self.times == []

    def get_next_time(self) -> datetime.datetime:
        if self.times:
            return self.times[0]
        else:
            return None

    def get_next_subject(self) -> str:
        if self.subjects:
            return self.subjects[0]
        else:
            return None

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
        for day in schedule.values():
            for exam_blok in day:
                if exam_blok[0] not in students_checked:
                    self.students.append(Student(exam_blok[0]))
                    students_checked.append(exam_blok[0])
        self.students.sort()
        self.message = None
        self.odmaturovali = []  # Seznam studentů co už odmaturovali

    @commands.Cog.listener()
    async def on_ready(self):
        self.message: discord.Message = await self.bot.get_channel(839882036407828480).fetch_message(846147778878373918)
        self.core.start()

    @tasks.loop(minutes=2)
    async def core(self):
        embed = discord.Embed(title="Maturita")
        now = datetime.datetime.now(tz=tzinfo)
        embed.timestamp = now

        while (now - self.students[0].get_next_time()) > datetime.timedelta(0, 1800):  # Kontrola jestli už je u zkoušky 15 minut
            self.students[0].check()
            if self.students[0].is_done():  # Kontrola jestli to byla jeho poslední zkouška
                self.odmaturovali.append(self.students[0])
                del self.students[0]
            self.students.sort()
        if len(self.students) == 0:
            embed.title = "Všichni odmaturovali"
            embed.colour = discord.Colour.orange()
            await self.message.edit(embed=embed)
            return

        if self.students[0].is_today(now.day):
            embed = self.next_tomorrow(embed)
        else:
            embed = self.normal_run(embed)

        embed.set_footer(text="stepech")
        await self.message.edit(content=None, embed=embed)

    def next_tomorrow(self, embed: discord.Embed) -> discord.Embed:
        """V přípaadě že daný den již nikdo nematuruje, připraví speciální zprávu"""
        description = "Dnes už nikdo nematuruje"
        embed.description = description

        embed.add_field(name="Dále pokračuje", value="Z" + subjects[self.students[0].get_next_subject()])
        embed.add_field(name=str(self.students[0]), value=str(self.students[0].get_next_time().day) + ". června - " + get_correct_time(self.students[0].get_next_time()))

        students = ""
        for i in range(1, 5):
            try:
                students += str(self.students[i]) + " z" + subjects[self.students[i].get_next_subject()] + "\n"
            except IndexError:
                break
        if students != "":
            embed.add_field(name="Později", value=students, inline=False)
        embed.colour = discord.Colour.dark_gold()
        return self.add_odmaturovali(embed)

    def normal_run(self, embed: discord.Embed) -> discord.Embed:
        """Výpočet pro normální maturitní část dne"""
        embed = embed
        embed = correct_title(embed, self.students[0])

        # Správně nastaví popis zprávy podle předmětů ze kterých se maturuje
        desc = "Z" + subjects[self.students[0].get_next_subject()] + "\n"
        f_subjects = "`" + self.students[0].subjects[0]
        for subject in self.students[0].subjects[1:]:
            f_subjects += " ~ " + subject
        desc += "Celkem maturuje z " + f_subjects + "`"
        embed.description = desc

        # Pochytá výjimky v případě že je student poslední/poslední v daný den
        if len(self.students) == 1:
            embed.add_field(name=str(self.students[0]) + " je poslední", value="Hodně štěstí v budoucím životě")
            return self.add_odmaturovali(embed)
        if not self.students[1].is_today(self.students[0].get_next_time().day):
            embed.add_field(name="Další maturující je zítra", value=str(self.students[1]) + " z" + subjects[self.students[1].get_next_subject()], inline=False)
            return self.add_odmaturovali(embed)

        # Přidá následujícího studenta
        embed.add_field(name="Následuje", value=str(self.students[1]))
        embed.add_field(name="Maturuje", value="Z"+subjects[self.students[1].get_next_subject()])
        embed.add_field(name="Začátek", value="V " + get_correct_time(self.students[1].get_next_time()))

        students = ""
        for i in range(2, 6):
            try:
                students += str(self.students[i]) + " z" + subjects[self.students[i].get_next_subject()] + "\n"
            except IndexError:
                break
        if students != "":
            embed.add_field(name="Později", value=students, inline=False)

        return self.add_odmaturovali(embed)

    def add_odmaturovali(self, embed: discord.Embed) -> discord.Embed:
        """Přidá na konec seznam všech studentů, kteří již odmaturovali"""
        embed = embed
        if not self.odmaturovali:
            return embed
        students_done = ""
        for student in self.odmaturovali:
            students_done += str(student) + "z "
            students_done += "`" + student.subjects[0]
            for subject in student.subjects[1:]:
                students_done += " ~ " + subject
            students_done += "`\n"
        embed.add_field(name="Již odmaturovali (" + str(len(self.odmaturovali)) + "):", value=students_done, inline=False)
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
        embed.title = title
    else:
        title = "Právě maturuje " + str(student)
        embed.title = title
    return embed
