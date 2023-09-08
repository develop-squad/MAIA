import gradio as gr
import logging
import random
import os
from utils.pairwise_form import PairwiseForm 

class ConversationForm(PairwiseForm):
    def __init__(self, model, title):
        self.guidance = {
            "irb_agreement":
                '''
                ## IRB Agreement
                ### 연구과제명 : 기억력 증강 대화 모델을 적용한 인텔리전트 어시스턴트
                본 연구는 기억력 증강 대화 모델을 통해 인텔리전트 어시스턴트(IA)의 기억 능력을 개선하는 연구입니다.
                IA는 음성 언어를 사용하여 사람과의 상호작용하며 일상생활을 지능적으로 지원하는 컴퓨터 시스템입니다.
                기존 IA는 장기적인 기억 능력이 부족하여 사용자와의 과거 대화나 선호도, 상태 및 행동을 충분히 반영하지 못하고 있습니다.
                본 연구를 통해, IA가 보다 개인화 된 경험을 사용자에게 제공할 수 있도록 하기 위한 방안을 탐구하고자 합니다.
                ''',
            "experiment_description":
                '''
                ## Experiment Description
                ### 1. 3가지 상황이 순차적으로 주어집니다.
                * 상황 1
                    1. “당신의 물건 하나를 선정하여 어디에 있는지 어시스턴트에게 알려주어라.”
                    2. “그 물건과 다른 토픽으로 대화를 5턴 해보아라.”
                    3. “처음 이야기한 물건을 어시스턴트가 기억하고 있는지 구체적으로 질문해 보아라.”
                * 상황 2
                    1. “최근 관심 있는 분야에 대해 어시스턴트에게 알려주어라.”
                    2. “그 분야와 전혀 관련 없는 토픽으로 대화를 5턴 해보아라.”
                    3. “처음 이야기한 분야를 어시스턴트가 기억하고 있는지 구체적으로 질문해 보아라.”
                * 상황 3
                    1. “작성 예정”
                    2. “작성 예정”
                    3. “작성 예정”
                ### 2. 주어지는 상황 가이드에 따라 IA와 대화해주세요.
                ### 3. 3가지 상황에 한 대화가 끝나면 자유롭게 IA와 대화해주세요.
                ''',
            "system_guide":
                '''
                ## System guide
                ### 1. MTurk Worker ID를 입력하고 "Save MTurk Worker ID" 버튼을 클릭하세요.
                ### 2. "Record from microphone" 버튼을 클릭하고 2초 대기 후 발화를 시작해주세요.
                ### 3. 발화가 끝났으면 "Stop recording" 버튼을 클릭하여 녹음을 완료해주세요.
                ### 4. IA가 답변하는 것을 기다려주세요.
                ### 5. [Model 1]과 [Model 2]에 대한 10가지 항목을 모두 평가해주세요.
                ### 6. 모두 평가했다면, 녹음된 음성 위의 x 버튼을 클릭하고, 다시 2단계부터 반복하여 주어진 상황을 완료해주세요.
                ### 7. 주어진 상황에 맞게 대화를 모두 완료했다면, "Finish this conversation" 버튼을 클릭해주세요.
                ### 8. 최종 평가를 진행하고, "Submit" 버튼을 클릭해주세요.
                ### 9. "Usability Evaluation" 사용성 평가를 진행해주세요.
                ### * 중간 단계에서 진행이 안된다면, "Reset" 버튼을 클릭하여 2단계부터 다시 진행할 수 있습니다.
                '''
        }
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

            with gr.Tab("IRB Agreement"):
                gr.Markdown(self.guidance['irb_agreement'])
                irb_agreement = gr.Radio(
                    show_label=False,
                    choices=[("Agree", 1), ("Disagree", 0)],
                    container=False
                )
                irb_button = gr.Button("Save IRB Agreement")
            with gr.Tab("System Guide"):
                with gr.Column():
                    gr.Markdown(self.guidance['experiment_description'])
                    gr.Markdown(self.guidance['system_guide'])
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
                            label="[Model 2] Is the response make sense?",
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
                    finish_message = gr.Markdown(
                        "### Thank you! :)",
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
                with gr.Column(visible=True) as usability_message_ui:
                    usability_message = gr.Markdown("### Please use the \"System\" first.")
                with gr.Column(visible=False) as usability_ui:
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
                    usability_button = gr.Button("Submit")
            
            irb_button.click(
                self.__save_irb_agreement,
                inputs=[irb_agreement, irb_button],
                outputs=[irb_agreement, irb_button],
                queue=False,
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
                outputs=[last_question, submit_button, usability_message_ui,
                         finish_message, usability_ui],
                queue=True,
            )
            
            usability_button.click(
                self.__submit,
                inputs=[id_input,
                        usability_question1,
                        usability_question2,
                        usability_question3,
                        usability_question4,
                        usability_question5,
                        usability_question6,
                        usability_question7,
                        usability_question8,
                        usability_question9,
                        usability_question10,],
                outputs=[usability_ui, usability_message, usability_message_ui],
                queue=True
            )
        
        return form

    def __save_irb_agreement(self, irb_agreement, irb_button):
        if not irb_agreement:
            return irb_agreement, irb_button
        return (gr.update(interactive=False), ) * 2
    
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
            return (id_input, save_id_button, ) + tuple(args)
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
        bot_message['normal_model'] = message1 if self.random_num == 0 else message2
        bot_message['augmented_model'] = message2 if self.random_num == 0 else message1
        
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
    
    def __submit(self, id_input, *args):
        # 에외처리 필요
        content = dict()
        content["mturk_worker_id"] = id_input
        if len(args) == 1:
            content["last_answer"] = args[0]
        else:
            content["usability_answer"] = list(args)
        self.logger.info(f"Benchmark: {str(content)}")
        
        if len(args) == 1:
            return (gr.update(visible=False), ) * 3 + (gr.update(visible=True), ) * 2
        else:
            return gr.update(visible=False), \
                    gr.update(value="### Thank you :)"), \
                    gr.update(visible=True)
