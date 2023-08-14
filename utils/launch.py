import os
import torch
import gradio as gr
from dataclasses import dataclass
from .model import Model

@dataclass
class LaunchConfig:
    title: str = "MAIA"
    server_name: str = "0.0.0.0"
    server_port: int = 443
    share_gradio: bool = False

class Launcher:
    def __init__(self):
        self.SSL_CERT_PATH = os.environ.get("SSL_CERT_PATH")
        self.SSL_KEY_PATH = os.environ.get("SSL_KEY_PATH")
        
        if not self.SSL_CERT_PATH or not self.SSL_KEY_PATH:
            raise ValueError("Please set the SSL_CERT_PATH and SSL_KEY_PATH environment variables.")
    
    @staticmethod
    def get_device():
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

        try:
            if torch.backends.mps.is_available():
                device = "mps"
        except:  # noqa: E722
            pass

        return device

    def launch_gradio(
        self,
        model: Model,
        config: LaunchConfig
    ) -> tuple:
        gr.close_all()
        return gr.Interface(
            fn=model.fn,
            inputs=model.inputs,
            outputs=model.outputs,
            title=config.title,
        ).queue().launch(
            server_name=config.server_name,
            server_port=config.server_port,
            share=config.share_gradio,
            ssl_certfile=self.SSL_CERT_PATH,
            ssl_keyfile=self.SSL_KEY_PATH,
        )
