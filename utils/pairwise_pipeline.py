from utils.model import Model

class PairwisePipeline(Model):
    def __init__(
        self,
        transcribe_model: Model,
        generate_model_1: Model,
        generate_model_2: Model,
        synthesize_model: Model,
        forced_response: str = "",
    ):
        self.transcribe = transcribe_model.fn
        self.generate_1 = generate_model_1.fn
        self.generate_2 = generate_model_2.fn
        self.synthesize = synthesize_model.fn
        self.forced_response = forced_response

        self.setup_interface(
            fn=self,
            inputs=transcribe_model.inputs,
            outputs=[
                *transcribe_model.outputs,
                *generate_model_1.outputs,
                *generate_model_2.outputs,
                *synthesize_model.outputs,
            ],
        )
    
    def __call__(self, *args, **kwargs):
        transcript = self.transcribe(*args, **kwargs)

        if self.forced_response:
            message1 = message2 = self.forced_response
        else:
            message1 = "".join(self.generate_1(transcript))
            message2 = "".join(self.generate_2(transcript))

        speech1 = self.synthesize(message1)
        speech2 = self.synthesize(message2)

        return transcript, message1, speech1, message2, speech2
