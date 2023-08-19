import os
import gradio as gr
import google.generativeai as palm
from utils.model import Model

class PaLM(Model):
    def __init__(
        self,
        api_key: str = "",
        model: str = "models/chat-bison-001",
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        assert (
            self.api_key
        ), "Please specify an --google_api_key"
        palm.configure(api_key=self.api_key)

        self.model = palm.get_model(model)
        self.messages = []

        self.setup_interface(self.prompt, self.get_inputs(), self.get_outputs())

    def prompt(
        self,
        input,
        temperature=0.25,
        top_p=0.95,
        top_k=40,
    ):
        self.messages.append({
            "author": "user",
            "content": input,
        })

        chat = palm.chat(
            model=self.model,
            messages=self.messages,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )
        author = chat.messages[-1]['author']
        reply = chat.messages[-1]['content']

        self.messages.append({
            "author": author,
            "content": reply
        })

        return reply
    
    def get_inputs(self):
        return [
            gr.components.Textbox(
                lines=2,
                label="Input",
                placeholder="Tell me about PaLM.",
            ),
            gr.components.Slider(
                minimum=0, maximum=2, value=0.25, label="Temperature"
            ),
            gr.components.Slider(
                minimum=0, maximum=1, value=0.95, label="Top p"
            ),
            gr.components.Slider(
                minimum=0, maximum=100, step=1, value=40, label="Top k"
            ),
        ]
    
    def get_outputs(self):
        return [
            gr.components.Textbox(
                lines=5,
                label="Output",
            )
        ]
