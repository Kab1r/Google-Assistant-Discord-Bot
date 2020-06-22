
import json
import logging
import os

from google.assistant.embedded.v1alpha2 import (embedded_assistant_pb2,
                                                embedded_assistant_pb2_grpc)
from google.assistant.embedded.v1alpha2.embedded_assistant_pb2 import (
    AssistConfig, AssistRequest, AudioOutConfig, DeviceConfig, DialogStateIn,
    ScreenOutConfig)
from google.assistant.embedded.v1alpha2.embedded_assistant_pb2_grpc import \
    EmbeddedAssistantStub
from google.auth.transport.grpc import secure_authorized_channel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from html2text import html2text

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5


class Assistant(object):
    def __init__(self, language_code='en-US', device_model_id=None, device_id=None, credentials=None, token=None):
        loaded_credentials, http_request = self.load_oath2_credentials(
            credentials, token)
        channel = secure_authorized_channel(
            loaded_credentials, http_request, ASSISTANT_API_ENDPOINT)
        logging.info('Connecting to %s', ASSISTANT_API_ENDPOINT)

        self.stub = EmbeddedAssistantStub(channel)
        self.language_code = language_code
        self.device_model_id = device_model_id
        self.device_id = device_id
        self.conversation_state = None

    def text_assist(self, query: str, is_new_conversation=True) -> str:
        result: str = None
        better_result: str = None
        for response in self.stub.Assist(self.iter_text_assist_requests(query, is_new_conversation=is_new_conversation), DEFAULT_GRPC_DEADLINE):
            if response.dialog_state_out.conversation_state:
                self.conversation_state = response.dialog_state_out.conversation_state
            if response.dialog_state_out.supplemental_display_text:
                result = response.dialog_state_out.supplemental_display_text
                print('supplemental: ' + result)
            if response.screen_out.data:
                print('html: ' + response.screen_out.data)
                better_result = html2text(response.screen_out.data)
                print('parsed: ' + better_result)
        print('result: ' + result)
        return result

    def iter_text_assist_requests(self, query, is_new_conversation):
        config = AssistConfig(
            audio_out_config=AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
                volume_percentage=0,
            ),
            dialog_state_in=DialogStateIn(
                language_code=self.language_code,
                conversation_state=self.conversation_state,
                is_new_conversation=is_new_conversation,
            ),
            device_config=DeviceConfig(
                device_id=self.device_id,
                device_model_id=self.device_model_id,
            ),
            text_query=query,
        )
        req = AssistRequest(config=config)
        yield req

    def load_oath2_credentials(self, credentials: str, token: str):
        loaded_credentials = Credentials(
            token=token,
            **(json.load(credentials) if os.path.isfile(credentials) else json.loads(credentials))
        )

        http_request = Request()
        loaded_credentials.refresh(http_request)
        return loaded_credentials, http_request
