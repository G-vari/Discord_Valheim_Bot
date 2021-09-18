import discord
import requests
from dotenv import load_dotenv
import os
import asyncio

# The dathost server is automatically checked by the bot at this interval
# If nobody is online the server is closed
server_timeout_seconds = 60
# An initial time buffer to allow users to join once the server is started
login_buffer = 300

load_dotenv()

# Login details are stored in a local .env file
# Discord Info
TOKEN= os.getenv("TOKEN")
SERVER_NAME = os.getenv("SERVER_NAME")

# Dathost account info
username = os.getenv("username")
pwrd = os.getenv("pwrd")

# extremely secure valheim server pwrd
server_pwrd = os.getenv("server_pwrd")

# Use intents to allow bot to access the members list
intents = discord.Intents.default()
intents.members = True

# Init connection to discord
client = discord.Client(intents=intents)
client.activate_login_buffer = False

# Start up the bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    print("Servers this bot is connected to:")
    for guild in client.guilds:
        print(guild)
    print("This guild has the following members")
    for member in guild.members:
        print (member.name)

    # Start background task that auto disconnects the server if nobody is online
    await auto_disconnect_server()


# Implement the commands available to users on discord (by writing a message into the chat)
@client.event
async def on_message(message):
    if message.author == client.user: # Prevent bot ("client.user" here ) from replying to itself
        return

    # Start up the server
    if message.content.startswith('$start_server'):

        # Get the dathost server info (assumes there is only one server)
        server = requests.get(
            "https://dathost.net/api/0.1/game-servers",
            auth=(username, pwrd)).json()[0]
        
        requests.post(
            "https://dathost.net/api/0.1/game-servers/%s/start" % server["id"],
            auth=(username, pwrd),
            )

        ip_address = server["custom_domain"] + ":" + str(server["ports"]["game"])

        await message.channel.send("Server starting. You have "+ str(login_buffer)+ " seconds to connect before server auto-stop")
        await message.channel.send("Join game -> Join IP -> Enter IP address -> password")
        await message.channel.send(ip_address)
        await message.channel.send(server_pwrd)

        # Give users a time buffer to login before the auto-disconnect!
        client.activate_login_buffer = True
        

    # Stop the server
    if message.content.startswith('$stop_server'):

        # Get the dathost server info
        server = requests.get(
            "https://dathost.net/api/0.1/game-servers",
            auth=(username, pwrd)).json()[0]
        
        requests.post(
            "https://dathost.net/api/0.1/game-servers/%s/stop" % server["id"],
            auth=(username, pwrd),
            )

        await message.channel.send("Server stopping. Well remembered ;-)")



async def auto_disconnect_server():

    await client.wait_until_ready()

    while not client.is_closed():

        # After just starting the server, give users a minimum time buffer to login before the auto-disconnect!
        if client.activate_login_buffer:
            await asyncio.sleep(login_buffer)
            client.activate_login_buffer = False

        # Check if anybody is connected to the server (and whether the server is running)
        server = requests.get(
                "https://dathost.net/api/0.1/game-servers",
                auth=(username, pwrd)).json()[0]

        if server["players_online"] > 0 or not server["on"]:
            await asyncio.sleep(server_timeout_seconds)
            continue

        # If nobody is connected, close the server, and post a message to the bot-commands channel
        for guild in client.guilds:
            if guild.name == SERVER_NAME:
                break    
        for channel in guild.channels:
            if channel.name == "bot-commands":
                await channel.send("Nobody is online, closing the server")

        print("Auto-disconnecting the Valheim server due to inactivity")
        requests.post(
                "https://dathost.net/api/0.1/game-servers/%s/stop" % server["id"],
                auth=(username, pwrd),
                )

        await asyncio.sleep(server_timeout_seconds)


client.run(TOKEN)
