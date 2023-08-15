import os
import gradio as gr
import google.generativeai as palm
from utils.model import Model

class PaLM(Model):
    def __init__(
        self,
        api_key: str = "",
        model: str = "chat-bison-001",
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        assert (
            self.api_key
        ), "Please specify an --google_api_key"
        palm.configure(api_key=self.api_key)

        self.messages = []

        self.setup_interface(self.prompt, self.get_inputs(), self.get_outputs())

    def prompt(
        self,
        input,
        temperature=1.0,
        candidate_count=1,
        top_p=1.0,
        top_k=None,
    ):
        self.messages.append({
            "role": "user",
            "content": input,
        })

        chat = palm.chat(
            model=self.model,
            messages=self.messages,
            temperature=temperature,
            candidate_count=candidate_count,
            top_p=top_p,
            top_k=top_k,
        )
        role = chat.messages[-1]['role']
        reply = chat.messages[-1]['content']

        self.messages.append({
            "role": role,
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
                minimum=0, maximum=2, value=1, label="Temperature"
            ),
            gr.components.Slider(
                minimum=0, maximum=1, value=1, label="Top p"
            ),
            gr.components.Slider(
                minimum=0, maximum=100, step=1, default=None, label="Top k"
            ),
            gr.components.Slider(
                minimum=1, maximum=8, step=1, default=1, label="Candidate Count"
            ),
        ]
    
    def get_outputs(self):
        return [
            gr.components.Textbox(
                lines=5,
                label="Output",
            )
        ]
