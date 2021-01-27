import discord
import random
import asyncio
import requests
from json import loads
import os
import logging
import teachers

TOKEN = "ODAxODg5MTExNzQ0NzA4NjQx.YAnPbg.I9PjsuAQF1Tj4HkXbWtKHQ7zmts"
DUB = "./TakZdar.mp3"

VOJTA = 525816801133723658
MARŤA = 772909380139483146

BOBAN_REPLY_CHANCE = 1

POLITISCHE_GESPRACHE = ["trump", "biden", "babiš", "zeman"]

boban_lines = []
r = requests
logging.basicConfig(level=logging.INFO)

try:
    with open("boban.txt", "r", encoding='utf-8') as f:
        for line in f:
            boban_lines.append(line.strip())
        if not boban_lines:
            print("No boban lines!")
        else:
            for line in boban_lines:
                print("loaded boban line: %s" % line)
except FileNotFoundError:
    print("No boban lines!")


marťa_msg_sendone = False

client = discord.Client()

teachers = [teachers.Monika()]


async def proc_webhooks(channel: discord.TextChannel) -> list[discord.Webhook]:
    # V případě že se v kanále nenachází žádný webhook, vytvoří si jeden
    try:
        hooks = await channel.webhooks()
    except discord.Forbidden:
        await channel.send("Zkontroluj moje práva\nPotřebuji Manage Webhooks abych mohl pokračovat")
        return []
    hooks = [hook for hook in hooks if hook.type != discord.WebhookType.channel_follower]

    if not hooks:
        try:
            hooks.append(await channel.create_webhook(name="webhook", reason="Vytvořil si potřebný webhook"))
        except discord.HTTPException:
            print("Chyba při připojování")
    return hooks


@client.event
async def on_ready():
    print("I'm ready! {0.name}".format(client.user))


@client.event
async def on_message(msg: discord.Message):
    global marťa_msg_sendone

    if msg.author == client.user or msg.webhook_id is not None:
        return

    print("{0.created_at}> {0.author.display_name} píše".format(msg))

    # user specific responses
    if msg.author.id == VOJTA:
        if boban_lines and random.random() <= BOBAN_REPLY_CHANCE:
            await msg.channel.send(random.choice(boban_lines))

    elif msg.author.id == MARŤA:
        if marťa_msg_sendone:
            await msg.channel.send("Zdravím!")
            marťa_msg_sendone = False

    if msg.content.startswith("-nick"):
        replacements = ["<@!", ">"]
        if len(msg.content.split()) >= 3:
            args = msg.content.split(" ", 2)
            if args[1].startswith("<@!") and args[1].endswith(">"):
                target = args[1]
                print(target)
                for word in replacements:
                    target = target.replace(word, "")
                target = int(target)
                nick = args[2]
            else:
                await msg.channel.send("Druhý argument musí být člověk jehož jméno měníš.")
                return
        else:
            await msg.channel.send("Příkaz se zadává ve formátu: '-nick @cíl přezdívka'\nzkontroluj svou předchozí zprávu")
            return
        target = await msg.guild.fetch_member(member_id=target)
        await target.edit(nick=nick, reason="change by {0.name}".format(msg.author))
        return

    if msg.content.startswith("-among"):
        url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?format=json&appid=945360"
        info = r.get(url)
        if info.status_code != 200:
            await msg.channel.send("Chyba při získávání informací od Steamu")
        info = loads(info.text)
        stats = info["response"]
        response = "Among Us právě hraje {0} hráčů".format(stats["player_count"])
        await msg.channel.send(response)
        return

    if msg.content.startswith("-end"):
        os.system("shutdown /s /t 180")
        await msg.channel.send("Vypínám.. Dobrou noc")
        quit()

    if msg.content.startswith("-dub"):
        try:
            voice = await msg.author.voice.channel.connect()
        except AttributeError:
            await msg.channel.send("You have to be connected to a voice channel before using this command")
            return
        voice.play(discord.FFmpegPCMAudio(DUB))
        counter = 0
        duration = 41
        while counter < duration:
            await asyncio.sleep(1)
            counter = counter + 1
        await voice.disconnect()
        return

    webhooks = await proc_webhooks(msg.channel)
    for teacher in teachers:
        await teacher.handleMessage(msg, webhooks)


client.run(TOKEN)
