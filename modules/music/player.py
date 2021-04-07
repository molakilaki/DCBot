import discord
from discord.ext import commands
import youtube_dl
import logging
import asyncio
from random import shuffle
import os

MUSIC_CH_IDS = [822070192544022538, 828295231861424161, 783694547716669480]

ytdl_format_options = {
    'outtmpl': 'downloads/%(id)s.mp3',
    'format': 'bestaudio/best',
    'reactrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_addreacs': '0.0.0.0',
    'output': r'youtube-dl',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }]
}

stim = {
    'audioquality': 5,
    'format': 'bestaudio',
    'restrictfilenames': True,
    'flatplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}


def is_music_channel():
    async def predicate(ctx: commands.Context):
        for id in MUSIC_CH_IDS:
            if id == ctx.channel.id:
                return True
        return False

    return commands.check(predicate)


def get_info(arg):
    with youtube_dl.YoutubeDL(stim) as ydl:
        info = ydl.extract_info(arg, download=False)
    return info


def download_song(url: str):
    with youtube_dl.YoutubeDL(ytdl_format_options) as yt:
        yt.download([url])
        logging.info("Downloading song - " + url)
    return


class Queue():
    def __init__(self):
        self._queue = []

    def __getitem__(self, item: int):
        return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return len(self._queue)

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

    def put(self, value: dict):
        self._queue.append(value)


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logging.info("Loaded player")
        self.database = {}

    @commands.command(name="clear")
    @is_music_channel()
    async def clear(self, ctx: commands.Context):
        if ctx.guild.voice_client is None:
            return
        if ctx.author.voice and ctx.author.voice.channel == ctx.guild.voice_client.channel:
            i = 0
            if len(self.database[ctx.guild]["queue"]) < 2:
                await ctx.send("Není nic ve frontě na smazání")
                return
            for i in range(1, len(self.database[ctx.guild]["queue"])):
                self.database[ctx.guild]["queue"].remove(i)

            await ctx.send("Smazáno `" + str(i) + "`")

    @commands.command(name="remove", aliases=["rm"])
    @is_music_channel()
    async def remove_song(self, ctx: commands.Context, song: int):
        songeros = self.database[ctx.guild]["queue"][song]
        self.database[ctx.guild]["queue"].remove(song)
        await ctx.send("Odebráno `{0}` z fronty".format(songeros['title']))

    @commands.command(name="shuffle")
    @is_music_channel()
    async def shuffle(self, ctx: commands.Context):
        if ctx.author.voice and ctx.author.voice.channel == ctx.guild.voice_channel:
            self.database[ctx.guild]["queue"].shuffle()
            await ctx.send("Fronta promíchána")

    @commands.command(name="loop")
    @is_music_channel()
    async def do_loop(self, ctx: commands.Context):
        if ctx.author.voice and ctx.author.voice.channel == ctx.guild.voice_client.channel:
            self.database[ctx.guild]["loop"] = not self.database[ctx.guild]["loop"]
            if self.database[ctx.guild]["loop"]:
                await ctx.send("🔂 Smyčka zapnuta")
            else:
                await ctx.send("➡️ Smyčka vypnuta")
            return

    @commands.command(name="skip", aliases=["next", "n"])
    @is_music_channel()
    async def skip(self, ctx: commands.Context):
        if ctx.guild.voice_client.is_playing and ctx.author.voice.channel == ctx.guild.voice_client.channel:
            ctx.guild.voice_client.stop()
            self.database[ctx.guild]["task"].cancel()
            self.database[ctx.guild]["queue"].remove(0)
            self.database[ctx.guild]["task"] = asyncio.create_task(self.lets_play_it(ctx.guild))
        return

    @commands.command(name="play", aliases=["p"])
    @commands.guild_only()
    @is_music_channel()
    async def play(self, ctx, *, arg=None):
        if not ctx.author.voice:
            await ctx.send("Nejdřív se připoj, pak budu hrát")
            return
        elif ctx.guild.voice_client is None:
            await ctx.author.voice.channel.connect()
            self.database[ctx.guild] = {
                "queue": Queue(),
                "loop": False
            }
        elif ctx.guild.voice_client and not ctx.author.voice.channel == ctx.guild.voice_client.channel:
            await ctx.send("Hraju jinde")
            return
        elif ctx.guild.voice_client.is_paused:
            ctx.guild.voice_client.resume()
            if not arg:
                return
        elif not arg:
            await ctx.send("Zadej název písničky, nebo odkaz")
            return

        await ctx.send(content="🌐 **Vyhledávám:** 🔎 `" + arg + "`", embed=None)
        data = get_info(arg)
        if data['entries']:
            data = data["entries"][0]

        song = {'title': data['title'],
                'url': data['webpage_url'],
                'id': data['id'],
                'message': ctx,
                'duration': int(data['duration'])}

        if not ctx.guild.voice_client:
            return
        self.database[ctx.guild]["queue"].put(song)
        name = str(song['id']) + ".mp3"

        try:
            if name not in os.listdir("./downloads/"):
                download_song(song['url'])
        except FileNotFoundError:
            os.mkdir("/downloads")
            logging.warning("Created 'downloads' folder")

        if "task" in self.database[ctx.guild]:
            embed = discord.Embed(title=song["title"], url=song["url"], colour=discord.Colour.green())
            embed.set_author(name="Přidáno do fronty", icon_url=ctx.author.avatar_url)
            channel = "[" + data["channel"] + "](" + data["channel_url"] + ")"
            embed.add_field(name="Channel", value=channel, inline=True)
            duration = str(int(song["duration"] / 60)) + ":"
            if song["duration"] % 60 < 10:
                duration = duration + "0"
            duration = duration + str(int(song["duration"] % 60))
            embed.add_field(name="Délka", value=duration, inline=True)
            embed.add_field(name="Počet zhlédnutí", value='{:,}'.format(int(data["view_count"])), inline=True)
            embed.set_thumbnail(url=data["thumbnail"])
            embed.add_field(name="Pozice ve frontě", value=str(len(self.database[ctx.guild]["queue"]) - 1))
            await ctx.send(embed=embed)
        else:
            self.database[ctx.guild]["task"] = asyncio.create_task(self.lets_play_it(ctx.guild))
        return

    @commands.command(name="dc")
    @commands.guild_only()
    @is_music_channel()
    async def disconnect(self, ctx: commands.Context):
        if not ctx.guild.voice_client:
            await ctx.send("?!")
        if not ctx.author.voice.channel == ctx.guild.voice_client.channel and len(
                ctx.guild.voice_client.channel.members) < 2:
            await ctx.send("Hraju jinde")
            return

        ctx.guild.voice_client.stop()
        await ctx.guild.voice_client.disconnect()
        del self.database[ctx.guild]
        return

    @commands.command(name="pause")
    @is_music_channel()
    async def pause(self, ctx: commands.Context):
        if not ctx.guild.voice_client:
            await ctx.send("?!")
            return
        if not ctx.guild.voice_client.channel == ctx.author.voice.channel:
            await ctx.send("Jestli si se mnou chceš popovídat, tak se ke mně připoj")
            return

        if not ctx.guild.voice_client.is_playing() or ctx.guild.voice_client.is_paused():
            await ctx.send("Tak s tímhle už nic neudělám hochu")
            return
        ctx.guild.voice_client.pause()
        return

    @commands.command(name="queue", aliases=["q"])
    @commands.guild_only()
    @is_music_channel()
    async def print_queue(self, ctx: commands.Context):
        try:
            queue = self.database[ctx.guild]["queue"]
        except KeyError:
            await ctx.send("Pro tento kanál neexistuje fronta")
            return
        if len(queue) > 0:
            if self.database[ctx.guild]["loop"]:
                loop = "✅"
            else:
                loop = "❌"
            embed = discord.Embed(title="Fronta písniček", colour=discord.Colour.gold())
            now_playing = "[" + queue[0]["title"] + "](" + queue[0]["url"] + ") | `zadal " + queue[0]["message"].author.name + "`"
            embed.add_field(name="__Právě hraje:__", value=now_playing, inline=False)
            if len(queue) > 1:
                i = 1
                next_playing = ""
                for index in range(1, len(queue)):
                    next_playing = next_playing + "`" + str(index) + ".` [" + queue[index]["title"] + "](" + queue[index]["url"] + ") | `zadal " + queue[index]["message"].author.name + "`\n\n"
                    i += 1
                    if i % 10 == 0:
                        embed.add_field(name="__Následují:__", value=next_playing, inline=False)
                        embed.set_footer(text=("🔂Loop:" + loop), icon_url=ctx.author.avatar_url)
                        await ctx.send(embed=embed)
                        next_playing = ""
                        embed = discord.Embed(title="Pokračování fronty písniček")

                if i % 10 != 0:
                    embed.add_field(name="__Následují:__", value=next_playing, inline=False)
            if embed.fields:
                embed.set_footer(text=("🔂Loop:" + loop), icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
        else:
            await ctx.send("Fronta je prázdná")

    async def lets_play_it(self, guild: discord.Guild):
        guild = guild
        while len(self.database[guild]["queue"]) > 0:
            now_playing = self.database[guild]["queue"][0]
            name = "./downloads/" + now_playing["id"] + ".mp3"
            await now_playing['message'].send("▶️ Teď hraje > `{0}`".format(now_playing['title']))
            guild.voice_client.play(discord.FFmpegPCMAudio(name))
            try:
                await asyncio.sleep(int(now_playing['duration']))
            except asyncio.CancelledError:
                return
            if guild.voice_client is None:
                break
            if not self.database[guild]["loop"]:
                self.database[guild]["queue"].remove(0)
            guild.voice_client.stop()
        del self.database[guild]["task"]
        return
