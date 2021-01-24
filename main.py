import discord
import random
import os.path

import teachers

TOKEN = "ODAxODg5MTExNzQ0NzA4NjQx.YAnPbg.I9PjsuAQF1Tj4HkXbWtKHQ7zmts"

VOJTA = 525816801133723658
MARŤA = 772909380139483146
ŠTĚPA = 470490558713036801

BOBAN_REPLY_CHANCE = 1

POLITISCHE_GESPRACHE = ["trump", "biden", "babiš", "zeman"]

boban_lines = []

if os.path.exists("boban.txt"):
    for line in open("boban.txt", "r"):
        boban_lines.append(line.strip())
    if not boban_lines:
        print("No boban lines!")
    else:
        for line in boban_lines:
            print("loaded boban line: %s" % line)

marťa_msg_sendone = False

client = discord.Client()

teachers = [teachers.Monika()]

@client.event
async def on_ready():
    print("I'm ready!")

@client.event
async def on_message(msg):
    global marťa_msg_sendone

    if msg.author == client.user or msg.webhook_id != None:
        return

    print("%s píše!" % msg.author.name)

    # user specific responses
    if msg.author.id == VOJTA:
        if boban_lines and random.random() <= BOBAN_REPLY_CHANCE:
            await msg.channel.send(random.choice(boban_lines))

    elif msg.author.id == MARŤA:
        if marťa_msg_sendone:
            await msg.channel.send("Zdravím!")
            marťa_msg_sendone = False

    elif msg.author.id == ŠTĚPA:
        if any((s in msg.content.lower()) for s in POLITISCHE_GESPRACHE):
            await msg.channel.send("Šťépo, netahej sem politiku...")      

    webhooks = await msg.channel.webhooks()

    for teacher in teachers:
        await teacher.handleMessage(msg, webhooks)

client.run(TOKEN)