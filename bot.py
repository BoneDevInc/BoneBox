import discord
import yt_dlp
import ffmpeg
import asyncio
import time
from discord import app_commands
import json

stfu = True

intents = discord.Intents.all()
client = discord.Client(intents = intents)

class MyView(discord.ui.View):
    def __init__(self, person, **kwargs):
        self.person = person
        super().__init__(**kwargs)
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.primary, emoji="😎")
    async def button_callback(self, interaction, button):
        await interaction.response.send_message("You Are Now Verified!")
        await self.person.add_roles(self.person.guild.get_role(1061340808445431920))

@client.event
async def on_message(message):
    global merf_count
    # Check if the message author has a role called "nerd"
    if message.author.bot:
        return
    if "nerd" in [role.name.lower() for role in message.author.roles]:
        await message.add_reaction("🤓")

@client.event
async def on_member_join(person):
    await person.send(f"Thanks for Joining {person.guild.name}", view=MyView(person))

@client.event
async def on_ready():
    await tree.sync() #syncronise bot commands
    print(f'We have logged in as {client.user}')

pvolume = 0.2

tree = app_commands.CommandTree(client)

@tree.command(name="ressetmerf", description="reset the merf count, obviously")
async def resetmerf(interaction):
    global merf_count
    merf_count = 0
    await interaction.response.send_message("Merf count has been reset.")

@tree.command(name="dcmein", description="disconnects you from this channel after [time] minuites")
async def dcmein(interaction, time: float):
    if interaction.user.voice:
        voice_channel = interaction.user.voice.channel
        #voice_client = interaction.voice_client
        if voice_channel and True:
            await interaction.response.send_message(f"Disconnecting {interaction.user.name} in {time} minute(s)...")
            await asyncio.sleep(time * 60)
            await interaction.user.move_to(None)
            await client.get_channel(interaction.channel_id).send(f"{interaction.user.name} has been disconnected from the voice channel.")
    else:
        await interaction.response.send_message("You are not in a voice channel.")


@tree.command(name="play", description="epic koru play command, supports YT URL or search for video")
async def play(interaction, ytvideotitle: str):
    user = interaction.user
    if 'PooPoo' in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message('You have the poopoo role!', ephemeral = stfu)
        return
    channel = interaction.user.voice.channel
    if channel is None:
        await interaction.response.send_message("You are not in a voice channel.", ephemeral = stfu)
        return
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    responsemessage = "Downloading..."
    isurl = True
    ytvideotitle = ytvideotitle.replace("https://youtu.be/", "https://www.youtube.com/watch?v=")
    if not "http" in ytvideotitle:
        if not "://" in ytvideotitle:
            ytvideotitle = f'ytsearch1:{ytvideotitle}'
            isurl = False
            responsemessage = "Searching..."
    print(ytvideotitle)

    await interaction.response.send_message(f"{responsemessage}", ephemeral = stfu)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"{ytvideotitle}", download=False)
        if not isurl:
            if not result['entries']:
                await interaction.followup.send("No video found.")
                return
        if not isurl:
            aquiredvideo = result['entries'][0]
        else:
            aquiredvideo = result
        #print(aquiredvideo)
        url = aquiredvideo['url']
        webpage_url = aquiredvideo['webpage_url']
        duration_string = aquiredvideo['duration_string']
        realduration = aquiredvideo['duration']
        # Connect to voice channel and play music

    await interaction.followup.send(f"Playing, {duration_string}\n{webpage_url}", ephemeral = stfu)
    if not channel.guild.voice_client:
        await channel.connect()
    voice = channel.guild.voice_client
    print(f"{interaction.user} Played {ytvideotitle}.")
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url,before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",options="-vn"))
    source.volume = pvolume
    if voice.is_playing():
        voice.stop()
    voice.play(source)
    print("volume = " + str(pvolume))
    await asyncio.sleep(realduration + 10)
    print("checking if no sound is playing")
    if not voice.is_playing():
        print("disconnecting")
        voice.stop()
        vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
        await vc.disconnect()
    else:
        print(f"voice is playing? {voice.is_playing}")

@tree.command(name="volume", description="sets the volume to [volume] %")
async def volume(interaction, volume: float):
    user = interaction.user
    if 'PooPoo' in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message('You have the poopoo role!', ephemeral = stfu)
        return
    if volume < 0 or volume > 100:
        await interaction.response.send_message("Volume must be between 0 and 100.", ephemeral = stfu)
        return
    voice_client = interaction.guild.voice_client
    if not voice_client:
        await interaction.response.send_message("I am not currently playing any music.", ephemeral = stfu)
        return
    voice_client.source.volume = volume/100
    pvolume = volume/100
    print(f"{interaction.user} set Volume to " + str(pvolume) + ".")
    await interaction.response.send_message(f"Volume set to {volume}%.", ephemeral = stfu)
    return

@tree.command(name="join", description="bot joins your channel")
async def join(interaction):
    if interaction.user.voice:
        user = interaction.user
        if 'PooPoo' in [role.name for role in interaction.user.roles]:
            await interaction.response.send_message('You have the poopoo role!', ephemeral = stfu)
            return
        print(f"{interaction.user} joined the bot.")
        await interaction.response.send_message("Joining: "+str(interaction.user.voice.channel), ephemeral = stfu)
        voice_client = interaction.guild.voice_client
        if not voice_client:
            voice_channel = interaction.user.voice.channel
            await voice_channel.connect()
    else:
        await interaction.response.send_message("You are not in a voice channel.")

@tree.command(name="disconnect", description="bot disconnects from your channel")
async def disconnect(interaction):
    user = interaction.user
    if 'PooPoo' in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message('You have the poopoo role!', ephemeral = stfu)
        return
    print(f"{interaction.user} Disconnected the bot.")
    channel = interaction.user.voice.channel
    vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
    voice_client = channel.guild.voice_client
    await interaction.response.send_message("Disconnected From: "+str(interaction.user.voice.channel), ephemeral = stfu)
    voice_client.stop()
    await vc.disconnect()
    print("Bot disconnected")

@tree.command(name="pause", description="pause the current video")
async def pause(interaction):
    user = interaction.user
    if 'PooPoo' in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message('You have the poopoo role!', ephemeral = stfu)
        return
    print("resume")
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return await interaction.response.send_message("I am not currently playing any music.", ephemeral = stfu)
    if voice_client.is_paused():
        return await interaction.response.send_message("The music is already paused.", ephemeral = stfu)
    voice_client.pause()
    await interaction.response.send_message("Paused the current music.", ephemeral = stfu)

@tree.command(name="stop", description="stop the current video")
async def stop(interaction):
    user = interaction.user
    if 'PooPoo' in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message('You have the poopoo role!', ephemeral = stfu)
        return
    interaction.guild.voice_client.stop()
    await interaction.response.send_message("stopped.", ephemeral = stfu)
    print(f"{interaction.user} stopped playback.")


@tree.command(name="resume", description="resume the current video")
async def resume(interaction):
    user = interaction.user
    if 'PooPoo' in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message('You have the poopoo role!', ephemeral = stfu)
        return
    print("pasue")
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return await interaction.response.send_message("I am not currently playing any music.", ephemeral = stfu)
    if not voice_client.is_paused():
        return await interaction.response.send_message("The music is not paused.", ephemeral = stfu)
    voice_client.resume()
    await interaction.response.send_message("Resumed the current music.", ephemeral = stfu)

client.run('ODY3NTY1OTQzMjkwNDYyMjE4.GAmd_2.RAICT5EMG5gEhc7F3L1iIVHZ_r4_vgHrxTSEDU')