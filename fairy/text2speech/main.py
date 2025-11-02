from elevenlabs import play
from elevenlabs.client import ElevenLabs

from fairy.text2speech.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)


if __name__ == '__main__':
    audio = elevenlabs.text_to_speech.convert(
        text="[whispering] Bylo nebylo, [swallows] za sedmero horami a sedmero řekami, [hesitates] žil byl jeden [shouting] král, který měl tři syny.",
        voice_id=ELEVENLABS_VOICE_ID,
        model_id="eleven_v3",
        output_format="mp3_44100_128",
    )

    play(audio)
