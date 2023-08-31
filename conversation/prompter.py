import os
import os.path as osp
import json
import typing
from dataclasses import dataclass
from utils.model import Model
from conversation.retriever import BiEncoderRetriever

@dataclass
class PromptConfig:
    remove_cot: bool = False

class Prompter(Model):
    def __init__(
        self,
        model: Model,
    ) -> None:
        super().__init__()

        self.model = model

        self.config = PromptConfig()
        self.templates = self._load_prompts("conversation/prompts/")
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
        self.fn = self.prompt
    
    def prompt(
        self,
        input:str,
    ) -> str:
        # Conversation Layer
        print("\n ** Extractor **")
        knowledge, query = self.extract(input)
        print("* Knowledge, Question:", (knowledge, query))

        print("\n ** Retriever **")
        retrieval = self.retrieve(query)
        print("* Retrieval:", retrieval)

        print("\n ** Reasoning **")
        conclusion = self.reasoning(knowledge + retrieval, query)
        print("* Conclusion:", conclusion)

        print("\n ** Generator **")
        response = self.generate(conclusion, query)
        print("* Generation:", response)

        # Memorization Layer
        ## TODO: Conversation 결과를 제공한 후 Memorize하여 응답 시간 단축
        # summaries = self.summarize(question, knowledge, retrieval, response)
        # print(" ** Summarization **\n", summaries)

        # memories = self.memorize(knowledge, retrieval, summaries)
        # print(" ** Memorization **\n", memories)

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
        ))
        return clarified_question

    def extract(
        self,
        input: str,
    ) -> tuple[list[str], str]:
        prompt = self.templates["extractor"].format(
            input=input,
        )
        completion = "".join(self.model.fn(
            input=prompt,
            temperature=0,
        ))
        print("* Completion:", completion)

        knowledge = self._parse_completion(completion, "Knowledge")
        query = self._parse_completion(completion, "Query")
    
        return knowledge, query
    
    def retrieve(
        self,
        query: str,
    ) -> list[str]:
        if len(self.session["history_summaries"]) == 0:
            return []

        retrieval = self.retriever.retrieve_top_summaries(
            query, self.session["history_summaries"],
        )

        return retrieval
    
    def reasoning(
        self,
        knowledge: list[str],
        query: str,
    ) -> str:
        prompt = self.templates["reasoner"].format(
            knowledge=knowledge,
            query=query,
        )
        print("* Prompt:", prompt)
        completion = "".join(self.model.fn(
            input=prompt,
            temperature=0,
        ))
        print("* Completion:", completion)

        conclusion = self._parse_completion(completion, "Conclusion")

        if len(conclusion) == 0:
            conclusion = ""
            print("** No conclusions were reached. **")
            print(completion)
            return completion
        
        return conclusion

    def generate(
        self,
        information: str,
        query: str,
    ) -> str:
        prompt = self.templates["generator"].format(
            query=query,
            information=information,
        )
        print("* Prompt:", prompt)
        completion = "".join(self.model.fn(
            input=prompt,
            temperature=0.7,
        ))
        print("* Completion:", completion)
        
        return completion
    
    def summarize(
        self,
        question: str,
        knowledge: list[str],
        retrieval: list[str],
        answer: str,
        num_examples: int = None,
    ) -> list[str]:
        if num_examples is None:
            num_examples = len(self.examples["summarizer"])
        input = self.templates["summarizer"].format(
            examples="\n".join(self.examples["summarizer"][:num_examples]),
            question=question,
            knowledge=self._combine_knowledge(knowledge, retrieval),
            answer=answer,
        )

        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
        ))

        summaries = completion.split("\n")
        summaries = [summary.strip("- ") for summary in summaries if summary.strip()]
        return summaries
    
    def memorize(
        self,
        knowledge: list[str],
        retrieval: list[str],
        summaries: list[str],
        num_examples: int = None,
    ) -> list[str]:
        knowledge_text = self._combine_knowledge(retrieval)
        summaries_text = self._combine_knowledge(summaries, knowledge)

        if num_examples is None:
            num_examples = len(self.examples["deduplication"])
        input = self.templates["deduplication"].format(
            examples="\n".join(self.examples["deduplication"][:num_examples]),
            knowledge=knowledge_text,
            summaries=summaries_text,
        )
        
        completion = "".join(self.model.fn(
            input,
            temperature=0.3,
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
        
    def _load_prompts(
        self,
        directory: str,
    ) -> dict[str, str]:
        prompts = {}
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                name_without_extension = os.path.splitext(filename)[0]
                prompts[name_without_extension] = content    
        return prompts
    
    def _parse_completion(
        self,
        completion: str,
        title: str
    ) -> typing.Union[list[str], str]:
        start_tags = [f"#{title}\n", f"#{title}: ", f"{title}: ", f"{title}\n"]
        end_tag = "#"
        
        start_tag = next((tag for tag in start_tags if tag in completion), None)
        
        if start_tag:
            content = completion.split(start_tag)[1].split(end_tag)[0].strip()
            
            # Determine if the content starts with '- ' (to decide if returning a list)
            if content.startswith("- "):
                return [item.strip().replace("- ", "").replace("* ", "") for item in content.split("\n") if item.strip()]
            else:
                return content
        else:
            return []

    def _combine_knowledge(
        self, 
        *args,
    ) -> str:
        combined = [f"({idx + 1}) {item}" for idx, item in enumerate(item for arg in args for item in arg)]
        return " ".join(combined)
