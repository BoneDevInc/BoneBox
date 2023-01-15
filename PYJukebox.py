import discord
import youtube_dl
import asyncio
import time
import os

dir = "/test/"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Bot()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
@client.slash_command()
async def play(ctx, filename: str):
    channel = ctx.author.voice.channel
    if channel is None:
        await ctx.respond("You are not in a voice channel.")
        return
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'ytsearch1:{filename}', download=False)
        url = result['entries'][0]['url']

    # Connect to voice channel and play music
    
    if not channel.guild.voice_client:
        await channel.connect()
    ctx.respond("playing "+url)
    voice = channel.guild.voice_client
    voice.play(discord.FFmpegPCMAudio(url))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.5

@client.slash_command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await ctx.respond("Joining: "+str(ctx.author.voice.channel))
    if not channel.guild.voice_client:
        await channel.connect()

@client.slash_command()
async def disconnect(ctx):
    channel = ctx.author.voice.channel
    vc = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    voice_client = channel.guild.voice_client
    await ctx.respond("Disconnected From: "+str(ctx.author.voice.channel))
    voice_client.stop()
    await vc.disconnect()
    print("Bot disconnected")

@client.slash_command()
async def pause(ctx):
    print("resume")
    voice_client = ctx.guild.voice_client
    if not voice_client:
        return await ctx.respond("I am not currently playing any music.")
    if voice_client.is_paused():
        return await ctx.respond("The music is already paused.")
    voice_client.pause()
    await ctx.respond("Paused the current music.")

@client.slash_command()
async def resume(ctx):
    print("pasue")
    voice_client = ctx.guild.voice_client
    if not voice_client:
        return await ctx.respond("I am not currently playing any music.")
    if not voice_client.is_paused():
        return await ctx.respond("The music is not paused.")
    voice_client.resume()
    await ctx.respond("Resumed the current music.")

@client.slash_command()
async def rmall(ctx):
    async for message in ctx.channel.history(limit=None):
        if message.content.startswith("pls"):
            print(str(message))
            await message.delete()

client.run('harhar token here')
