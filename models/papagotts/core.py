import gradio as gr
from navertts import NaverTTS

from utils.model import Model

class PapagoTTS(Model):
    def __init__(self, save_path):
        self.save_path = save_path
        
        self.setup_interface(self.transcribe, self.get_inputs(), self.get_outputs())
        
    def transcribe(
        self,
        text: str,
        language: str = "en",
    ):
        tts = NaverTTS(text, lang=language)
        tts.save(self.save_path)
        
        return self.save_path
        
    def get_inputs(self):
        return [
            gr.components.Textbox(lines=2, label="Input", placeholder=None),
        ]

    def get_outputs(self):
        return [
            gr.components.Audio(
                label="TTS Audio File",
                source="upload",
                type="filepath",
            ),
        ]
