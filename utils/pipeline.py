from utils.model import Model

class Pipeline(Model):
    def __init__(
        self,
        transcribe_model: Model,
        generate_model: Model,
        synthesize_model: Model,
        forced_response: str = "",
    ):
        self.transcribe = transcribe_model.fn
        self.generate = generate_model.fn
        self.synthesize = synthesize_model.fn
        self.forced_response = forced_response

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

        if self.forced_response:
            message = self.forced_response
        else:
            message = "".join(self.generate(transcript))

        speech = self.synthesize(message)

        return transcript, message, speech
