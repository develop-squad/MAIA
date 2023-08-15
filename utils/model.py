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
        inputs: typing.List[gr.components.Component],
        outputs: typing.List[gr.components.Component],
    ):
        self.fn = fn
        self.inputs = inputs
        self.outputs = outputs
