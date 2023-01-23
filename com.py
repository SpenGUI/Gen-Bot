import discord
from discord.ext import commands
from discord import app_commands
import requests
import math
import ccxt
import time
import asyncio
import datetime


# Replace YOUR_BOT_TOKEN with your actual bot token
bot = commands.Bot(command_prefix=['!', '/'], description='A simple trading bot', intents=discord.Intents.all())

# Connect to the cryptocurrency exchange
exchange = ccxt.binance()

# Define the threshold for price changes (in percentage)
THRESHOLD = 0.000000000000000000000000000001

# A list to store the subscribers
subscribers = []

# Discord server and channel ID
SERVER_ID = 941069171607867392
CHANNEL_ID = 1061460237254672404
ROLE_NAME = "BitCoin Subscriber"

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(bot.get_guild(SERVER_ID),bot.get_channel(CHANNEL_ID))

@bot.command(name="subscribe", description = "Subscribe to see bitcoin Alerts!")
async def subscribe(ctx):
    """Subscribe to Bitcoin price alerts"""
    # Add the user to the list of subscribers
    if ctx.message.author not in subscribers:
        subscribers.append(ctx.message.author)
        role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)
        await ctx.message.author.add_roles(role)
        await ctx.send(f'{ctx.message.author.display_name} you are now subscribed to Bitcoin price alerts and have been given the BitCoin Subscriber role')
    else:
        await ctx.send(f'{ctx.message.author.display_name} you are already subscribed to Bitcoin price alerts')


@bot.command(name="unsubscribe", description = "Unsubscribe from Bitcoin price alerts")
async def unsubscribe(ctx):
    # Remove the user from the list of subscribers
    if ctx.message.author in subscribers:
        subscribers.remove(ctx.message.author)
        role = discord.utils.get(ctx.guild.roles, name="BitCoin Subscriber")
        await ctx.message.author.remove_roles(role)
        await ctx.send(f'{ctx.message.author.display_name} you are now unsubscribed from Bitcoin price alerts and the BitCoin Subscriber role has been removed')
    else:
        await ctx.send(f'{ctx.message.author.display_name} you are not subscribed to Bitcoin price alerts')


running = False


is_alerts_running = False

@bot.command(name="alerts", description = "Start checking the price of Bitcoin and alerting subscribers if it changes by more than " + str(THRESHOLD) + "%")
async def alerts(ctx):
    channel = bot.get_guild(SERVER_ID).get_channel(CHANNEL_ID)
    global running
    global is_alerts_running
    if is_alerts_running:
        await ctx.send("Alerts are already running.")
        return
    is_alerts_running = True
    running = True
    ticker = exchange.fetch_ticker('BTC/GBP')
    current_price = ticker['last']
    while running:
        ticker = exchange.fetch_ticker('BTC/GBP')
        await asyncio.sleep(10)
        latest_price = ticker['last']
        change = ((latest_price - current_price) / current_price) * 100
        if change > THRESHOLD:
            for user in subscribers:
                await user.send(f"Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")
            await channel.send(f"Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")
        elif change < -THRESHOLD: 
            for user in subscribers:
                await user.send(f"Not Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")
            await channel.send(f"Not Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")
        current_price = latest_price
    running = True
    is_alerts_running = False
    
@bot.command(name="stopalerts", description = "Stop the alerts", aliases=["stop", "SA", "StopAlerts"])
async def stopalerts(ctx):
    global running
    global is_alerts_running
    if is_alerts_running:
        running = False
        is_alerts_running = False
        await ctx.send("Alerts stopped.")
    else:
        await ctx.send("Alerts are not running.")

@bot.command(aliases=["quit", "s"])
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    global is_alerts_running
    if is_alerts_running:
        global running
        running = False
        await ctx.send("Stopping alerts loop and shutting down the bot...")
        await ctx.channel.send("Shutting down...")
    else:
        await ctx.send("Bot is already not running")
    await bot.close()

yourKey = "5540350d-71bb-4557-b64a-c3881708df0a"

