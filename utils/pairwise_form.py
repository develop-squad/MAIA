import gradio as gr
from .pairwise_pipeline import PairwisePipeline

class PairwiseForm:
    def __init__(
        self,
        model: PairwisePipeline,
        title: str,
    ):
        self.model = model
        self.title = title
        self._form = self._create_form()
    
    def _create_form(self) -> gr.Blocks:
        with gr.Blocks() as form:
            gr.Interface(
                fn=self.model.fn,
                inputs=self.model.inputs,
                outputs=self.model.outputs,
                title=self.title,
            )
        
        return form

    def get_form(self) -> gr.Blocks:
        if self._form is None:
            raise NotImplementedError("The _form attribute has not been initialized.")
        return self._form
