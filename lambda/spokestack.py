"""
Spokestack TTS request code, mostly copied from the library itself:
https://github.com/spokestack/spokestack-python
"""
import base64
import hashlib
import hmac
import json
from typing import Any, Iterator

import requests

_MODES = {
    "ssml": "synthesizeSSML",
    "markdown": "synthesizeMarkdown",
    "text": "synthesizeText",
}

API_URL = "https://api.spokestack.io/v1"

class TextToSpeechClient:
    """Spokestack Text to Speech Client
    Args:
        key_id (str): identity from spokestack api credentials
        key_secret (str): secret key from spokestack api credentials
        url (str): spokestack api url
    """

    def __init__(self, key_id: str, key_secret: str) -> None:

        self._key_id = key_id
        self._key = key_secret.encode("utf-8")

    def synthesize(
        self,
        utterance: str,
        mode: str = "text",
        voice: str = "demo-male",
    ) -> str:
        """Converts the given utterance to speech accessible by a URL.
        Args:
            utterance (str): string that needs to be rendered as speech.
            mode (str): synthesis mode to use with utterance. text, ssml, markdown.
            voice (str): name of the tts voice.
        Returns: URL of the audio clip
        """
        body = self._build_body(utterance, mode, voice)
        signature = base64.b64encode(
            hmac.new(self._key, body.encode("utf-8"), hashlib.sha256).digest()
        ).decode("utf-8")
        headers = {
            "Authorization": f"Spokestack {self._key_id}:{signature}",
            "Content-Type": "application/json",
        }
        response = requests.post(API_URL, headers=headers, data=body)

        if response.status_code != 200:
            raise Exception(response.reason)

        response = response.json()
        if "errors" in response:
            raise TTSError(response["errors"])

        return response["data"][_MODES[mode]]["url"]

    @staticmethod
    def _build_body(message: str, mode: str, voice: str) -> str:
        if mode not in _MODES:
            raise ValueError("invalid_mode")
        query = f"""
        query AlexaSynthesis($voice: String!, ${mode}: String!, $profile: SynthesisProfile) {{
          {_MODES[mode]}(voice: $voice, {mode}: ${mode}, profile: $profile) {{url}}
        }}
        """
        return json.dumps({
            "query": query,
            "variables": {"voice": voice, mode: message, "profile": "ALEXA"}
        })


class TTSError(Exception):
    """ Text to speech error wrapper """

    def __init__(self, response: Any) -> None:
        messages = [error["message"] for error in response]
        super().__init__(messages)
