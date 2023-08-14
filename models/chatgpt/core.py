import os
import openai
import gradio as gr
from utils.model import Model

class ChatGPT(Model):
    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-3.5-turbo",
    ):
        super().__init__()

        openai.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        assert (
            openai.api_key
        ), "Please specify an --openai_api_key"

        self.model = model
        self.messages = []

        self.setup_interface(self.prompt, self.get_inputs(), self.get_outputs())

    def prompt(
        self,
        input,
        temperature=1.0, # 0~2.0
        top_p=1.0,
        frequency_penalty=0, # -2.0~2.0
        presence_penalty=0, # -2.0~2.0
        stop=["\n"], # up to 4 sequences
    ):
        self.messages.append({
            "role": "user",
            "content": input,
        })

        chat = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
        )
        role = chat.choices[0].message.role
        reply = chat.choices[0].message.content

        self.messages.append({
            "role": role,
            "content": reply,
        })

        return reply # Without streaming
        
    def get_inputs(self):
        return [
            gr.components.Textbox(
                lines=2,
                label="Input",
                placeholder="Tell me about GPT.",
            ),
            gr.components.Slider(
                minimum=0, maximum=2, value=1, label="Temperature"
            ),
            gr.components.Slider(
                minimum=0, maximum=1, value=1, label="Top p"
            ),
            gr.components.Slider(
                minimum=-2, maximum=2, value=0, label="Frequency penalty"
            ),
            gr.components.Slider(
                minimum=-2, maximum=2, value=0, label="Presence penalty"
            ),
        ]

    def get_outputs(self):
        return [
            gr.components.Textbox(
                lines=5,
                label="Output",
            ),
        ]
