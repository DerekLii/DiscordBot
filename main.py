from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Message, FFmpegPCMAudio
from discord.ext import commands
from responses import get_response
import yt_dlp as youtube_dl

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
bot: commands.Bot = commands.Bot(command_prefix='!', intents=intents)

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')

# STEP 4: HANDLING INCOMING MESSAGE
@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return

    # Process commands first
    await bot.process_commands(message)

    # If the message was a command, skip further handling
    if message.content.startswith(bot.command_prefix):
        return
    
    # Your custom message handling logic for non-command messages
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

# STEP 5: VOICE COMMANDS

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined {channel}")
    else:
        await ctx.send("You are not connected to a voice channel.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("I'm not connected to any voice channel.")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.send("I'm not connected to a voice channel.")
        return

    # Download the video
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    # Play the audio
    ctx.voice_client.stop()
    ctx.voice_client.play(FFmpegPCMAudio(filename))

    await ctx.send(f'Now playing: {info["title"]}')

# STEP 6: MAIN ENTRY POINT
def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
