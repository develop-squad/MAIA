import gradio as gr
from utils.form import Form

class ConversationForm(Form):
    def __init__(self, model, title):
        super().__init__(model=model, title=title)
    
    def _create_form(self) -> gr.Blocks:
        with gr.Blocks(css="#chatbot") as form:
            gr.HTML(f"<h1 style=\"text-align: center;\">{self.title}</h1>")
            
            chatbot = gr.Chatbot(elem_id="chatbot")

            with gr.Row():
                with gr.Column(scale=0.85):
                    audio_record = gr.Audio(
                        show_label=False,
                        source="microphone",
                        type="filepath",
                    )
                with gr.Column(scale=0.15, min_width=0):
                    audio_file = gr.UploadButton(
                        "📁",
                        file_types=["audio"],
                    )
            with gr.Row():
                text_input = gr.Textbox(show_label=False)
                text_input.style(container=False)
            
            text_input.submit(
                self.__add_text,
                inputs=[chatbot, text_input],
                outputs=[chatbot, text_input],
                queue=False,
            ).then(
                self.__process,
                inputs=chatbot,
                outputs=chatbot,
                queue=True
            ).then(
                lambda: gr.update(interactive=True),
                inputs=None,
                outputs=[text_input],
                queue=False
            )

            audio_record.change(
                self.__add_record,
                inputs=[chatbot, audio_record],
                outputs=[chatbot],
                queue=False,
            ).then(
                self.__process,
                inputs=chatbot,
                outputs=chatbot,
                queue=True
            ).then(
                lambda: gr.update(interactive=True),
                inputs=None,
                outputs=[audio_record],
                queue=False
            )

            audio_file.upload(
                self.__add_audio,
                inputs=[chatbot, audio_file],
                outputs=[chatbot, audio_file],
                queue=True,
            ).then(
                self.__process,
                inputs=chatbot,
                outputs=chatbot,
                queue=True
            ).then(
                lambda: gr.update(interactive=True),
                inputs=None,
                outputs=[audio_file],
                queue=False
            )
        
        return form

    def __add_text(self, history, text_input):
        history = history + [(text_input, None)]
        return history, gr.update(value="", interactive=False)
    
    def __add_record(self, history, audio_record):
        if not audio_record:
            return history
        history = history + [((audio_record,), None)]
        return history

    def __add_audio(self, history, audio_file):
        history = history + [((audio_file.name,), None)]
        return history, gr.update(value="", interactive=False)
    
    def __process(self, history):
        input = history[-1][0]

        if isinstance(input, str):
            response = self.model.fn(text_input=input)
        elif isinstance(input, tuple):
            response = self.model.fn(audio_file=input[0])
        else:
            response = self.model.fn(
                text_input=input,
                forced_response="I can't process this type of input.",
            )
        transcript, message, speech = response
        print(f"- User: {transcript}")
        print(f"- Assistant: {message}")

        speech_data = f"data:audio/wav;base64,{speech}"
        output = f"<audio controls autoplay src=\"{speech_data}\" type=\"audio/wav\"></audio>"
        output += message

        history[-1] = (transcript, output)
        return history
