# 🦄🌈
import os
import time
import string
import subprocess
import random

import discord

def get_version():
    try:
        # Run the git command to get the latest commit hash
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
                                cwd=os.path.dirname(os.path.realpath(__file__)))
        return result.stdout.strip()[:8]  # Get the hash and remove any extra whitespace
    except subprocess.CalledProcessError as e:
        return 'maybe 0.0.1?'

def read_dictionary(filename):
    dictionary = []
    for line in open(filename, 'r', encoding='utf-8').read().split('\n'):
        if line.startswith('//'):
            continue
        superior_word, subpar_word = line.split(':')  # Crowdstrike disaster vibes code
        dictionary.append([superior_word, subpar_word])
    return dictionary[::-1]

dictionary = read_dictionary('substitutionlist.txt')
quotes = open('quotes.txt', 'r').read().split('\n')
triggers = open('reactiontriggerlist.txt', 'r').read().split('\n')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Avoiding cacopony

    # "Commands"
    if 'ponyquote' == message.content:
        await message.delete()
        await message.channel.send(random.choice(quotes).replace(' | ', '\u000A'))
        return
    if 'ponyversion' == message.content:
        await message.delete()
        await message.channel.send(f'PonyBot version `{get_version()}`')
    if 'ponystop!YESPLEASE' == message.content:
        # Fantastic design! Simply delightful! No auth!! No context appropriateness checks!!!
        await message.delete()
        time.sleep(0.5)
        exit()

    # Legacy message rewriter
    # TODO: I can make it way better!
    better_message = message.content
    # Throw-away joke quality code
    # We will replace it with an LLM anyway
    for superior_word, subpar_word in dictionary:
        better_message = better_message.replace(subpar_word, f'\u200B*{superior_word}*\u200B')
        # Optimization is not my passion today
        better_message = better_message.replace(string.capwords(subpar_word), f'\u200B*{string.capwords(superior_word)}*\u200B')
    if better_message != message.content:
        await message.delete()  # 😈 mode
        await message.channel.send(f'<@{message.author.id}> :unicorn: :\n{better_message}')

    # Maybe add reaction
    message_lower = str(message.content).lower()
    add_reaction = False
    for t in triggers:
        # Optimization is not my passion today
        if t in message_lower:
            add_reaction = True
    if add_reaction:
        await message.add_reaction('🦄')

    # Random quote out of nowhere
    if random.random() > 0.99:
        # This message is your lucky message!
        await message.channel.send(random.choice(quotes))

if __name__ == '__main__':
    client.run(open('token', 'r').read())
