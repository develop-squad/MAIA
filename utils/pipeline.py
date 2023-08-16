from utils.model import Model

class Pipeline(Model):
    def __init__(
        self,
        transcribe_model: Model,
        generate_model: Model,
        synthesize_model: Model,
    ):
        self.transcribe = transcribe_model.fn
        self.generate = generate_model.fn
        self.synthesize = synthesize_model.fn

        self.setup_interface(
            fn=self,
            inputs=transcribe_model.inputs,
            outputs=[
                *transcribe_model.outputs,
                *generate_model.outputs,
                *synthesize_model.outputs,
            ],
        )
    
    def __call__(self, *args, **kwargs):
        transcript = self.transcribe(*args, **kwargs)
        response = "".join(self.generate(transcript))
        speech = self.synthesize(response)
        return transcript, response, speech
