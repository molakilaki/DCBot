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


class Queue(asyncio.Queue):
    pass


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.loop = False
        self.bot = bot
        logging.info("Loaded player")
        self.queue = []
        self.playing_task = None
        self.i = 0

    @commands.command(name="remove", aliases=["rm"])
    @is_music_channel()
    async def remove_song(self, ctx: commands.Context, song: int):
        song = self.queue.pop(self.i + song)
        await ctx.send("Odebráno `{0}` z fronty".format(song['title']))

    @commands.command(name="shuffle")
    @is_music_channel()
    async def shuffle(self, ctx: commands.Context):
        if len(self.queue) <= self.i:
            return
        queue = self.queue[self.i:]
        self.i = 0
        shuffle(queue)
        self.queue = queue
        await ctx.send("Fronta promíchána")

    @commands.command(name="loop")
    @is_music_channel()
    async def do_loop(self, ctx: commands.Context):
        self.loop = not self.loop
        if self.loop:
            await ctx.send("Smyčka zapnuta")
        else:
            await ctx.send("Smyčka vypnuta")
        return

    @commands.command(name="skip", aliases=["next", "n"])
    @is_music_channel()
    async def skip(self, ctx: commands.Context, arg: int = 1):
        if ctx.guild.voice_client.is_playing:
            ctx.guild.voice_client.stop()
            self.playing_task.cancel()
            self.i += arg
            self.playing_task = asyncio.create_task(self.lets_play_it())
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
        elif ctx.guild.voice_client and not ctx.author.voice.channel == ctx.guild.voice_client.channel:
            await ctx.send("Hraju jinde")
            return
        elif ctx.guild.voice_client.is_paused:
            ctx.guild.voice_client.resume()
            return
        elif not arg:
            await ctx.send("Zadej název písničky, nebo odkaz")
            return

        await ctx.send(content="**Vyhledávám:** `" + arg + "`", embed=None)
        data = get_info(arg)
        await asyncio.sleep(2)
        if data['entries']:
            data = data["entries"][0]

        song = {'title': data['title'],
                'url': data['webpage_url'],
                'id': data['id'],
                'message': ctx,
                'duration': data['duration']}

        if not ctx.guild.voice_client:
            return
        self.queue.append(song)
        name = song['id'] + ".mp3"

        try:
            if name not in os.listdir("./downloads/"):
                download_song(song['url'])
        except FileNotFoundError:
            os.mkdir("/downloads")
            logging.warning("Created 'downloads' folder")

        if self.playing_task and not self.playing_task.done():
            await ctx.send("added {0} to the queue - link: {1}".format(song['title'], song['url']))
        else:
            self.playing_task = asyncio.create_task(self.lets_play_it())
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
        self.queue.clear()
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
        if len(self.queue) > self.i:
            embed = discord.Embed(title="Fronta písniček")
            now_playing = "[" + self.queue[self.i]["title"] + "](" + self.queue[self.i]["url"] + ") | `zadal " + \
                          self.queue[self.i]["message"].author.name + "`"
            embed.add_field(name="__Právě hraje:__", value=now_playing, inline=False)
            if len(self.queue) > self.i + 1:
                next_playing = "`1.` [" + self.queue[self.i + 1]["title"] + "](" + self.queue[self.i + 1][
                    "url"] + ") | `zadal " + self.queue[self.i + 1]["message"].author.name + "`\n\n"
                i = 2
                for index in range(self.i + 2, len(self.queue)):
                    next_playing = next_playing + "`" + str(index - self.i) + ".` [" + self.queue[index][
                        "title"] + "](" + self.queue[index]["url"] + ") | `zadal " + self.queue[index][
                                       "message"].author.name + "`\n\n"
                    i += 1
                    if i % 10 == 0:
                        embed.add_field(name="__Následují:__", value=next_playing, inline=False)
                        await ctx.send(embed=embed)
                        next_playing = ""
                        embed = discord.Embed(title="Pokračování fronty písniček")

                if i % 10 != 0:
                    embed.add_field(name="__Následují:__", value=next_playing, inline=False)
            if embed.fields:
                await ctx.send(embed=embed)
        else:
            await ctx.send("Fronta je prázdná")

    async def lets_play_it(self):
        now_playing = None
        while self.i < len(self.queue):
            now_playing = self.queue[self.i]
            name = "./downloads/" + now_playing["id"] + ".mp3"
            await now_playing['message'].send("Teď pojede {0}".format(now_playing['title']))
            now_playing['message'].guild.voice_client.play(discord.FFmpegPCMAudio(name))
            try:
                await asyncio.sleep(int(now_playing['duration']))
            except asyncio.CancelledError:
                return
            self.i += 1
        self.queue.clear()
        self.i = 0
        if now_playing:
            now_playing['message'].guild.voice_client.stop()
        return
