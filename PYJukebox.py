import discord
import youtube_dl
import asyncio
import time
import os

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
        if not result['entries']:
            await ctx.send("No video found.")
            return
        url = result['entries'][0]['url']
        # title = result['entries'][0]['title']

    # Connect to voice channel and play music
    
    if not channel.guild.voice_client:
        await channel.connect()
    # await ctx.respond("playing: "+title)
    voice = channel.guild.voice_client
    voice.play(discord.FFmpegPCMAudio(url))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.2

@client.slash_command()
async def set_volume(ctx, volume: float):
    if volume < 0 or volume > 100:
        await ctx.respond("Volume must be between 0 and 100.")
        return
    voice_client = ctx.guild.voice_client
    if not voice_client:
        ctx.respond("I am not currently playing any music.")
        return
    voice_client.source.volume = volume/100
    await ctx.respond(f"Volume set to {volume}%.")
    return

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
async def stop(ctx):
    ctx.voice_client.stop()

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

client.run('tokenere')
