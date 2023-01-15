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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


@client.slash_command()
async def download(ctx, url: str, name: str):
    await ctx.respond("Downloading "+name+" from: "+url)
    name += ".webm"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    # create a youtube_dl object and download the audio
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    name = name[:-5] 
    embed = None
    await ctx.channel.send("Finished Dowloading: <"+name+"> From: "+url, embed=embed)
    
@client.slash_command()
async def play(ctx, filename: str):
    channel = ctx.author.voice.channel
    if channel is None:
        await ctx.send("You are not in a voice channel.")
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
       voice = await channel.connect()
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
async def list(ctx):
    await ctx.respond("Getting Music ID List:")
    # Initialize a new embed object
    embed = discord.Embed(title="Current Files", description="")
    i = 0
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f != "txt.py":
            # Add each file name to a new field in the embed
            embed.add_field(name=str(i)+". "+f, value="\u200b", inline=True)
            i =  i + 1

    # Send the embed to the channel
    await ctx.channel.send(embed=embed)

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

client.run('tokenere')
