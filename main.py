import fire
import gradio as gr
import torch

from alpaca.core import Alpaca

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

try:
    if torch.backends.mps.is_available():
        device = "mps"
except:  # noqa: E722
    pass

def main(
    server_name: str = "0.0.0.0",
    server_port: int = 36000,
    share_gradio: bool = False,
):
    alpaca = Alpaca(
        device=device,
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
