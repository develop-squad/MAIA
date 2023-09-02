import gradio as gr
import logging
import random
from utils.pairwise_form import PairwiseForm 

class ConversationForm(PairwiseForm):
    def __init__(self, model, title):
        super().__init__(model=model, title=title)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        self.file_handler = logging.FileHandler("benchmark.log")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
    
    def _create_form(self) -> gr.Blocks:
        with gr.Blocks(css="#chatbot") as form:
            gr.HTML(f"<h1 style=\"text-align: center;\">{self.title}</h1>")

            with gr.Row():
                with gr.Column(scale=0.85):
                    name_input = gr.Textbox(
                        label="Name",
                        show_label=True
                    )
                with gr.Column(scale=0.15, min_width=0):
                    name_button = gr.Button("Save name")

            chatbot = gr.Chatbot(elem_id="chatbot")

            with gr.Column():
                question1 = gr.Radio(
                    choices=[
                        ("Strongly disagree", 1),
                        ("Disagree", 2),
                        ("Neither agree nor disagree", 3),
                        ("Agree", 4),
                        ("Strongly agree", 5)
                    ],
                    label="Is the response correct?",
                    show_label=True,
                    visible=False,
                )
                question2 = gr.Radio(
                    choices=[
                        ("Strongly disagree", 1),
                        ("Disagree", 2),
                        ("Neither agree nor disagree", 3),
                        ("Agree", 4),
                        ("Strongly agree", 5)
                    ],
                    label="Is the context of the response consistent?",
                    show_label=True,
                    visible=False,
                )
                question3 = gr.Radio(
                    choices=[
                        ("Strongly disagree", 1),
                        ("Disagree", 2),
                        ("Neither agree nor disagree", 3),
                        ("Agree", 4),
                        ("Strongly agree", 5)
                    ],
                    label="Are you interested in the response? Would you like to continue the conversation?",
                    show_label=True,
                    visible=False,
                )
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
            with gr.Row():
                finish_button = gr.Button("Finish this conversation")
            with gr.Row():
                with gr.Column(scale=0.7):
                    last_question = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="How was the conversation?",
                        show_label=True,
                        visible=False,
                    )
                with gr.Column(scale=0.3, min_width=0):
                    submit_button = gr.Button(
                        "Submit",
                        visible=False,
                    )
            
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

            name_button.click(
                self.__save_name,
                inputs=[name_input, name_button],
                outputs=[name_input, name_button],
                queue=False,
            )

            audio_record.stop_recording(
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
            ).then(
                self.__activate_benchmark,
                outputs=[question1, question2, question3],
                queue=True,
            )
            
            audio_record.change(
                self.__save_benchmark,
                inputs=[name_input, chatbot, question1, question2, question3],
                outputs=[question1, question2, question3],
                queue=True,
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
            
            finish_button.click(
                self.__deactivate_assistant,
                inputs=None,
                outputs=[chatbot, audio_record, audio_file, text_input, finish_button],
                queue=True,
            ).then(
                self.__activate_assistant,
                inputs=None,
                outputs=[last_question, submit_button],
                queue=False
            )
            
            submit_button.click(
                self.__submit,
                inputs=[name_input, last_question],
                outputs=[last_question, submit_button],
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
    
    def __save_name(self, name_input, name_button):
        if not name_input:
            return name_input, name_button
        return gr.update(interactive=False), gr.update(interactive=False)
    
    def __activate_benchmark(self):
        return gr.update(value=None, visible=True), \
                gr.update(value=None, visible=True), \
                gr.update(value=None, visible=True)
    
    def __save_benchmark(self, name_input, chatbot, question1, question2, question3):
        if not question1 and not question2 and not question3:
            return question1, question2, question3
        
        content = dict()
        content["name"] = name_input
        content["speech"] = chatbot[-1][0]
        content["bot_message"] = chatbot[-1][1].split('</audio>')[-1]
        content["answer"] = [question1, question2, question3]
        self.logger.info(f"Benchmark: {str(content)}")
        
        return gr.update(value=None, visible=False), \
                gr.update(value=None, visible=False), \
                gr.update(value=None, visible=False)
    
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
        transcript, message, speech, message2, speech2 = response
        print(f"- User: {transcript}")

        random_num = random.randrange(2)
        if random_num == 0:
            speech_data = f"data:audio/wav;base64,{speech}"
            output = f"[Model 1]<br/><audio controls autoplay src=\"{speech_data}\" type=\"audio/wav\"></audio>"
            output += message
        
            speech_data = f"data:audio/wav;base64,{speech2}"
            output += f"<br/><br/>[Model 2]<br/><audio controls src=\"{speech_data}\" type=\"audio/wav\"></audio>"
            output += message2
            
            print(f"- Assistant 1: {message}")
            print(f"- Assistant 2: {message2}")
        else:
            speech_data = f"data:audio/wav;base64,{speech2}"
            output = f"[Model 1]<br/><audio controls autoplay src=\"{speech_data}\" type=\"audio/wav\"></audio>"
            output += message2
        
            speech_data = f"data:audio/wav;base64,{speech}"
            output += f"<br/><br/>[Model 2]<br/><audio controls src=\"{speech_data}\" type=\"audio/wav\"></audio>"
            output += message
            
            print(f"- Assistant 1: {message2}")
            print(f"- Assistant 2: {message}")

        history[-1] = (transcript, output)
        return history
    
    def __deactivate_assistant(self):
        return gr.update(visible=False), \
                gr.update(visible=False), \
                gr.update(visible=False), \
                gr.update(visible=False), \
                gr.update(visible=False)
    
    def __activate_assistant(self):
        return gr.update(visible=True), gr.update(visible=True)
    
    def __submit(self, name_input, last_question):
        content = dict()
        content["name"] = name_input
        content["last_answer"] = last_question
        self.logger.info(f"Benchmark: {str(content)}")
        
        return gr.update(visible=False), gr.update(visible=False)
