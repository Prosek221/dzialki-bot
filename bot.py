import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.command()
async def saldo(ctx):
    await ctx.send("Twoje saldo to: 100$")

bot.run("TWÓJ_TOKEN")