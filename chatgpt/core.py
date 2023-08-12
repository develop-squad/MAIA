import os

import openai
import gradio as gr

class ChatGPT:
    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-3.5-turbo",
    ):
        openai.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        assert (
            openai.api_key
        ), "Please specify an --openai_api_key"

        messages = []

        def prompt(
            input,
            temperature=1.0, # 0~2.0
            top_p=1.0,
            frequency_penalty=0, # -2.0~2.0
            presence_penalty=0, # -2.0~2.0
            stop=["\n"], # up to 4 sequences
        ):
            messages.append({
                "role": "user",
                "content": input,
            })

            chat = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
            )
            role = chat.choices[0].message.role
            reply = chat.choices[0].message.content

            messages.append({
                "role": role,
                "content": reply,
            })

            return reply # Without streaming
        
        self.fn = prompt
        self.inputs = [
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
        self.outputs = [
            gr.components.Textbox(
                lines=5,
                label="Output",
            )
        ]
