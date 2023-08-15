import fire
import gradio as gr
import torch
import os
from typing import Callable
from dotenv import load_dotenv

load_dotenv()
SSL_CERT_PATH = os.environ.get("SSL_CERT_PATH")
SSL_KEY_PATH = os.environ.get("SSL_KEY_PATH")

if not SSL_CERT_PATH or not SSL_KEY_PATH:
    raise ValueError("Please set the SSL_CERT_PATH and SSL_KEY_PATH environment variables.")

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

def run_chatgpt(
    openai_api_key: str = "",
    server_name: str = "0.0.0.0",
    server_port: int = 36000,
    share_gradio: bool = False,
):
    from chatgpt.core import ChatGPT
    
    chatgpt = ChatGPT(api_key=openai_api_key)
    
    gr.Interface(
        fn=chatgpt.fn,
        inputs=chatgpt.inputs,
        outputs=chatgpt.outputs,
        title="MAIA (ChatGPT Only)",
    ).queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=share_gradio,
    )

def run_whisperx(
    server_name: str = "0.0.0.0",
    server_port: int = 36000,
    share_gradio: bool = False,
):
    from whisperx.core import WhisperX
    
    whisper = WhisperX(
        device=get_device(),
        device_index=0,
        compute_type="float16",
        batch_size=16,
    )

    gr.Interface(
        fn=whisper.fn,
        inputs=whisper.inputs,
        outputs=whisper.outputs,
        title="MAIA (WhisperX Only)",
    ).queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=share_gradio,
    )

def run_alpaca(
    server_name: str = "0.0.0.0",
    server_port: int = 36000,
    share_gradio: bool = False,
):
    from alpaca.core import Alpaca
    
    alpaca = Alpaca(
        device=get_device(),
        load_8bit=True,
        base_model="decapoda-research/llama-7b-hf",
        lora_weights="tloen/alpaca-lora-7b",
    )

    gr.Interface(
        fn=alpaca.fn,
        inputs=alpaca.inputs,
        outputs=alpaca.outputs,
        title="MAIA (Alpaca Only)",
    ).queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=share_gradio,
    )

def run_bard(
    bard_api_key: str = "",
    server_name: str = "0.0.0.0",
    server_port: int = 36000,
    share_gradio: bool = False,
):
    from bard.core import Bard
    
    bard = Bard(api_key=bard_api_key)

    gr.Interface(
        fn=bard.fn,
        inputs=bard.inputs,
        outputs=bard.outputs,
        title="MAIA (Bard Only)",
    ).queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=share_gradio,
    )

def run_palm(
    google_api_key: str = "",
    server_name: str = "0.0.0.0",
    server_port: int = 36000,
    share_gradio: bool = False,
):
    from palm.core import PaLM
    
    palm = PaLM(api_key=google_api_key)

    gr.Interface(
        fn=palm.fn,
        inputs=palm.inputs,
        outputs=palm.outputs,
        title="MAIA (PaLM Only)",
    ).queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=share_gradio,
    )

def main(
    server_name: str = "0.0.0.0",
    server_port: int = 36000,
    share_gradio: bool = False,
):
    from whisperx.core import WhisperX
    from alpaca.core import Alpaca
    
    whisper = WhisperX(
        device=get_device(),
        device_index=0,
        compute_type="float32",
        batch_size=16,
    )
    
    alpaca = Alpaca(
        device=get_device(),
        load_8bit=True,
        base_model="decapoda-research/llama-7b-hf",
        lora_weights="tloen/alpaca-lora-7b",
    )

    def pipeline(
        transcribe: Callable[..., str],
        generate: Callable[..., str],
    ):
        def inference(*args, **kwargs):
            transcript = transcribe(*args, **kwargs)
            response = "".join(generate(transcript))
            return response
        return inference

    gr.Interface(
        fn=pipeline(whisper.fn, alpaca.fn),
        inputs=whisper.inputs,
        outputs=alpaca.outputs,
        title="MAIA",
    ).queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=share_gradio,
        ssl_certfile=SSL_CERT_PATH,
        ssl_keyfile=SSL_KEY_PATH,
    )

if __name__ == "__main__":
    gr.close_all()
    fire.Fire(main)
