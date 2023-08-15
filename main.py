import fire
from dotenv import load_dotenv
from utils.launch import Launcher, LaunchConfig
from utils.pipeline import Pipeline

load_dotenv()
launcher = Launcher()

def run_chatgpt(openai_api_key: str = "", **kwargs):
    from models.chatgpt.core import ChatGPT

    chatgpt = ChatGPT(api_key=openai_api_key)

    config = LaunchConfig(**kwargs, title="MAIA (ChatGPT Only)")
    launcher.launch_gradio(chatgpt, config)

def run_whisperx(**kwargs):
    from models.whisperx.core import WhisperX

    whisper = WhisperX(
        device=launcher.get_device(),
        device_index=0,
        compute_type="float16",
        batch_size=16,
    )

    config = LaunchConfig(**kwargs, title="MAIA (WhisperX Only)")
    launcher.launch_gradio(whisper, config)

def run_alpaca(**kwargs):
    from models.alpaca.core import Alpaca
    
    alpaca = Alpaca(
        device=launcher.get_device(),
        load_8bit=True,
        base_model="decapoda-research/llama-7b-hf",
        lora_weights="tloen/alpaca-lora-7b",
    )

    config = LaunchConfig(**kwargs, title="MAIA (Alpaca Only)")
    launcher.launch_gradio(alpaca, config)

def run_bard(bard_api_key: str = "", **kwargs):
    from models.bard.core import Bard
    
    bard = Bard(api_key=bard_api_key)

    config = LaunchConfig(**kwargs, title="MAIA (Bard Only)")
    launcher.launch_gradio(bard, config)

def run_palm(google_api_key: str = "", **kwargs):
    from models.palm.core import PaLM
    
    palm = PaLM(api_key=google_api_key)

    config = LaunchConfig(**kwargs, title="MAIA (PaLM Only)")
    launcher.launch_gradio(palm, config)

def main(**kwargs):
    from models.whisperx.core import WhisperX
    from models.alpaca.core import Alpaca
    
    whisper = WhisperX(
        device=launcher.get_device(),
        device_index=0,
        compute_type="float32",
        batch_size=16,
    )
    
    alpaca = Alpaca(
        device=launcher.get_device(),
        load_8bit=True,
        base_model="decapoda-research/llama-7b-hf",
        lora_weights="tloen/alpaca-lora-7b",
    )

    pipeline = Pipeline(
        transcribe_model=whisper,
        generate_model=alpaca,
    )

    config = LaunchConfig(**kwargs)
    launcher.launch_gradio(pipeline, config)

if __name__ == "__main__":
    fire.Fire(main)
