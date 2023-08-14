import gradio as gr
import typing

class Model:
    def __init__(self):
        self.fn = None
        self.inputs = []
        self.outputs = []
    
    def setup_interface(
        self,
        fn: typing.Callable,
        inputs: typing.List[gr.Interface.Component],
        outputs: typing.List[gr.Interface.Component],
    ):
        self.fn = fn
        self.inputs = inputs
        self.output = outputs
