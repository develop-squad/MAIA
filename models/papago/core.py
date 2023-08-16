import gradio as gr
from navertts import NaverTTS

from utils.model import Model

class Papago(Model):
    def __init__(self, save_path):
        self.save_path = save_path
        
        self.setup_interface(self.transcribe, self.get_inputs(), self.get_outputs())
        
    def transcribe(
        self,
        text: str,
        language: str = "en",
    ):
        speech = NaverTTS(text, lang=language)
        speech.save(self.save_path)
        
        return self.save_path
        
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
