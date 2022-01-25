import os

from assist import Assistant
from discord.ext.commands import AutoShardedBot
from top_api import top_setup

INVOCATION_PREFIXES = [
    "la gardaş bak hele,",
    "ula uşağum bak bağa da,",
    "Googlecum bana bakar mısın,",
]

HELP_MESSAGE = """Abi beklettiğim için kusuruma bakma.Ben senin asistanınım :grinning:
Yardım etmemi istiyorsan, "Googlecum bana bakar mısın" demen yeterli Sorgularınız doğrudan ele alınmaz,
sorgular, Google bulut sunucularında bir Sinir Ağı tarafından işlenir.
Yardım, sabit kodlanmış tek komuttur."""

ERROR_MESSAGE = """Abi üzülmeni istemem ama şuanlık sana yardımcı olamam"""


class AssistantDiscordBot(AutoShardedBot):
    """Discord Hesap bilgi sorgularına yardımcı olur"""

    def __init__(
        self,
        device_model_id=None,
        device_id=None,
        credentials=None,
        token=None,
        dbl_token=None,
    ):
        super(AssistantDiscordBot, self).__init__(
            command_prefix=None, fetch_offline_members=False
        )
        self.dbl_token = dbl_token
        self.assistant = Assistant(
            device_model_id=device_model_id,
            device_id=device_id,
            credentials=credentials,
            token=token,
        )

    async def on_ready(self):
        print("olarak giriş yaptı")
        print(self.user.name)
        print(self.user.id)
        print("------")
        if self.dbl_token:
            top_setup(self, self.dbl_token)

    async def on_message(self, message):
        if message.author.bot:
            return
        lower_content = message.content.lower()
        # if message does not begin with an invocation prefix
        if list(filter(lower_content.startswith, INVOCATION_PREFIXES)) == []:
            return

        if "help" in lower_content[:18]:
            await message.channel.send(HELP_MESSAGE)

        assistant_response = self.assistant.text_assist(lower_content)

        if assistant_response:
            await message.channel.send(assistant_response)


if __name__ == "__main__":
    device_model_id = os.environ.get("GA_DEVICE_MODEL_ID")
    device_id = os.environ.get("GA_DEVICE_ID")
    assistant_token = os.environ.get("GA_TOKEN")
    credentials = os.environ.get("GA_CREDENTIALS")

    dbl_token = os.environ.get("DBL_TOKEN")

    discord_token = os.environ.get("DISCORD_TOKEN")

    client = AssistantDiscordBot(
        device_model_id=device_model_id,
        device_id=device_id,
        credentials=credentials,
        token=assistant_token,
        dbl_token=dbl_token,
    )

    client.run(discord_token)
