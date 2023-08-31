from utils.model import Model
from conversation.prompter import Prompter

class Conversation(Model):
    def __init__(self, model: Model) -> None:
        self.model = model
        self.prompter = Prompter(model)
    
    def prompt(
        self,
        input: str,
    ) -> str:
        self.prompter.prompt