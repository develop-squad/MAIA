import json
import os.path as osp
from dataclasses import dataclass
from utils.model import Model
from conversation.retriever import BiEncoderRetriever

@dataclass
class PromptConfig:
    remove_cot: bool = False

class Prompter:
    def __init__(self, model: Model) -> None:
        self.model = model

        self.config = PromptConfig()
        self.templates = self._load_templates("templates.json")
        self.examples = self._load_templates("examples.json")
        self.responses = {
            "clarifier": None,
            "retrieval": None,
            "summerizer": None,
        }
        self.session = {
            "history": [],
            "history_summaries": ["They are starting conversation."],
            "prefix": None,
            "suffix": None,
        }

        self.retriever = BiEncoderRetriever()
    
    def prompt(self, input:str) -> str:
        #question = self.clarify(input, 1)
        knowledge, question = self.extract(input, 1)
        retrieval = self.retrieve(question)
        return ""
    
    def clarify(
        self,
        input: str,
        num_examples: int = None,
    ) -> str:
        if num_examples is None:
            num_examples = len(self.examples["clarifier"])
        input = self.templates["clarifier"].format(
            examples="\n".join(self.examples["clarifier"][:num_examples]),
            input=input,
        )
        print("\n  ** Clarifier Input **")
        print(input)

        clarified_question = "".join(self.model.fn(
            input,
            temperature=0.3,
            stop=[],
        ))
        print("\n ** Clarifier Output **")
        print(clarified_question)
        return clarified_question
    
        print("\n** Clarifier **")
        print(prompt)

        result = "".join(self.model.fn(
            prompt,
            temperature=0.3,
        ))
        return result
    
    def retrieve(self, question: str) -> str:
        retrieved_summaries = self.retriever.retrieve_top_summaries(
            question, self.session["history_summaries"]
        )

        if not self.config.remove_cot:
            numbered_summaries = [f"{i+1} " + summary for i, summary in enumerate(retrieved_summaries)]
            summaries = "\n".join(numbered_summaries)
        else:
            summaries = "\n".join(retrieved_summaries)

        # Few-shot retrieval
        input = self.templates["memory_processor"].format(
            summaries=summaries,
            question=question,
        )
        print("\n  ** Retrieval Input **")
        print(input)

        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
        ))
        print("\n  ** Retrieval Output **")
        print(completion)
        return completion

    def _load_templates(self, filename: str) -> dict:
        try:
            with open(osp.join("conversation", "configs", filename), "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Error: 'conversation/configs/{filename}' file not found!")
        except json.JSONDecodeError:
            raise Exception(f"Error: JSON decoding failed for 'conversation/configs/{filename}'!")
