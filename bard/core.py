import os
import gradio as gr
import requests
from bardapi import Bard as BardAPI, SESSION_HEADERS

class Bard:
    def __init__(
        self,
        api_key: str = "",
    ):
        api_key = api_key or os.getenv("BARD_API_KEY", "")
        assert (
            api_key
        ), "Please specify an --bard_api_key"

        session = requests.Session()
        session.headers = SESSION_HEADERS
        session.cookies.set("__Secure-1PSID", api_key)
        session.cookies.set("__Secure-1PSIDTS", "")
        # session.cookies.set("__Secure-1PSIDCC", "")

        def prompt(
            input,
        ):
            chat = BardAPI(
                token=api_key,
                session=session,
            )
            response = chat.get_answer(input)
            reply = response['content']

            return reply
        
        self.fn = prompt
        self.inputs = [
            gr.components.Textbox(
                lines=2,
                label="Input",
                placeholder="Tell me about Bard.",
            ),
        ]
        self.outputs = [
            gr.components.Textbox(
                lines=5,
                label="Output",
            )
        ]
