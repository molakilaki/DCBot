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
    'outtmpl': '{}',
    'restrictfilenames': True,
    'flatplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    "extractaudio": True,
    "audioformat": "opus",
    'quiet': True,
    'no_warnings': True,
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


async def get_info(arg):
    ytdl = youtube_dl.YoutubeDL(stim)
    return ytdl.extract_info(arg, download=False)


class Player:
    def __init__(self):
        self.loop = False
        self.voice_client = None
        logging.info("Loaded player")
        self.queue = []
        self.playing_task = None

    def remove_song(self, song: int):
        self.queue.remove(song)

    async def handle_message(self, message: discord.Message):
        if check_aliases(message.content, PLAY):
            await self.play(message, self.queue)
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

    async def play(self, msg: discord.Message, queue):
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
        data = await get_info(args[1])
        if 'entries' in data:
            data = data["entries"][0]

        song = {'title': data['title'], 'url': data['webpage_url'], 'id': data['id'], 'channel': msg.channel, 'duration': data['duration']}

        queue.append(song)
        name = song['id'] + ".mp3"
        if name not in os.listdir("./downloads/"):

            yt = youtube_dl.YoutubeDL(ytdl_format_options)
            yt.download([song['url']])

        self.queue = queue
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
        if self.queue:
            for song in self.queue:
                await msg.channel.send(song)

    async def lets_play_it(self):
        i = 0
        while i < len(self.queue):
            now_playing = self.queue[i]
            name = "./downloads/" + now_playing["id"] + ".mp3"
            await now_playing['channel'].send("Teď pojede {0}".format(now_playing['title']))
            self.voice_client.play(discord.FFmpegPCMAudio(name), after=lambda e: print('Player error: %s' % e) if e else None)
            await asyncio.sleep(int(now_playing['duration']))
            i += 1
        self.queue.clear()
        return

