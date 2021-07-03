from datetime import datetime
import os
import asyncio
import discord
from discord.ext import commands
from config import VERSION, TOKEN, DEV_IDS, OWNER_PERMS
from database import db


def get_prefix(bot, message):
    prefix = db.query("SELECT Prefix FROM guilds WHERE Id = ?", message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)

class PKBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            intents=discord.Intents.all(),
            owner_ids=DEV_IDS,
            case_insensitive=True,
        )
        self.remove_command('help')

bot = PKBot()

@bot.event
async def on_ready():
    bot.uptime = datetime.utcnow()
    await bot.change_presence(
        status=discord.Status.online, 
        activity=discord.Game('lounging')
    )
    print(f"PKBot v{VERSION} online {bot.uptime}")
    print(f"________________________________________\n")
    await asyncio.sleep(1)
    print(f"________________________________________\n")

@bot.event
async def on_message(message):
    if message.author == bot:
        return

    data = db.one(
        "SELECT Channel, Prefix FROM guilds WHERE Id = ?", message.guild.id
    )

    channel = discord.utils.get(message.guild.channels, name=data[0])
    pfx = data[1]
    
    if (
        message.author.permissions_in(message.channel).value in OWNER_PERMS
        or message.channel == channel or message.author.id in DEV_IDS
    ):
        await bot.process_commands(message)
    elif message.content.startswith(pfx):
        print("cannot process commands in this channel")
        await message.channel.send(
            f"PKBot cannot process commands in this channel\n\
            Please use channel: '{channel.mention}'",
            delete_after=10,
        )

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

if __name__ == '__main__':
    db.build_database()
    bot.run(TOKEN, reconnect=True)
