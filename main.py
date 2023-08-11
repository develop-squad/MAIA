import fire
import gradio as gr
import torch

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
        share=share_gradio
    )

def main(
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
        title="MAIA",
    ).queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=share_gradio
    )

if __name__ == "__main__":
    fire.Fire(main)
