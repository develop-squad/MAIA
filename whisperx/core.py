import gc

import gradio as gr
import torch

from . import whisperx

class WhisperX:
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
        
        def transcribe(
            audio_file: str,
            language: str = "en",
        ):
            # 1. Transcribe with original whisper (batched)
            audio = whisperx.load_audio(audio_file)
            result = self.model.transcribe(audio, batch_size=batch_size, language=language)

            # delete model if low on GPU resources
            del self.model
            gc.collect()
            torch.cuda.empty_cache()

            # 2. Align whisper output
            align_model, metadata = whisperx.load_align_model(language_code=result['language'] if language is None else language, device=device)
            result = whisperx.align(result["segments"], align_model, metadata, audio, device, return_char_alignments=False)

            # delete model if low on GPU resources
            del align_model
            gc.collect()
            torch.cuda.empty_cache()
            
            text_list = [data['text'].strip() + "\n" for data in result["segments"]]
            text = "".join(text_list).rstrip()
            return text
        
        self.fn = transcribe
        self.inputs = [
            gr.components.Audio(
                label="STT Model",
                type="filepath",
            ),
        ]
        self.outputs = [
            gr.inputs.Textbox(
                label="Output",
            )
        ]
