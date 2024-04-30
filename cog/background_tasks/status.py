import discord
import function.data as data_manager
from discord.ext import tasks, commands


class statut_Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status.start()

    @tasks.loop(seconds = 5)
    async def status(self):
        current_status = data_manager.get_data("db", "bot_status")
        await self.bot.change_presence(
            activity = discord.Streaming(
                name = current_status,
                url = "https://www.twitch.tv/twitch"
            )
        )

    @status.before_loop
    async def before_status(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(statut_Task(bot))