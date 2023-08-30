import json
import os.path as osp
from dataclasses import dataclass
from utils.model import Model
from conversation.retriever import BiEncoderRetriever

@dataclass
class PromptConfig:
    remove_cot: bool = False

class Prompter:
    def __init__(
        self,
        model: Model,
    ) -> None:
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
            "history_summaries": [],
            "prefix": None,
            "suffix": None,
        }

        self.retriever = BiEncoderRetriever()
    
    def prompt(
        self,
        input:str,
    ) -> str:
        # Conversation
        knowledge, question = self.extract(input, 1)
        print(" ** Knowledge **\n", knowledge)
        print(" ** Question **\n", question)
        retrieval = self.retrieve(question)
        print(" ** Retrieval **\n", retrieval)
        reasoning = self.reasoning(question, knowledge, retrieval)
        print(" ** Reasoning **\n", reasoning)
        response = self.generate(question, reasoning)
        print(" ** Generation **\n", response)

        # Memorization
        ## TODO: Conversation 결과를 제공한 후 Memorize하여 응답 시간 단축
        summaries = self.summarize(question, knowledge, retrieval, response)
        print(" ** Summarization **\n", summaries)
        memories = self.memorize(knowledge, retrieval, summaries)
        print(" ** Memorization **\n", memories)

        return response
    
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

        clarified_question = "".join(self.model.fn(
            input,
            temperature=0.3,
            stop=[],
        ))
        return clarified_question
    
    def extract(
        self,
        input: str,
        num_examples: int = None,
    ) -> tuple[list[str], str]:
        if num_examples is None:
            num_examples = len(self.examples["extractor"])
        input = self.templates["extractor"].format(
            examples="\n".join(self.examples["extractor"][:num_examples]),
            input=input,
        )

        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
            stop=[],
        ))

        knowledge = []
        question = ""
        sections = [section.strip() for section in completion.split("##") if section.strip()]
        for section in sections:
            if section.startswith("Knowledge"):
                knowledge = [line.strip("- ").strip() for line in section.replace("Knowledge", "").strip().split("\n") if line.strip()]
                # knowledge = section.replace("Knowledge", "").strip()
            elif section.startswith("Question"):
                question = section.replace("Question", "").strip()

        return knowledge, question
    
    def retrieve(
        self,
        question: str,
    ) -> list[str]:
        if len(self.session["history_summaries"]) == 0:
            return ""

        retrieved_summaries = self.retriever.retrieve_top_summaries(
            question, self.session["history_summaries"]
        )
        return retrieved_summaries

        # if not self.config.remove_cot:
        #     numbered_summaries = [f"{i+1}. " + summary for i, summary in enumerate(retrieved_summaries)]
        #     summaries = "\n".join(numbered_summaries)
        # else:
        #     summaries = "\n".join(retrieved_summaries)
        # return summaries

    def reasoning(
        self,
        question: str,
        knowledge: list[str],
        retrieval: list[str],
        num_examples: int = None,
    ) -> str:
        if num_examples is None:
            num_examples = len(self.examples["extractor"])
        input = self.templates["reasoner"].format(
            examples="\n".join(self.examples["reasoner"][:num_examples]),
            knowledge=self._combine_knowledge(knowledge, retrieval),
            question=question,
        )

        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
            stop=[],
        ))
        return completion
    
    def generate(
        self,
        question: str,
        reasoning: str,
    ) -> str:
        input = self.templates["generator"].format(
            question=question,
            reasoning=reasoning,
        )

        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
        ))
        return completion
    
    def summarize(
        self,
        question: str,
        knowledge: list[str],
        retrieval: list[str],
        answer: str,
    ) -> list[str]:
        input = self.templates["summarizer"].format(
            question=question,
            knowledge=self._combine_knowledge(knowledge, retrieval),
            answer=answer,
        )

        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
            stop=[],
        ))

        summaries = completion.split("\n")
        summaries = [summary.strip("- ") for summary in summaries if summary.strip()]
        return summaries
    
    def memorize(
        self,
        knowledge: list[str],
        retrieval: list[str],
        summaries: list[str],
    ) -> list[str]:
        knowledge_text = self._combine_knowledge(retrieval)
        summaries_text = self._combine_knowledge(summaries, knowledge)

        input = self.templates["deduplication"].format(
            knowledge=knowledge_text,
            summaries=summaries_text,
        )
        
        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
            stop=[],
        ))

        memories = completion.split("\n")
        memories = [memory.strip("- ") for memory in memories if memory.strip()]
        self.session["history_summaries"].extend(memories)
        return memories

    def _load_templates(
        self,
        filename: str,
    ) -> dict:
        try:
            with open(osp.join("conversation", "configs", filename), "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"Error: 'conversation/configs/{filename}' file not found!")
        except json.JSONDecodeError:
            raise Exception(f"Error: JSON decoding failed for 'conversation/configs/{filename}'!")

    def _combine_knowledge(
        self, 
        *args,
    ) -> str:
        combined = [f"- {item}" for arg in args for item in arg]
        return "\n".join(combined)
