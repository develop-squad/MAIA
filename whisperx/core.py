import gc
import gradio as gr
import torch

from . import whisperx

from utils.model import Model

class WhisperX(Model):
    def __init__(
        self,
        device: str = "cpu",
        device_index: int = 0,
        model_name: str = "large-v2",
        compute_type: str = "float16",  # reduce if low on GPU mem
        batch_size: int = 16,
    ):
        # 1. Transcribe with original whisper (batched)
        self.model = whisperx.load_model(model_name, device, device_index=device_index, compute_type=compute_type)
        self.device = device
        self.batch_size = batch_size

        self.setup_interface(self.transcribe, self.get_inputs(), self.get_outputs())
        
    def transcribe(
        self,
        audio_file: str,
        language: str = "en",
    ):
        # 1. Transcribe with original whisper (batched)
        audio = whisperx.load_audio(audio_file)
        result = self.model.transcribe(audio, batch_size=self.batch_size, language=language)

        # delete model if low on GPU resources
        del self.model
        gc.collect()
        torch.cuda.empty_cache()

        # 2. Align whisper output
        align_model, metadata = whisperx.load_align_model(language_code=result['language'] if language is None else language, device=self.device)
        result = whisperx.align(result["segments"], align_model, metadata, audio, self.device, return_char_alignments=False)

        # delete model if low on GPU resources
        del align_model
        gc.collect()
        torch.cuda.empty_cache()
        
        text_list = [data['text'].strip() + "\n" for data in result["segments"]]
        text = "".join(text_list).rstrip()
        return text
        
    def get_inputs(self):
        return [
            gr.components.Audio(
                label="STT Model",
                source="microphone",
                type="filepath",
            ),
        ]

    def get_outputs(self):
        return [
            gr.inputs.Textbox(
                label="Output",
            )
        ]
