from utils.model import Model

class Pipeline(Model):
    def __init__(
        self,
        transcribe_model: Model,
        generate_model: Model,
        #synthesize_model: Model,
        forced_response: str = "",
    ):
        self.transcribe = transcribe_model.fn
        self.generate = generate_model.fn
        #self.synthesize = synthesize_model.fn
        self.forced_response = forced_response

        self.setup_interface(
            fn=self,
            inputs=transcribe_model.inputs,
            outputs=[
                *transcribe_model.outputs,
                *generate_model.outputs,
                #*synthesize_model.outputs,
            ],
        )
    
    def __call__(self, *args, **kwargs):
        transcript = self.transcribe(*args, **kwargs)

        if self.forced_response:
            message = self.forced_response
        else:
            message = "".join(self.generate(transcript))

        #speech = self.synthesize(message)

        return transcript, message

class PairwisePipeline(Pipeline):
    def __init__(
        self,
        transcribe_model: Model,
        generate_model_1: Model,
        generate_model_2: Model,
        forced_response: str = "",
    ):
        def generate_1_wrapper(*args, **kwargs):
            return generate_model_1.fn(*args, stop=["\n"], **kwargs)

        self.transcribe = transcribe_model.fn
        self.generate_1 = generate_1_wrapper
        self.generate_1_name = generate_model_1.name
        self.generate_2 = generate_model_2.fn
        self.generate_2_name = generate_model_2.name
        self.forced_response = forced_response

        self.setup_interface(
            fn=self,
            inputs=transcribe_model.inputs,
            outputs=[
                *transcribe_model.outputs,
                *generate_model_1.outputs,
                *generate_model_2.outputs,
            ],
        )
        
    def set_wrapper(self, model: Model):
        def generate_1_wrapper(*args, **kwargs):
            return model.fn(*args, stop=["\n"], **kwargs)
        
        self.generate_1 = generate_1_wrapper
    
    def __call__(self, *args, **kwargs):
        transcript = self.transcribe(*args, **kwargs)

        if self.forced_response:
            message1 = message2 = self.forced_response
        else:
            message1 = "".join(self.generate_1(transcript))
            message2 = "".join(self.generate_2(transcript))

        return transcript, message1, message2
