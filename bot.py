import discord
from discord.ext import commands
from mcrcon import MCRcon
import json
import os

# === KONFIGURACJA ===
TOKEN = 'MTM2NzkxOTEyMTgxOTUwNDcwMQ.GGh6YV.Hkpx3m715lwMLWhZTWeA3SB_SQqpndxzJtJOko'
RCON_HOST = 'TWOJE_IP_SERWERA'
RCON_PORT = 25575
RCON_PASSWORD = 'TWOJE_HASLO_RCON'

# === INICJALIZACJA ===
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# === WCZYTYWANIE DANYCH ===
if os.path.exists('dzialki.json'):
    with open('dzialki.json', 'r') as f:
        dzialki = json.load(f)
else:
    dzialki = {}

połączenia = {}  # Tymczasowe połączenia chunków: {user_id: [chunk1, chunk2, ...]}

def zapisz():
    with open('dzialki.json', 'w') as f:
        json.dump(dzialki, f, indent=4)

# === POMOCNICZA FUNKCJA – aktualny chunk gracza ===
def get_chunk_coords(gracz):
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        response = mcr.command(f"data get entity {gracz} Pos")
        pos = [float(x) for x in response.split('[')[1].split(']')[0].split(',')]
        chunk_x = int(pos[0]) >> 4
        chunk_z = int(pos[2]) >> 4
        return {'x': chunk_x, 'z': chunk_z, 'world': 'world'}

# === /połącz 1/2 – wybór chunków ===
@bot.command()
async def połącz(ctx, numer: int):
    user = str(ctx.author.id)
    if user not in połączenia:
        połączenia[user] = []
    try:
        chunk = get_chunk_coords(ctx.author.name)
        if numer == 1:
            połączenia[user] = [chunk]
        elif numer == 2:
            połączenia[user].append(chunk)
        await ctx.send(f"Zaznaczono chunk {numer}.")
    except:
        await ctx.send("Błąd pobierania pozycji. Musisz być online na serwerze Minecraft.")

# === /wystaw_dzialke nazwa cena ===
@bot.command()
async def wystaw_dzialke(ctx, nazwa: str, cena: int):
    user = str(ctx.author.id)
    if user not in połączenia or not połączenia[user]:
        await ctx.send("Najpierw zaznacz chociaż jeden chunk komendą `/połącz`.")
        return
    nazwa = nazwa.lower()
    if nazwa in dzialki:
        await ctx.send("Działka już istnieje.")
        return
    dzialki[nazwa] = {
        "cena": cena,
        "wlasciciel": None,
        "chunki": połączenia[user]
    }
    zapisz()
    połączenia[user] = []
    await ctx.send(f"Wystawiono działkę **{nazwa}** za **{cena}$**.")

# === /dzialki – lista wolnych działek ===
@bot.command()
async def dzialki(ctx):
    wolne = [nazwa for nazwa, d in dzialki.items() if d["wlasciciel"] is None]
    if not wolne:
        await ctx.send("Brak dostępnych działek.")
    else:
        msg = "**Dostępne działki:**\n"
        for nazwa in wolne:
            msg += f"• {nazwa} – {dzialki[nazwa]['cena']}$\n"
        await ctx.send(msg)

# === /kup_dzialke nazwa ===
@bot.command()
async def kup_dzialke(ctx, nazwa: str):
    nazwa = nazwa.lower()
    nick = ctx.author.name
    if nazwa not in dzialki:
        await ctx.send("Taka działka nie istnieje.")
        return
    if dzialki[nazwa]["wlasciciel"] is not None:
        await ctx.send("Ta działka już jest kupiona.")
        return
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            bal = mcr.command(f"eco balance {nick}")
            saldo = int(''.join(filter(str.isdigit, bal)))
            cena = dzialki[nazwa]['cena']
            if saldo < cena:
                await ctx.send("Nie masz wystarczająco pieniędzy.")
                return
            mcr.command(f"eco take {nick} {cena}")
            dzialki[nazwa]['wlasciciel'] = nick
            zapisz()
            await ctx.send(f"Kupiłeś działkę **{nazwa}** za **{cena}$**.")
    except Exception as e:
        print(e)
        await ctx.send("Błąd komunikacji z serwerem.")


