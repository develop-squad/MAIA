import gradio as gr
import typing

class Model:
    def __init__(self) -> None:
        self.inputs = []
        self.fn = None
        self.outputs = []
    
    def setup_interface(
        self,
        fn: typing.Callable,
        inputs: typing.List[gr.components.Component],
        outputs: typing.List[gr.components.Component],
    ) -> None:
        self.fn = fn
        self.inputs = inputs
        self.outputs = outputs

    def prompt(*args, **kwargs) -> str:
        return
