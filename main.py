# 🦄🌈
import os
import time
import subprocess
import random
import re

import discord


def get_version():
    try:
        # Run the git command to get the latest commit hash
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
                                cwd=os.path.dirname(os.path.realpath(__file__)))
        return 'beta ' + result.stdout.strip()[:8]  # Get the hash and remove any extra whitespace
    except subprocess.CalledProcessError as e:
        return 'maybe 0.1.0?'


HASHING_MODULO = 2**64 - 59  # Is prime
HASHING_COEFFICIENT = 31337


def read_dictionary(filename):
    dictionary = {}
    for line in open(filename, 'r', encoding='utf-8').read().split('\n'):
        if line.startswith('//'):
            continue
        superior_word, subpar_word = line.split(':')  # Crowdstrike disaster vibes code (fun joke)

        subpar_len = len(subpar_word)
        if subpar_len not in dictionary:
            dictionary[subpar_len] = {}
        hash = 0
        for c in list(subpar_word):
            hash *= HASHING_COEFFICIENT
            hash += ord(c)
            hash %= HASHING_MODULO
        if hash in dictionary[subpar_len]:
            pass
            # # Crowdstrike disaster vibes code (*really* fun joke)
            # raise Exception(f'Substitutionlist is ambiguous for word {subpar_word}')
        dictionary[subpar_len][hash] = superior_word
    return dictionary


def read_config():
    cfg = {}
    cfgtxt = open('config.cfg', 'r').read()
    for line in cfgtxt.split('\n'):
        if len(line) < 2:
            continue
        key, value = line.split('=')  # See it in a stacktrace? Malformed config.cfg!
        cfg[key] = value
    return cfg


dictionary = read_dictionary('substitutionlist.txt')
exception_dictionary = read_dictionary('substitutionexceptionslist.txt')
cfg = read_config()

PROTECTED_REGEXES = [
    re.compile(r'<:[a-zA-Z0-9_]+:\d+>'),  # Custom emojis
    re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)')
]
def unprotected_regions(msg):
    msglist = list(msg)
    for reg in PROTECTED_REGEXES:
        for match in reg.finditer(msg):
            sp = match.span()
            msglist[sp[0]:sp[1]] = msglist[sp[0]:sp[1]] = ['\00'] * (sp[1] - sp[0])
    return msglist


def obtain_substitutions(msg):
    msg = unprotected_regions(msg)
    substitutions = [[]] * len(msg)

    lenghts = range(max(max(dictionary.keys()), max(exception_dictionary)))[::-1]
    dicts = [exception_dictionary, dictionary]
    for ll, udict in [(x, y) for y in dicts for x in lenghts]:
        if ll not in udict.keys():
            continue
        tail_coff = pow(HASHING_COEFFICIENT, ll, HASHING_MODULO)

        cur_hash = 0
        fed = 0
        for i in range(len(msg)):
            cur_hash *= HASHING_COEFFICIENT
            cur_hash += ord(msg[i])
            cur_hash %= HASHING_MODULO
            if fed == ll:
                cur_hash = (cur_hash - tail_coff * ord(msg[i - ll])) % HASHING_MODULO
            else:
                fed += 1
            if cur_hash in udict[ll]:
                if udict[ll][cur_hash] != '':  # Substitution to empty is interpreted as _ignore_
                    substitutions[i] = [i - ll + 1, i + 1, udict[ll][cur_hash]]
                for i in range(i - ll + 1, i + 1):
                    msg[i] = '\00'
                fed = 0
                cur_hash = 0
    substitutions = [s for s in substitutions if s != []]
    return substitutions


def message_rewriter(msg):
    # Complexity: O(NK), N = len(msg), K = len(dictionary.items())
    subs = obtain_substitutions(f'{msg}'.lower().replace('ё', 'е'))
    if len(subs) == 0:
        return msg

    result = ''
    subs_i = 0
    msg_i = 0
    while msg_i < len(msg):
        # Proudly tested in production 😊
        if subs_i < len(subs) and subs[subs_i][0] == msg_i:
            repl = msg[subs[subs_i][0]:subs[subs_i][1]]
            # TODO: clown case
            caps = repl.isupper()
            capitalized = repl[0].isupper()
            substitution: str = subs[subs_i][2]
            if caps:
                substitution = substitution.upper()
            elif capitalized:
                substitution = substitution.capitalize()

            result += f'\u2060*{substitution}*\u2060'
            msg_i = subs[subs_i][1]
            subs_i += 1
        else:
            result += msg[msg_i]
            msg_i += 1
    return result


quotes = [x for x in open('quotes.txt', 'r').read().split('\n') if len(x) > 1]
triggers = open('reactiontriggerlist.txt', 'r').read().split('\n')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await tree.sync()


@tree.command(name="ponyversion", description="Show PonyBot version")
async def ponyversion(interaction: discord.Interaction):
    await interaction.response.send_message(f'PonyBot version `{get_version()}`', ephemeral=True)


@tree.command(name="ponyquote", description="Send a random pony quote")
async def ponyquote(interaction: discord.Interaction):
    quote = random.choice(quotes).replace(' | ', '\u000A')
    await interaction.response.send_message(quote)


@tree.command(name="ponystop", description="Stop PonyBot (superadmin only)")
async def ponystop(interaction: discord.Interaction):
    if cfg['superadmin_id'] != str(interaction.user.id):
        await interaction.response.send_message("Access denied.", ephemeral=True)
        return
    await interaction.response.send_message("Stopping...", ephemeral=True)
    time.sleep(0.5)
    exit()


@client.event
async def on_message(message : discord.Message):
    if message.author == client.user:
        return  # Avoiding cacopony

    # Smart message rewriter
    # Order of magnitude: ~30ms for a message at the Discord's default character limit
    better_message = message_rewriter(message.content)
    if better_message != message.content:
        if cfg['enforcer_mode'] == 'True':
            await message.delete()  # 😈 mode
            await message.channel.send(f'<@{message.author.id}> :unicorn: :\n{better_message}')
        else:
            await message.add_reaction('😢')
            await message.reply(f'{better_message}', mention_author=False)
        return  # Sending a message is a lot as is

    # Maybe add reaction
    message_lower = str(message.content).lower()
    add_reaction = False
    for t in triggers:
        if t in message_lower:
            add_reaction = True
    if add_reaction:
        await message.add_reaction('🦄')

    # Random quote out of nowhere
    if random.random() > 0.99:
        # This message is your lucky message!
        await message.channel.send(random.choice(quotes))

if __name__ == '__main__':
    client.run(cfg['token'])
