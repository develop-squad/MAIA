from utils.model import Model

class Pipeline:
    def __init__(
        self,
        transcribe_model: Model,
        generate_model: Model,
        tts_model: Model,
    ):
        self.fn = self
        self.transcribe = transcribe_model.fn
        self.generate = generate_model.fn
        self.tts = tts_model.fn
        self.inputs = transcribe_model.inputs
        self.outputs = [
            *transcribe_model.outputs,
            *generate_model.outputs,
            *tts_model.outputs,
        ]
    
    def __call__(self, *args, **kwargs):
        transcript = self.transcribe(*args, **kwargs)
        response = "".join(self.generate(transcript))
        tts = self.tts(response)
        return transcript, response, tts
