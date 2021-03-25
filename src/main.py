import os

from discord.ext.commands import AutoShardedBot

from assist import Assistant
from top_api import top_setup

INVOCATION_PREFIXES = ['hey google,', 'ok google,', 'okay google,']

HELP_MESSAGE = '''I\'m your Google Assistant :grinning:
Ready to help, just say `Hey Google, `
Your queries are not handled directly,
queries are handled by a Neural Network on Google cloud servers.
Help is the only hardcoded command.'''

ERROR_MESSAGE = '''Sorry, I can't help with that yet'''
FAIL_MESSAGE = '''It seems that personalized response are
disabled. No responses would be receieved until the
personalized responses are enabled again.'''


class AssistantDiscordBot(AutoShardedBot):
    """Responds to Discord User Queries"""

    def __init__(
            self,
            device_model_id=None,
            device_id=None,
            credentials=None,
            token=None,
            dbl_token=None):
        super(AssistantDiscordBot, self).__init__(
            command_prefix=None,
            fetch_offline_members=False
        )
        self.dbl_token = dbl_token
        self.assistant = Assistant(
            device_model_id=device_model_id,
            device_id=device_id,
            credentials=credentials,
            token=token
        )

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        if(self.dbl_token):
            top_setup(self, self.dbl_token)

    async def on_message(self, message):
        if message.author.bot:
            return
        lower_content = message.content.lower()
        # if message does not begin with an invocation prefix
        if list(filter(lower_content.startswith, INVOCATION_PREFIXES)) == []:
            return

        if 'help' in lower_content[:18]:
            await message.channel.send(HELP_MESSAGE)

        assistant_response = self.assistant.text_assist(lower_content)

        if assistant_response:
            await message.channel.send(assistant_response)
        else:
            await message.channel.send(FAIL_MESSAGE)


if __name__ == '__main__':
    device_model_id = os.environ.get('GA_DEVICE_MODEL_ID')
    device_id = os.environ.get('GA_DEVICE_ID')
    assistant_token = os.environ.get('GA_TOKEN')
    credentials = os.environ.get('GA_CREDENTIALS')

    dbl_token = os.environ.get('DBL_TOKEN')

    discord_token = os.environ.get('DISCORD_TOKEN')

    client = AssistantDiscordBot(
        device_model_id=device_model_id,
        device_id=device_id,
        credentials=credentials,
        token=assistant_token,
        dbl_token=dbl_token
    )

    client.run(discord_token)
