import discord
import os
from dotenv import load_dotenv

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

for folder in os.listdir("cog"):
    for file in os.listdir(os.path.join("cog", folder)):
        if not file.endswith(".py"):
            continue
        try:
            bot.load_extension(f"cog.{folder}.{file.removesuffix('.py')}")
            print(f"Le fichier 'cog/{folder}/{file}' a été importé")
        except Exception as exception:
            print(f"Erreur lors de la tentative d'importation de 'cog/{folder}/{file}' : {exception}")

load_dotenv()
bot.run(os.getenv('TOKEN')) 