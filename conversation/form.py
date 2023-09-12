import gradio as gr
import logging
import random
import json
import os
import os.path as osp
from utils.form import PairwiseForm

class ConversationForm(PairwiseForm):
    def __init__(self, model, title):
        self.scales = {
            "likert": [
                ("Strongly disagree", 1),
                ("Disagree", 2),
                ("Neither agree nor disagree", 3),
                ("Agree", 4),
                ("Strongly agree", 5),
            ],
            "comparison": [
                ("Model 1", 1),
                ("Model 2", 2),
            ],
        }
        self.situations = self.__load_scenario("hit")
        self.guidance = {
            "informed_consent": self.__load_guidance("informed_consent"),
            "experiment_description": self.__load_experiment_description("experiment_description", self.situations),
            "system_guide": self.__load_guidance("system_guide"),
            "system_usage_instruction": self.__load_guidance("system_usage_instruction"),
        }
        self.situation_idx = 0
        self.data = {
            "mturk_worker_id": "N/A",
            "result": {
                "situation1": list(),
                "situation2": list(),
                "situation3": list(),
                "last_answer": -1,          # -1 means None(=null)
                "usability_answer": list()
            }
        }
        self.data_path = "results"

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
                gr.Markdown(self.guidance['informed_consent'])
                informed_consent = gr.Radio(
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

                with gr.Column():
                    situation_title = gr.Markdown(
                        "## System Usage Instruction",
                        visible=False
                    )
                    situation_description = gr.Markdown(
                        self.guidance["system_usage_instruction"]
                            .format("\n".join([f"{i+1}. {situation}" for i, situation in enumerate(self.situations[self.situation_idx])])),
                        visible=False
                    )
                chatbot = gr.Chatbot(
                    elem_id="chatbot",
                    visible=False
                )

                with gr.Column():
                    with gr.Row():
                        question1 = gr.Radio(
                            scale=0.5,
                            choices=self.scales["likert"],
                            label="[Model 1] Is the response make sence?",
                            show_label=True,
                            visible=False,
                        )
                        question4 = gr.Radio(
                            scale=0.5,
                            choices=self.scales["likert"],
                            label="[Model 2] Is the response make sense?",
                            show_label=True,
                            visible=False,
                        )
                    with gr.Row():
                        question2 = gr.Radio(
                            scale=0.5,
                            choices=self.scales["likert"],
                            label="[Model 1] Is the context of the response consistent?",
                            show_label=True,
                            visible=False,
                        )
                        question5 = gr.Radio(
                            scale=0.5,
                            choices=self.scales["likert"],
                            label="[Model 2] Is the context of the response consistent?",
                            show_label=True,
                            visible=False,
                        )
                    with gr.Row():
                        question3 = gr.Radio(
                            scale=0.5,
                            choices=self.scales["likert"],
                            label="[Model 1] Are you interested in the response? Would you like to continue the conversation?",
                            show_label=True,
                            visible=False,
                        )
                        question6 = gr.Radio(
                            scale=0.5,
                            choices=self.scales["likert"],
                            label="[Model 2] Are you interested in the response? Would you like to continue the conversation?",
                            show_label=True,
                            visible=False,
                        )
                with gr.Column():
                    with gr.Row():
                        pairwise_question1 = gr.Radio(
                            choices=self.scales["comparison"],
                            label="Which response makes more sense?",
                            show_label=True,
                            visible=False,
                        )
                        pairwise_question2 = gr.Radio(
                            choices=self.scales["comparison"],
                            label="Which response is more consistent?",
                            show_label=True,
                            visible=False,
                        )
                    with gr.Row():
                        pairwise_question3 = gr.Radio(
                            choices=self.scales["comparison"],
                            label="Which response is more interesting?",
                            show_label=True,
                            visible=False,
                        )
                        pairwise_question4 = gr.Radio(
                            choices=self.scales["comparison"],
                            label="Who do you prefer to talk to more?",
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
                        "Reset this conversation",
                        visible=False
                    )
                with gr.Column():
                    text_input = gr.Textbox(
                        show_label=False,
                        visible=False
                    )
                    text_input_message = gr.Markdown(
                        "Please use Text input when microphone is not working well.",
                        visible=False
                    )
                    text_input.style(container=False)
                    text_input_button = gr.Button(
                        "Save evaluation results",
                        visible=False,
                    )
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
                            choices=self.scales["likert"],
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
                        choices=self.scales["likert"],
                        label="I think that I would like to use this system frequently.",
                        show_label=True
                    )
                    usability_question2 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I found the system unnecessarily complex.",
                        show_label=True,
                    )
                    usability_question3 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I thought the system was easy to use.",
                        show_label=True
                    )
                    usability_question4 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I think that I would need the support of a technical person to be able to use this system.",
                        show_label=True
                    )
                    usability_question5 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I found the various functions in this system were well integrated.",
                        show_label=True
                    )
                    usability_question6 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I thought there was too much inconsistency in this system.",
                        show_label=True
                    )
                    usability_question7 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I would imagine that most people would learn to use this system very quickly.",
                        show_label=True
                    )
                    usability_question8 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I found the system very cumbersome to use.",
                        show_label=True
                    )
                    usability_question9 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I felt very confident using the system.",
                        show_label=True
                    )
                    usability_question10 = gr.Radio(
                        choices=self.scales["likert"],
                        label="I needed to learn a lot of things before I could get going with this system.",
                        show_label=True
                    )
                    usability_button = gr.Button("Submit")
            
            irb_button.click(
                self.__save_irb_agreement,
                inputs=[informed_consent, irb_button],
                outputs=[informed_consent, irb_button],
                queue=False,
            )
            
            text_input.submit(
                self.__add_text,
                inputs=[chatbot, text_input],
                outputs=[chatbot, text_input],
                queue=False,
            ).then(
                lambda: gr.update(interactive=False),
                inputs=None,
                outputs=[audio_record],
                queue=False
            ).then(
                self.__process,
                inputs=chatbot,
                outputs=chatbot,
                queue=True
            ).then(
                lambda: (gr.update(interactive=True), ) * 2,
                inputs=None,
                outputs=[text_input, audio_record],
                queue=False
            ).then(
                self.__activate_benchmark,
                outputs=[question1, question2, question3, question4, question5, question6,
                         pairwise_question1, pairwise_question2, pairwise_question3, pairwise_question4],
                queue=True,
            ).then(
                lambda: (gr.update(visible=True), ) * 3,
                outputs=[text_input_button, reset_button, finish_button],
                queue=False
            )
            
            text_input_button.click(
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
                lambda: (gr.update(visible=False), ) * 2,
                outputs=[reset_button, text_input_button],
                queue=False,
            )

            save_id_button.click(
                self.__save_id,
                inputs=[id_input, save_id_button,
                        situation_title, situation_description, chatbot, audio_record, text_input, text_input_message],
                outputs=[id_input, save_id_button,
                         situation_title, situation_description, chatbot, audio_record, text_input, text_input_message],
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
                lambda: (gr.update(visible=True), ) *2,
                outputs=[reset_button, finish_button],
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
                queue=True
            ).then(
                lambda: (gr.update(visible=False),) * 3,
                outputs=[reset_button, finish_button, text_input_button],
                queue=False
            )
            
            finish_button.click(
                self.__finish_conversation,
                inputs=situation_title,
                outputs=[situation_title, situation_description, chatbot, audio_record, text_input, finish_button, text_input_message],
                queue=True,
            ).then(
                self.__activate_assistant,
                inputs=[last_question, submit_button],
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
        self.data["mturk_worker_id"] = id_input
        return (gr.update(interactive=False), ) * 2 + (gr.update(visible=True), ) * len(args)
    
    def __activate_benchmark(self):
        return (gr.update(value=None, visible=True), ) * 10
    
    def __save_benchmark(self, id_input, chatbot, *args):
        all_questions = list(args)
        if None in all_questions:
            return tuple(all_questions)
        
        # if self.random_num == 0 1=normal, 2=augmented
        # else 1=augmented, 2=normal
        if self.random_num == 0:
            for i in range(-1, -5, -1):
                all_questions[i] = "normal" if all_questions[i] == 1 else "augmented"
        else:
            for i in range(-1, -5, -1):
                all_questions[i] = "augmented" if all_questions[i] == 1 else "normal"

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
        content["situation_index"] = self.situation_idx
        self.logger.info(f"Benchmark: {str(content)}")
        
        del content["mturk_worker_id"]
        del content["situation_index"]
        self.data["result"][f"situation{self.situation_idx + 1}"].append(content)

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
        content["situation_index"] = self.situation_idx
        content['message'] = "The conversation history has been reset."
        self.logger.info(f"Benchmark: {str(content)}")
        self.data["result"][f"situation{self.situation_idx + 1}"].clear()

        from conversation.prompter import Prompter
        from models.chatgpt.core import ChatGPT
            
        chatgpt = ChatGPT()
        if type(self.model.generate_1) is type(chatgpt.prompt):
            self.model.generate_2 = Prompter(chatgpt).prompt
        else:
            from models.palm.core import PaLM
            palm = PaLM()
            if type(self.model.generate_1) is type(palm.prompt):
                self.model.generate_2 = Prompter(palm).prompt
        
        return (gr.update(value=None, visible=False), ) * 10
    
    def __activate_assistant(self, *args):
        if self.situation_idx > 2:
            return (gr.update(visible=True), ) * len(args)
        else:
            return args
    
    def __finish_conversation(self, situation_title):
        self.situation_idx += 1
        if self.situation_idx > 2:
            return (gr.update(visible=False), ) * 2 \
                + (gr.update(value=None, visible=False), ) + (gr.update(visible=False),) * 4
        else:            
            from conversation.prompter import Prompter
            from models.chatgpt.core import ChatGPT
            
            chatgpt = ChatGPT()
            if type(self.model.generate_1) is type(chatgpt.prompt):
                self.model.generate_1 = chatgpt.prompt
                self.model.generate_2 = Prompter(chatgpt).prompt
            else:
                from models.palm.core import PaLM
                palm = PaLM()
                if type(self.model.generate_1) is type(palm.prompt):
                    self.model.generate_1 = palm.prompt
                    self.model.generate_2 = Prompter(palm).prompt
            
            situation_msg = f'''
                            1. {self.situations[self.situation_idx][0]}
                            2. {self.situations[self.situation_idx][1]}
                            3. {self.situations[self.situation_idx][2]}
                            '''
            return (situation_title, gr.update(value=situation_msg), ) + (gr.update(value=None), ) * 3 + (gr.update(visible=False), gr.update(visible=True))
    
    def __submit(self, id_input, *args):
        # 에외처리 필요
        content = dict()
        content["mturk_worker_id"] = id_input
        if len(args) == 1:
            content["last_answer"] = args[0]
            self.data["result"]["last_answer"] = args[0]
        else:
            content["usability_answer"] = list(args)
            self.data["result"]["usability_answer"] = list(args)
        self.logger.info(f"Benchmark: {str(content)}")
        
        os.makedirs(f"{self.data_path}", exist_ok=True)
        with open(f"{self.data_path}/user_{id_input}_data.json", "w", encoding="utf-8") as file:
            json.dump(self.data, file)
        
        if len(args) == 1:
            return (gr.update(visible=False), ) * 3 + (gr.update(visible=True), ) * 2
        else:
            return gr.update(visible=False), \
                    gr.update(value="### Thank you :)"), \
                    gr.update(visible=True)
    
    def __load_scenario(self, prefix: str) -> list[str]:
        index = 1
        scenarios = []

        while True:
            filepath = osp.join("conversation", "scenarios", f"{prefix}{index}.txt")
            if osp.exists(filepath):
                with open(filepath, "r") as file:
                    scenario = [line.strip() for line in file.readlines()]
                    scenarios.append(scenario)
                index += 1
            else:
                break
        
        return scenarios
    
    def __load_guidance(self, name: str) -> str:
        with open(osp.join("conversation", "guidances", f"{name}.txt"), "r", encoding="utf-8") as file:
            return file.read()
    
    def __load_experiment_description(self, name: str, situations: list[str]) -> str:
        with open(osp.join("conversation", "guidances", f"{name}.txt"), "r", encoding="utf-8") as file:
            description = file.read().format(
                situations[0][0], situations[0][1], situations[0][2],
                situations[1][0], situations[1][1], situations[1][2],
                situations[2][0], situations[2][1], situations[2][2],
            )
            return description
