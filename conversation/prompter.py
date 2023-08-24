import json
import os.path as osp
from utils.model import Model
from conversation.retriever import BiEncoderRetriever

class Prompter:
    def __init__(self, model: Model) -> None:
        self.model = model

        self.templates = self._load_templates("prompts.json")
        self.examples = self._load_templates("examples.json")
        self.responses = {
            "clarifier": None,
            "retrieval": None,
            "summerizer": None,
        }
        self.session = {
            "history": [],
            "history_summary": None,
            "prefix": None,
            "suffix": None,
        }

        self.retriever = BiEncoderRetriever()
    
    def prompt(self, input:str) -> str:
        return ""
    
    def clarify(
        self,
        input: str,
        num_examples: int = None,
    ) -> str:
        if num_examples is None:
            num_examples = len(self.examples["clarifier"])
        prompt = self.templates["clarifier"].format(
            examples="\n".join(self.examples["clarifier"][:num_examples]),
            input=input,
        )
        print("\n** Clarifier **")
        print(prompt)

        result = "".join(self.model.fn(
            prompt,
            temperature=0.3,
        ))
        return result
    
    def retrieve(self, input: str) -> str:
        retrieved_summaries = self.retriever.retrieve_top_summaries(
            input, self.session['history_summary']
        )
        summaries = "\n" + "\n".join(retrieved_summaries)
        return summaries

    def _load_templates(self, filename: str) -> dict:
        try:
            with open(osp.join("conversation", "configs", filename), "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Error: 'conversation/configs/{filename}' file not found!")
        except json.JSONDecodeError:
            raise Exception(f"Error: JSON decoding failed for 'conversation/configs/{filename}'!")
