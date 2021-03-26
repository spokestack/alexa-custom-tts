import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

from spokestack import TextToSpeechClient

###############################################################################
# Customize your skill here!
###############################################################################
# your Spokestack API credentials
SPOKESTACK_CLIENT_ID = "your-id-here"
SPOKESTACK_CLIENT_SECRET = "your-secret-key-here"

# the name of the TTS voice to use
# you can use this default voice or the name of a voice you've created using
# the text to speech tool on Spokestack's site
VOICE = "demo-male"

# text to read as a response
RESPONSE = "You're good enough, you're smart enough, and dog gone it, people like you!"

# the name of your skill (shown on cards)
SKILL_NAME = "Stuart Smallish"

###############################################################################
# This is basically the only feature we've added.
# All it does is insert Spokestack TTS URLs in an SSML tag.
###############################################################################
tts = TextToSpeechClient(key_id=SPOKESTACK_CLIENT_ID,
                         key_secret=SPOKESTACK_CLIENT_SECRET)


def synthesize(text):
    """
    Creates an SSML `<audio>` element containing a URL to
    a synthesized version of the text.
    """
    try:
        url = tts.synthesize(text, voice=VOICE)
        return {
            "audio": f'<audio src="{url}"/>',
            "text": text
        }
    except Exception as e:
        return {
            "audio": "Sorry; there was a problem",
            "text": f"There was a problem: {e}"
        }


###############################################################################
# The code below comes from an Amazon sample with slight modification to
# intercept the response and run it through TTS before returning it.
# See https://github.com/alexa/skill-sample-python-helloworld-decorators
###############################################################################
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _create_response(response_builder, synthesized, end_session=True):
    return response_builder.speak(synthesized["audio"]).set_card(
        SimpleCard(SKILL_NAME, synthesized["text"])).set_should_end_session(
            end_session).response

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for skill launch."""
    synth = synthesize(RESPONSE)

    return _create_response(handler_input.response_builder, synth)

# handle other intents, even though we won't need to since we're
# exiting after launch

@sb.request_handler(can_handle_func=is_intent_name("MotivateIntent"))
def motivate_intent_handler(handler_input):
    """Handler for MotivateIntent."""
    synth = synthesize(RESPONSE)

    return _create_response(handler_input.response_builder, synth)


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for HelpIntent."""
    synth = synthesize("Ask me to motivate you!")

    return _create_response(handler_input.response_builder, synth, False)


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for CancelIntent and StopIntent."""
    synth = synthesize("Goodbye for now!")

    return _create_response(handler_input.response_builder, synth, False)


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    speech = ("Sorry; I can't help with that. Only you can help you. "
              "You can ask me to motivate you.")
    reprompt = "Ask me to say something."
    synth = synthesize(speech)
    reprompt_synth = synthesize(reprompt)
    handler_input.response_builder.speak(synth["audio"]).ask(reprompt_synth["audio"])
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for session end."""
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch-all exception handler.
    Log exception and respond with custom message.
    """
    logger.error(exception, exc_info=True)

    speech = "Sorry, there was a problem. Please try again!"
    synth = synthesize(speech)

    handler_input.response_builder.speak(synth["audio"]).ask(synth["audio"])

    return handler_input.response_builder.response


# special assignment for AWS Lambda
lambda_handler = sb.lambda_handler()
