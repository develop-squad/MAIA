import json
import os.path as osp
from utils.model import Model

class Prompter:
    def __init__(self, model: Model):
        self.model = model

        self.prompts = self._load_prompts("prompts.json")
        self.examples = self._load_prompts("examples.json")
        self.responses = {
            "clarifier": None,
            "retrieval": None,
            "summerizer": None,
        }
    
    def clarify(
        self,
        input: str,
        num_examples: int = None,
    ) -> str:
        if num_examples is None:
            num_examples = len(self.examples["clarifier"])
        prompt = self.prompts["clarifier"].format(
            examples="\n".join(self.examples["clarifier"][:num_examples]),
            input=input,
        )
        print("\n** Clarifier **")
        print(prompt)
        return "".join(self.model.fn(prompt))

    def _load_prompts(self, filename: str) -> dict:
        try:
            with open(osp.join("conversation", "configs", filename), "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Error: 'conversation/configs/{filename}' file not found!")
        except json.JSONDecodeError:
            raise Exception(f"Error: JSON decoding failed for 'conversation/configs/{filename}'!")
