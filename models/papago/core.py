import gradio as gr
import tempfile
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
        audio_filename = tempfile.NamedTemporaryFile(delete=True, suffix=".mp3").name
        speech = NaverTTS(text, lang=language)
        speech.save(audio_filename)
        
        return audio_filename
        
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
