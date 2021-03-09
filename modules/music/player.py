from modules.music.queue import Queue
import discord
import youtube_dl
import os

PREFIX = "!"
PLAY = ["play ", "p "]
DISCONNECT = ["dc", "disconnect", "leave"]


def check_aliases(message: discord.Message.content, aliases: list):
    for alias in aliases:
        alias = PREFIX + alias
        if message.startswith(alias):
            return True
    return False


class Player:
    def __init__(self):
        self.ytdl_options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        self.queue = Queue()
        self.voice_channel = None
        self.paused = False
        self.playing = False

    async def handle_message(self, message: discord.Message):
        if check_aliases(message.content, PLAY):
            args = message.content.split(" ", 1)
            try:
                self.voice_channel: discord.VoiceChannel = await message.author.voice.channel.connect()
            except AttributeError:
                await message.channel.send("Před použitím tohoto příkazu musíš být připojen do hlasového chatu",
                                           delete_after=20.0)
            with youtube_dl.YoutubeDL(self.ytdl_options) as ydl:
                ydl.download([args[1]])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    self.voice_channel.play(discord.FFmpegPCMAudio(file))
            return

        if check_aliases(message.content, DISCONNECT) and self.voice_channel:
            await self.voice_channel.disconnect()
            self.voice_channel = None
            return
