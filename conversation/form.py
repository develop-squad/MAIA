import gradio as gr
import logging
import random
import os
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

            with gr.Tab("IRB Agreement and Experiment Description"):
                gr.Markdown("## IRB Agreement")
                irb_agreement = gr.Radio(
                    show_label=False,
                    choices=[("Yes", 1), ("No", 0)]
                )
                with gr.Column():
                    gr.Markdown("## Experiment description")
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("1. Input your MTurk Worker ID and click 'Save MTurk Worker ID' button")
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("2. Input your MTurk Worker ID and click 'Save MTurk Worker ID' button")
            with gr.Tab("Usage guide"):
                with gr.Column():
                    gr.Markdown("## System guide")
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("1. Input your MTurk Worker ID and click \"Save MTurk Worker ID\" button.")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("2. Click \"Record\" button to input audio.")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("3. Please wait for IA to answer.")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("4. Model evaluation")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("5. 녹음된 음성 위의 x 버튼을 누르고, 다시 1부터 반복")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("6. Last evaluation")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("7. 1~6과정을 3번 반복")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("8. IA와 자유롭게 5턴 이상 대화")
                    
                    gr.Image(
                        "conversation/images/explain_image1.png",
                        show_label=False,
                        show_download_button=False
                    )
                    gr.Markdown("9. 사용성 평가")
            with gr.Tab("Guide for Situation"):
                with gr.Column():
                    gr.Markdown("### 1. 당신의 물건 하나를 선정하여 어디에 있는지 어시스턴트에게 알려주어라.")
                    gr.Markdown("### 2. 그 물건과 다른 토픽으로 대화를 5턴 해보아라.")
                    gr.Markdown("### 3. 처음 이야기한 물건을 어시스턴트가 기억하고 있는지 구체적으로 질문해 보아라.")
            with gr.Tab("System"):
                with gr.Row():
                    with gr.Column(scale=0.8):
                        id_input = gr.Textbox(
                            label="MTurk Worker ID",
                            show_label=True
                        )
                    with gr.Column(scale=0.2, min_width=0):
                        save_id_button = gr.Button("Save MTurk Worker ID")

                chatbot = gr.Chatbot(
                    elem_id="chatbot",
                    visible=False
                )

                with gr.Column():
                    with gr.Row():
                        question1 = gr.Radio(
                            scale=0.5,
                            choices=[
                                ("Strongly disagree", 1),
                                ("Disagree", 2),
                                ("Neither agree nor disagree", 3),
                                ("Agree", 4),
                                ("Strongly agree", 5)
                            ],
                            label="[Model 1] Is the response correct?",
                            show_label=True,
                            visible=False,
                        )
                        question4 = gr.Radio(
                            scale=0.5,
                            choices=[
                                ("Strongly disagree", 1),
                                ("Disagree", 2),
                                ("Neither agree nor disagree", 3),
                                ("Agree", 4),
                                ("Strongly agree", 5)
                            ],
                            label="[Model 2] Is the response correct?",
                            show_label=True,
                            visible=False,
                        )
                    with gr.Row():
                        question2 = gr.Radio(
                            scale=0.5,
                            choices=[
                                ("Strongly disagree", 1),
                                ("Disagree", 2),
                                ("Neither agree nor disagree", 3),
                                ("Agree", 4),
                                ("Strongly agree", 5)
                            ],
                            label="[Model 1] Is the context of the response consistent?",
                            show_label=True,
                            visible=False,
                        )
                        question5 = gr.Radio(
                            scale=0.5,
                            choices=[
                                ("Strongly disagree", 1),
                                ("Disagree", 2),
                                ("Neither agree nor disagree", 3),
                                ("Agree", 4),
                                ("Strongly agree", 5)
                            ],
                            label="[Model 2] Is the context of the response consistent?",
                            show_label=True,
                            visible=False,
                        )
                    with gr.Row():
                        question3 = gr.Radio(
                            scale=0.5,
                            choices=[
                                ("Strongly disagree", 1),
                                ("Disagree", 2),
                                ("Neither agree nor disagree", 3),
                                ("Agree", 4),
                                ("Strongly agree", 5)
                            ],
                            label="[Model 1] Are you interested in the response? Would you like to continue the conversation?",
                            show_label=True,
                            visible=False,
                        )
                        question6 = gr.Radio(
                            scale=0.5,
                            choices=[
                                ("Strongly disagree", 1),
                                ("Disagree", 2),
                                ("Neither agree nor disagree", 3),
                                ("Agree", 4),
                                ("Strongly agree", 5)
                            ],
                            label="[Model 2] Are you interested in the response? Would you like to continue the conversation?",
                            show_label=True,
                            visible=False,
                        )
                with gr.Column():
                    pairwise_question1 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="Which response makes more sense?",
                        show_label=True,
                        visible=False,
                    )
                    pairwise_question2 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="Which response is more consistent?",
                        show_label=True,
                        visible=False,
                    )
                    pairwise_question3 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="Which response is more interesting?",
                        show_label=True,
                        visible=False,
                    )
                    pairwise_question4 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="Based on your current response,\
                            which assistant would you prefer to have a longer conversation with?\
                                The conversation will continue with the assistant you choose.",
                        show_label=True,
                        visible=False,
                    )
                with gr.Column():
                    audio_record = gr.Audio(
                        show_label=False,
                        source="microphone",
                        type="filepath",
                        visible=False,
                    )
                with gr.Column():
                    reset_button = gr.Button(
                        "Reset this message",
                        visible=False
                    )
                with gr.Column():
                    text_input = gr.Textbox(
                        show_label=False,
                        visible=False
                    )
                    text_input.style(container=False)
                with gr.Column():
                    finish_message = gr.Textbox(
                        "Thank you! :)",
                        visible=False,
                        show_label=False
                    )
                with gr.Column():
                    finish_button = gr.Button(
                        "Finish this conversation",
                        visible=False
                    )
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
            with gr.Tab("Usability Evaluation"):
                with gr.Column():
                    usability_question1 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I think that I would like to use this system frequently.",
                        show_label=True
                    )
                    usability_question2 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I found the system unnecessarily complex.",
                        show_label=True,
                    )
                    usability_question3 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I thought the system was easy to use.",
                        show_label=True
                    )
                    usability_question4 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I think that I would need the support of a technical person to be able to use this system.",
                        show_label=True
                    )
                    usability_question5 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I found the various functions in this system were well integrated.",
                        show_label=True
                    )
                    usability_question6 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I thought there was too much inconsistency in this system.",
                        show_label=True
                    )
                    usability_question7 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I would imagine that most people would learn to use this system very quickly.",
                        show_label=True
                    )
                    usability_question8 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I found the system very cumbersome to use.",
                        show_label=True
                    )
                    usability_question9 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I felt very confident using the system.",
                        show_label=True
                    )
                    usability_question10 = gr.Radio(
                        choices=[
                            ("Strongly disagree", 1),
                            ("Disagree", 2),
                            ("Neither agree nor disagree", 3),
                            ("Agree", 4),
                            ("Strongly agree", 5)
                        ],
                        label="I needed to learn a lot of things before I could get going with this system.",
                        show_label=True
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

            save_id_button.click(
                self.__save_id,
                inputs=[id_input, save_id_button,
                        chatbot, audio_record, text_input, finish_button],
                outputs=[id_input, save_id_button,
                         chatbot, audio_record, text_input, finish_button],
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
                outputs=[question1, question2, question3, question4, question5, question6,
                         pairwise_question1, pairwise_question2, pairwise_question3, pairwise_question4],
                queue=True,
            ).then(
                lambda: gr.update(visible=True),
                outputs=[reset_button],
                queue=False
            )
            
            audio_record.change(
                self.__save_benchmark,
                inputs=[id_input, chatbot,
                        question1, question2, question3,
                        question4, question5, question6,
                        pairwise_question1, pairwise_question2, pairwise_question3, pairwise_question4],
                outputs=[question1, question2, question3,
                         question4, question5, question6,
                         pairwise_question1, pairwise_question2, pairwise_question3, pairwise_question4],
                queue=True,
            ).then(
                lambda: gr.update(visible=False),
                outputs=[reset_button],
                queue=False,
            )
            
            reset_button.click(
                self.__reset,
                inputs=id_input,
                outputs=[question1, question2, question3,
                         question4, question5, question6,
                         pairwise_question1, pairwise_question2, pairwise_question3, pairwise_question4],
                queue=True
            ).then(
                lambda: (gr.update(value=None),) * 2,
                inputs=None,
                outputs=[chatbot, audio_record],
                queue=False
            ).then(
                lambda: gr.update(visible=False),
                outputs=[reset_button],
                queue=False
            )
            
            finish_button.click(
                self.__deactivate_assistant,
                inputs=None,
                outputs=[chatbot, audio_record, text_input, finish_button],
                queue=True,
            ).then(
                self.__activate_assistant,
                inputs=None,
                outputs=[last_question, submit_button],
                queue=False
            )
            
            submit_button.click(
                self.__submit,
                inputs=[id_input, last_question],
                outputs=[last_question, submit_button],
                queue=True
            ).then(
                lambda: gr.update(visible=True),
                inputs=None,
                outputs=[finish_message],
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
    
    def __save_id(self, id_input, save_id_button, *args):
        if not id_input:
            return id_input, save_id_button
        return (gr.update(interactive=False), ) * 2 \
                + (gr.update(visible=True), ) * len(args)
    
    def __activate_benchmark(self):
        return (gr.update(value=None, visible=True), ) * 10
    
    def __save_benchmark(self, id_input, chatbot, *args):
        all_questions = list(args)
        if None in all_questions:
            return tuple(all_questions)
        
        message1 = chatbot[-1][1].split('</audio>')[1].split('<br/>')[0]
        message2 = chatbot[-1][1].split('</audio>')[-1]
        
        bot_message = dict()
        bot_message['chatgpt'] = message1 if self.random_num == 0 else message2
        bot_message['palm'] = message2 if self.random_num == 0 else message1
        
        content = dict()
        content["mturk_worker_id"] = id_input
        content["speech"] = chatbot[-1][0]
        content["bot_message"] = bot_message
        content["answer"] = all_questions
        self.logger.info(f"Benchmark: {str(content)}")
        
        return (gr.update(value=None, visible=False), ) * (2 + len(args))
    
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

        self.random_num = random.randrange(2)
        speech_data = f"data:audio/wav;base64,{speech if self.random_num == 0 else speech2}"
        output = f"[Model 1]<br/><audio controls autoplay src=\"{speech_data}\" type=\"audio/wav\"></audio>"
        output += message if self.random_num == 0 else message2
        
        speech_data = f"data:audio/wav;base64,{speech2 if self.random_num == 0 else speech}"
        output += f"<br/><br/>[Model 2]<br/><audio controls src=\"{speech_data}\" type=\"audio/wav\"></audio>"
        output += message2 if self.random_num == 0 else message
        
        print(f"- Assistant 1: {message if self.random_num == 0 else message2}")
        print(f"- Assistant 2: {message2 if self.random_num == 0 else message}")

        history[-1] = (transcript, output)
        return history
    
    def __reset(self, id_input):
        content = dict()
        content['mturk_worker_id'] = id_input
        content['message'] = "The conversation history has been reset."
        self.logger.info(f"Benchmark: {str(content)}")
        return (gr.update(value=None, visible=False), ) * 10
    
    def __deactivate_assistant(self):
        return gr.update(value=None, visible=False),\
            gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
    
    def __activate_assistant(self):
        return gr.update(visible=True), gr.update(visible=True)
    
    def __submit(self, id_input, last_question):
        content = dict()
        content["mturk_worker_id"] = id_input
        content["last_answer"] = last_question
        self.logger.info(f"Benchmark: {str(content)}")
        
        return gr.update(visible=False), gr.update(visible=False)
