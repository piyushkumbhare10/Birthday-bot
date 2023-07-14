import os
from datetime import datetime, time, timedelta
import pytz
import asyncio

import discord
from discord import app_commands
from discord.utils import get
from discord.ext import commands, tasks

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

GUILD_ID = os.getenv('GUILD_ID')
BOT_ID = int(os.getenv('BOT_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

BIRTHDAY_ROLE_ID = int(os.getenv('BIRTHDAY_ROLE_ID'))
MY_ID = int(os.getenv('MY_ID'))

owners = [338869820776775691, 268126708413104128]
print(TOKEN)

run_time = time(hour=0, minute=0, tzinfo=pytz.timezone("US/Pacific"))

bot = commands.Bot(command_prefix='$', owner_id = MY_ID, intents=discord.Intents.all())

current_guild = None

birthdays = dict()
changes = 0

@bot.event
async def on_ready():
    print("bot ready!")
    global changes
    changes = 0
    for i in bot.guilds:
        if i is not None:
            print(f"{i.name}: {i.id}")
            current_guild = i
            break

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    
    print("Loading birthdays")
    with open('birthdays.txt', 'r+') as f:
        for i in f.readlines():
            line = i.split(',')
            birthdays[line[0]] = [int(num) for num in line[1::]]
            print(birthdays[line[0]])
    
    channel = bot.get_channel(CHANNEL_ID)

    t = datetime.now(pytz.timezone("US/Pacific"))

    x = [t.month, t.day, t.year]

    for person in birthdays.keys():
        if birthdays[person][0:2] == x[0:2]:
            print(f"It's {person}'s birthday now. Today = {x[0:2]}, Birthday = {birthdays[person][0:2]}")
            await channel.send(f"<@&{BIRTHDAY_ROLE_ID}> Happy birthday {person}!! Congratulations on turning {t.year - birthdays[person][2]} years old!")

    test.start()
    

@bot.tree.command(name="sis", description="How can there be a /bro without a /sis?")
async def bro(interaction: discord.Interaction):
    await interaction.response.send_message(f"What's up sis {interaction.user.mention}")
    

@bot.tree.command(name="bro", description="Just a test command that I grew attached to.")
async def bro(interaction: discord.Interaction):
    await interaction.response.send_message(f"What's up bro {interaction.user.mention}")

@bot.tree.command(name="add-birthday", description="Adds the birthday of a person to the list. If the person exists, replaced by new value.")
@app_commands.describe(person="Who's birthday?", month="Month", day="Day", year="Year")
async def add_birthday(interaction: discord.Interaction, person: str, month: int, day: int, year: int):
    #Check date validity
    print(person, month, day, year)
    if(person.find(',') != -1):
        await interaction.response.send_message(f"Names cannot have commas, please try again.")
        return
    
    if month not in range(1, 13) or day not in range(1, 32) or year not in range(1, 3001):
        await interaction.reponse.send_message(f"That's an invalid date. Enter in the format /add_birthday Name Month Day Year")
        return

    #Valid date, now check if already exists
    if(person in birthdays.keys()):
        bday = birthdays[person]
        await interaction.response.send_message(f"Birthday already found, replacing old date ({bday[0]}/{bday[1]}/{bday[2]}) with new value ({month}/{day}/{year})")
    else:
        await interaction.response.send_message(f"Added birthday for {person} on {month}/{day}/{year} successfully!")
        

    birthdays[person] = [int(num) for num in [month, day, year]]
    global changes
    changes = 1
    return


@bot.tree.command(name="get-birthday", description="Returns the birthday of a specified person. (Case Sensitive)")
@app_commands.describe(person="Who?")
async def get_birthday(interaction: discord.Interaction, person: str):
    #Check if person is in the birthday dict
    if person not in birthdays.keys():
        await interaction.response.send_message(f"{person}'s birthday has not been registered yet. Add it using /add-birthday")
        return

    bday = birthdays[person]

    await interaction.response.send_message(f"{person}'s birthday is on {bday[0]}/{bday[1]}. Be sure to send them your wishes!")
    return


@bot.tree.command(name="list-all-birthdays", description="Lists all registered birthdays.")
async def list_all_birthdays(interaction: discord.Interaction):
    #Prepare message format
    message = f"```{'Name' : <20}{'Birthday' : >10}\n"
    message += "=" * 30 + "\n"

    t = datetime.now(pytz.timezone("US/Pacific"))

    x = [t.month, t.day, t.year]

    #Iterate through dict and append people/bdays
    for person in birthdays.keys():
        bday = birthdays[person]
        message += f"{person : <20}{f'{bday[0]}/{bday[1]}/{bday[2]}' : >10} {':birthday:' * (birthdays[person][0:2] == x[0:2])}\n"
    
    message += "```"

    await interaction.response.send_message(f"Here is a list of all birthdays!\n{message}(To register a birthday, use the /add-birthday command!)")
    return


@bot.tree.command(name="remove-birthday", description="Removes the entry of the specified person. (Case Sensitive)")
@app_commands.describe(person="Who?")
async def remove_birthday(interaction: discord.Interaction, person: str):
    #Check if person is in the birthday dict
    if person not in birthdays.keys():
        await interaction.response.send_message(f"{person}'s birthday has not been registered yet. Add it using /add-birthday")
        return

    bday = birthdays.pop(person)
    global changes
    changes = 1
    await interaction.response.send_message(f"Removed {person}'s birthday from the list")
    return

@bot.tree.command(name="shutdown", description="Caches updates values and shuts down bot. Can only be called by owner.")
async def shutdown(interaction: discord.Interaction):

    called_by_owner = await bot.is_owner(interaction.user)
    if called_by_owner == True:
        await interaction.response.send_message("Shutting down... Until next time :wave:")
    else:
        await interaction.response.send_message("Only the owner can call this command! Hands off!")
        return
    
    #write to file
    with open('birthdays.txt', 'w') as f:
        for person in birthdays.keys():
            f.write(f"{person},{birthdays[person][0]},{birthdays[person][1]},{birthdays[person][2]}\n")
    
    #die
    await bot.close()

@tasks.loop(time=run_time)
async def test():
    channel = bot.get_channel(CHANNEL_ID)

    # await channel.send(f"<@&{BIRTHDAY_ROLE_ID}> Test ping")    
    
    print("looped")
    global changes
    # print(f"Scanning, changes = {changes}")
    if changes == 1:
        changes = 0
        print("Changes detected, writing to disk")
        with open('birthdays.txt', 'w') as f:
            for person in birthdays.keys():
                f.write(f"{person},{birthdays[person][0]},{birthdays[person][1]},{birthdays[person][2]}\n")

    t = datetime.now(pytz.timezone("US/Pacific"))

    x = [t.month, t.day, t.year]

    for person in birthdays.keys():
        if birthdays[person][0:2] == x[0:2]:
            print(f"It's {person}'s birthday now. Today = {x[0:2]}, Birthday = {birthdays[person][0:2]}")
            await channel.send(f"<@&{BIRTHDAY_ROLE_ID}> Happy birthday {person}!! Congratulations on turning {t.year - birthdays[person][2]} years old!")
    return

bot.run(TOKEN)
