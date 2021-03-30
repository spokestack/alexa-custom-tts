## Spokestack Custom Text to Speech on Alexa

This is sample code for an [Alexa-hosted skill](https://developer.amazon.com/en-US/docs/alexa/hosted-skills/build-a-skill-end-to-end-using-an-alexa-hosted-skill.html) that uses a custom text to speech (TTS) voice from [Spokestack](https://www.spokestack.io/) to replace Alexa's voice.

The skill itself isn't impressive; it simply repeats an encouraging message (see https://www.youtube.com/watch?v=xNx_gU57gQ4 for our inspiration) and exits. Its main purpose is to be a template demonstrating the use of SSML and a custom TTS service to replace the default voice on a smart speaker. The same SSML will work for Google Assistant, but the rest of the code in this repository is structured to run in Amazon's hosting infrastructure.

## Installation

_You'll need an [Amazon developer account](https://developer.amazon.com/) to set up this skill and a [Spokestack account](https://www.spokestack.io/create) for it to produce responses._

1. Log in to the [Alexa developer console](https://developer.amazon.com/alexa/console/ask#).
1. On the "Skills" tab (which is selected by default at the time of writing), click `Create Skill`.
1. On the "Create a new skill" screen:
    - Enter a name for your skill. Any name will do.
    - Under "Choose a model..." select "Custom" (selected by default).
    - Under "Choose a method..." select "Alexa-hosted (Python)".
    - Click the "Create skill" button (you may have to scroll up to see it).
1. On the next screen ("Choose a template..."), click the "Import skill" button.
1. Enter this repository's URL (`https://github.com/spokestack/alexa-custom-tts`) in the "Import skill" box.
1. Click "Import".

Once you've clicked "Import", Amazon will take care of copying over the code and creating a new sandbox for your skill to run in. When the import completes, click on the "Code" tab to finish setup. This will open the `lambda_function.py` file in a code editor. Look for the "Customize your skill here!" section and customize it at will. The only things you _need_ to change are `SPOKESTACK_CLIENT_ID` and `SPOKESTACK_CLIENT_SECRET`, replacing the default values with a set of credentials from [your account settings](https://www.spokestack.io/account/settings#api).

When you're finished making changes, click "Save" then "Deploy" at the top. While you're waiting for the deployment to finish, click over to the "Test" tab. In the dropdown next to "Test is disabled for this skill" (at the top of the page), you'll want to select "Devleopment". This will let you test your skill directly on the page or on any Alexa-enabled devices connected to the account you used to create this skill.

That's it! Enjoy your new smart speaker voice!

## How Does It Work?

The bulk of the sample code here is based on Amazon's [Python SDK example](https://github.com/alexa/skill-sample-python-helloworld-decorators). The only thing we're customizing is running the text of our responses (or _response_, in this case, because we're being lazy) through Spokestack's text to speech API. That gives us back a URL that points to the speech audio, and we're using the [SSML `audio` element](https://www.w3.org/TR/speech-synthesis11/#S3.3.1) to play the audio instead of having Amazon's TTS service synthesize the text for us in Alexa's voice and play _that_ audio.

The code for the actual synthesis is in the `spokestack.py` file. It makes a GraphQL request to Spokestack's TTS API and pulls out the resulting audio URL.

## Can I Use My Own Voice?

Yes! Spokestack's Maker account lets you train your own TTS voice using a simple web tool and your own microphone. You can do it with as little as 5 minutes of data; once your voice is trained, simply plug its name into the `VOICE` variable at the top of `lambda_function.py`.

## Troubleshooting

### Alexa says, "Sorry, I don't know that one" during testing
This happens if you ask Alexa to open a skill, but the skill's name isn't recognized. Development skills can run into this problem if the invocation name has been changed without rebuilding the skill's model. To ensure your skill name is up to date:
1. Click on the "*Build*" tab in the development console.
1. Click on "*Invocation Name*" in the Skill builder checklist.
1. Double-check that your invocation name is what you want, then click "*Save Model*" at the top of the page.
1. Click "*Deploy Model*".
When the model is updated, Amazon will notify you with a popup at the bottom of the screen. At this point, "open `skill name`" should work in the test console.
