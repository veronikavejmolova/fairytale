from elevenlabs import play
from elevenlabs.client import ElevenLabs

from tools.text2speech.config import ELEVEN_LABS_KEY, ELEVEN_LABS_VOICE_ID

elevenlabs = ElevenLabs(api_key=ELEVEN_LABS_KEY)


if __name__ == '__main__':
    audio = elevenlabs.text_to_speech.convert(
        text="[whispering] Bylo nebylo, [swallows] za sedmero horami a sedmero řekami, [hesitates] žil byl jeden [shouting] král, který měl tři syny.",
        voice_id=ELEVEN_LABS_VOICE_ID,
        model_id="eleven_v3",
        output_format="mp3_44100_128",
    )

    play(audio)
