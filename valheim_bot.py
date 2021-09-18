import discord
import requests
from dotenv import load_dotenv
import os

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

        await message.channel.send("Server starting. Please remember to close it when you're done :-)")
        await message.channel.send("Join game -> Join IP -> Enter IP address -> password")
        await message.channel.send(ip_address)
        await message.channel.send(server_pwrd)
        

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

client.run(TOKEN)
