import asyncio
import logging

from dbl import DBLClient
from discord.ext import commands, tasks


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot, dbl_token):
        self.logger = logging.getLogger('bot')
        self.bot = bot
        self.token = dbl_token
        self.dblpy = DBLClient(self.bot, self.token, autopost=True)

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        while not self.bot.is_closed():
            self.logger.info('Attempting to post server count')
            try:
                await self.dblpy.post_guild_count()
                self.logger.info('Posted server count ({})'.format(
                    self.dblpy.guild_count()))
            except Exception as e:
                self.logger.exception(
                    'Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)


def top_setup(bot, dbl_token):
    bot.add_cog(TopGG(bot, dbl_token))