def get_uuid(username):
    url = 'https://api.mojang.com/users/profiles/minecraft/' + username
    userName = username
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['id']
    else:
        return None

def getLevel(uuid):
    url = "https://api.hypixel.net/player?key=" + yourKey + "&uuid=" + uuid
    response = requests.get(url)
    if response.status_code == 200:
        networkExperience = response.json()["player"]["networkExp"]
        networkLevel = (math.sqrt((2 * networkExperience) + 30625) / 50) - 2.5
        return networkLevel
    else:
        return None
    
def getxp(uuid):
    url = "https://api.hypixel.net/player?key=" + yourKey + "&uuid=" + uuid
    response = requests.get(url)
    if response.status_code == 200:
        networkExperience = response.json()["player"]["networkExp"]
        return networkExperience
    else:
        return None

def log_table(username, dev_id, minecraft_user, hypixel_xp, hypixel_level, channel, request_failed):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    failure_string = "Yes" if request_failed else "No"
    with open("Log.txt", "a") as log_file:
            log_string = f"| {username} | {dev_id} | {minecraft_user} | {hypixel_xp} | {hypixel_level} | {channel} |{failure_string} | {current_time} |"
            log_file.write(f"| {username} | {dev_id} | {minecraft_user} | {hypixel_xp} | {hypixel_level} | {channel} |{failure_string} | {current_time} |\n")
            
    print(log_string)

@bot.command(name="lock_server")
async def Lockserver(ctx):
    server = ctx.guild
    unlocked_channel = server.get_channel(1066823238556065803)
    for channel in server.channels:
        if channel != unlocked_channel:
            await channel.set_permissions(server.default_role, read_messages=False)
            await unlocked_channel.set_permissions(server.default_role, read_messages=True)
            

@bot.command(name="unlock_server")
async def Unlockserver(ctx):
    server = ctx.guild
    unlocked_channel = server.get_channel(1066823238556065803)
    for channel in server.channels:
        if channel != unlocked_channel:
            await channel.set_permissions(server.default_role, read_messages=True)
            await unlocked_channel.set_permissions(server.default_role, read_messages=False)

@bot.command()
async def hypixelinfo(ctx, arg):
    title = "Infomation for " + arg
    hypixel_xp = getxp(get_uuid(arg))
    hypixel_level = getLevel(get_uuid(arg))
    print("https://gen.plancke.io/exp/" + arg + ".png")
    embed=discord.Embed(title=title, description="Bot by spen#0001, Powered by https://gen.plancke.io/", color=0xFF5733)
    ###embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_image(url="https://gen.plancke.io/exp/" + arg + ".png")
    
    embed2 = discord.Embed(color=0xFF5733)
    embed2.set_image(url="https://gen.plancke.io/achievementPoints/" + arg + ".png")
    await ctx.send(embed = embed)
    await ctx.send(embed = embed2)
    log_table(ctx.author.name, ctx.author.id, arg, hypixel_xp, hypixel_level, ctx.channel, hypixel_level)

@bot.command()
async def kick(ctx, member: discord.Member, reason):
    role = discord.utils.get(ctx.guild.roles, name="perms")
    if role in ctx.author.roles:
        message = f'We are very sorry, you have been kicked from the server! Reason: {reason}'
        try:
            await member.send(message)
            await member.kick(reason=reason)
        except discord.Forbidden:
            print(f"Could not send message to {member.name}")

async def kick(ctx, member: discord.Member, reason):
    role = discord.utils.get(ctx.guild.roles, name="perms")
    if role in ctx.author.roles:
        message = f'We are very sorry, you have been kicked from the server! Reason: {reason}.'
        try:
            await member.send(message)
            await member.kick(reason=reason)
            await ctx.message.delete()
        except discord.Forbidden:
            print(f"Could not send message to {member.name}")
            await ctx.message.delete()

@bot.command()
async def note(ctx, *, note_text):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("DevNotes.txt", "a") as f:
        f.write(f"{current_time} - {note_text}\n")


# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run("")
