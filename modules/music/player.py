import discord
import youtube_dl
import logging
import asyncio
from random import shuffle
import os

PREFIX = "!"
PLAY = ["play ", "p "]
DISCONNECT = ["dc", "disconnect", "leave"]
QUEUE = ["q", "list", "queue"]
CLEAR = ["clear", "clr"]
SHUFFLE = ["shuffle", "mix"]
LOOP = ["loop", "repeat"]
PAUSE = ["pause"]
SKIP = ["s", "skip", "n", "next"]

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
    # bind to ipv4 since ipv6 addreacses cause issues sometimes
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
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}


def check_aliases(message: discord.Message.content, aliases: list):
    for alias in aliases:
        alias = PREFIX + alias
        if message.startswith(alias):
            return True
    return False


def get_info(arg):
    with youtube_dl.YoutubeDL(stim) as ydl:
        info = ydl.extract_info(arg, download=False)
    return info


def download_song(url: str):
    with youtube_dl.YoutubeDL(ytdl_format_options) as yt:
        yt.download([url])
    return


class Player:
    def __init__(self):
        self.loop = False
        self.voice_client = None
        logging.info("Loaded player")
        self.queue = []
        self.playing_task = None
        self.i = 0

    def remove_song(self, song: int):
        self.queue.remove(self.i + song)

    async def handle_message(self, message: discord.Message):
        if check_aliases(message.content, PLAY):
            await self.play(message)
            return

        if check_aliases(message.content, DISCONNECT) and self.voice_client:
            await self.disconnect(message)
            return

        if check_aliases(message.content, QUEUE):
            await self.print_queue(message)
            return

        if check_aliases(message.content, CLEAR) and message.author.voice.channel == self.voice_client.channel:
            self.queue.clear()
            self.voice_client.stop()
            self.playing_task.cancel()
            await message.channel.send("Cleared queue")
            return

        if check_aliases(message.content, SHUFFLE):
            shuffle(self.queue)
            return

        if check_aliases(message.content, LOOP):
            await self.do_loop(message)
            return

        if check_aliases(message.content, PAUSE):
            await self.pause(message)
            return

        if check_aliases(message.content, SKIP):
            if self.playing_task:
                self.voice_client.stop()
                self.playing_task.cancel()
                self.i += 1
                self.playing_task = asyncio.create_task(self.lets_play_it())
            return

    async def play(self, msg: discord.Message):
        if self.voice_client:
            if not msg.author.voice.channel == self.voice_client.channel:
                await msg.channel.send("Hraju jinde")
                return
        elif not msg.author.voice:
            await msg.channel.send("Nejdřív se připoj, pak budu hrát")
            return
        else:
            self.voice_client: discord.VoiceClient = await msg.author.voice.channel.connect()

        args = msg.content.split(" ", 1)
        data = get_info(args[1])
        await asyncio.sleep(2)
        if data['entries']:
            data = data["entries"][0]

        song = {'title': data['title'],
                'url': data['webpage_url'],
                'id': data['id'],
                'message': msg,
                'duration': data['duration']}

        self.queue.append(song)
        name = song['id'] + ".mp3"
        if name not in os.listdir("./downloads/"):
            download_song(song['url'])

        if self.playing_task and not self.playing_task.done():
            await msg.channel.send("added {0} to the queue - link: {1}".format(song['title'], song['url']))

        else:
            self.playing_task = asyncio.create_task(self.lets_play_it())
        return

    async def disconnect(self, msg: discord.Message):
        if not self.voice_client.channel:
            await msg.channel.send("?!")
        if not msg.author.voice.channel == self.voice_client.channel and len(self.voice_client.channel.members) >= 2:
            await msg.channel.send("Hraju jinde")
            return

        self.voice_client.stop()
        await self.voice_client.disconnect()
        self.queue.clear()
        self.voice_client = None
        return

    async def pause(self, msg: discord.Message):
        if not self.voice_client:
            await msg.channel.send("?!")

        if not self.voice_client.channel == msg.author.voice.channel:
            await msg.channel.send("Jestli si se mnou chceš popovídat, tak se ke mně připoj")

        if not self.voice_client.is_playing() or self.voice_client.is_paused():
            await msg.channel.send("Tak s tímhle už nic neudělám hochu")

        self.voice_client.pause()
        return

    async def do_loop(self, msg: discord.Message):
        self.loop = not self.loop
        if self.loop:
            await msg.channel.send("Smyčka zapnuta")
        else:
            await msg.channel.send("Smyčka vypnuta")
        return

    async def print_queue(self, msg: discord.Message):
        if len(self.queue) > self.i:
            embed = discord.Embed(title="Fronta písniček")
            now_playing = "[" + self.queue[self.i]["title"] + "](" + self.queue[self.i]["url"] + ") | `zadal " + self.queue[self.i]["message"].author.name + "`"
            embed.add_field(name="__Právě hraje:__", value=now_playing, inline=False)
            if len(self.queue) > self.i + 1:
                next_playing = "`1.` [" + self.queue[self.i + 1]["title"] + "](" + self.queue[self.i + 1]["url"] + ") | `zadal " + self.queue[self.i + 1]["message"].author.name + "`\n\n"
                i = 2
                for index in range(self.i + 2, len(self.queue)):
                    next_playing = next_playing + "`" + str(index - self.i) + ".` [" + self.queue[index]["title"] + "](" + self.queue[index]["url"] + ") | `zadal " + self.queue[index]["message"].author.name + "`\n\n"
                    i += 1
                    if i % 10 == 0:
                        embed.add_field(name="__Následují:__", value=next_playing, inline=False)
                        await msg.channel.send(embed=embed)
                        next_playing = ""
                        embed = discord.Embed(title="Pokračování fronty písniček")

                if i % 10 != 0:
                    embed.add_field(name="__Následují:__", value=next_playing, inline=False)
            if embed.fields:
                await msg.channel.send(embed=embed)
        else:
            await msg.channel.send("Fronta je prázdná")

    async def lets_play_it(self):
        while self.i < len(self.queue):
            now_playing = self.queue[self.i]
            name = "./downloads/" + now_playing["id"] + ".mp3"
            await now_playing['message'].channel.send("Teď pojede {0}".format(now_playing['title']))
            self.voice_client.play(discord.FFmpegPCMAudio(name), after=lambda e: print('Player error: %s' % e) if e else None)
            try:
                await asyncio.sleep(int(now_playing['duration']))
            except asyncio.CancelledError:
                return
            self.i += 1
        self.queue.clear()
        self.i = 0
        self.voice_client.stop()
        return
