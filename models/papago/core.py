import gradio as gr
import tempfile
import base64
from navertts import NaverTTS

from utils.model import Model

class Papago(Model):
    def __init__(self):
        self.setup_interface(self.transcribe, self.get_inputs(), self.get_outputs())
        
    def transcribe(
        self,
        text: str,
        language: str = "en",
    ):
        audio_file = tempfile.NamedTemporaryFile(delete=True, suffix=".mp3")

        speech = NaverTTS(text, lang=language)
        speech.save(audio_file.name)

        speech_base64 = self.__audio_to_base64(audio_file.name)

        return speech_base64
        
    def get_inputs(self):
        return [
            gr.components.Textbox(lines=2, label="Input", placeholder=None),
        ]

    def get_outputs(self):
        return [
            gr.components.Audio(
                label="Speech",
                type="filepath",
            ),
        ]
    
    def __audio_to_base64(self, audio_filepath: str) -> str:
        with open(audio_filepath, "rb") as audio_file:
            audio_encoded = base64.b64encode(audio_file.read())
        return audio_encoded.decode("utf-8")
