import os
import os.path as osp
import time
import json
import typing
from dataclasses import dataclass
from utils.model import Model
from models.palm.core import PaLM
from conversation.retriever import BiEncoderRetriever

@dataclass
class PromptConfig:
    remove_cot: bool = False

class BasePrompter(Model):
    def __init__(
        self,
        model_class: typing.Type[Model],
    ) -> None:
        super().__init__()

        self.model_class = model_class
        self.model_loaded = False
        self.fn = self.prompt
    
    def reset(self) -> None:
        self.__instantiate_model()
    
    def __instantiate_model(self) -> Model:
        self.model = self.model_class(context=True)
        self.model_loaded = True
        return self.model
    
    def prompt(
        self,
        input: str,
    ) -> str:
        completion = "".join(self.model.fn(
            input=input,
            temperature=0.7,
            stop=["\n"],
        ))
        return completion

class AugmentedPrompter(Model):
    def __init__(
        self,
        model_class: typing.Type[Model],
    ) -> None:
        super().__init__()

        self.model_class = model_class
        self.model_loaded = False
        self.fn = self.prompt
    
    def reset(self) -> None:
        self.__instantiate_model()
        self.config = PromptConfig()
        self.templates = self._load_prompts("conversation/prompts/")
        self.session = {
            "history": [],
            "history_summaries": [],
            "prefix": None,
            "suffix": None,
        }
        self.retriever = BiEncoderRetriever()
    
    def __instantiate_model(self) -> Model:
        self.model = self.model_class(context=False)
        self.role_key = "role"

        if isinstance(self.model, PaLM):
            self.model = self.model_class(
                model="models/text-bison-001",
                context=False,
            )
            self.role_key = "author"

        self.model_loaded = True
        return self.model
    
    def prompt(
        self,
        input: str,
    ) -> str:
        attempts = 0
        while attempts < 3:
            try:
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

                extended_history = [
                    {self.role_key: "user", "content": input},
                    {self.role_key: "assistant", "content": response},
                ]
                self.session["history"].extend(extended_history)

                # Memorization Layer
                ## TODO: Conversation 결과를 제공한 후 Memorize하여 응답 시간 단축
                summaries = self.summarize(self.session["history"])
                print(" ** Summarization **\n", summaries)

                self.session["history_summaries"].extend(summaries)

                return response
            except Exception as e:
                print(f"Attempt {attempts+1} failed with error: {e}")
                if attempts < 3:
                    time.sleep(1)
                attempts += 1
        return "Sorry, there was an error processing your request. Please try again, and if the error persists, reset the conversation and start over."

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
        query = self._parse_completion(completion, "Query")[0]
    
        return knowledge, query
    
    def retrieve(
        self,
        query: str,
    ) -> list[str]:
        prompt = self.templates["retriever"].format(
            question=query,
        )
        print("* Prompt:", prompt)
        completion = "".join(self.model.fn(
            input=prompt,
            temperature=0,
            history=self.session["history"],
        ))
        print("* History:", self.session["history"])
        print("* Completion:", completion)

        hsitory_content = [f"{x[self.role_key]}: {x['content']}" for x in self.session["history"]]

        if len(self.session["history_summaries"]) == 0:
            if "i can't answer" in completion.strip().lower() or "i cannot answer" in completion.strip().lower():
                return hsitory_content
            return [completion]

        retrieval = self.retriever.retrieve_top_summaries(
            query, self.session["history_summaries"],
        )

        if "i can't answer" in completion.strip().lower() or "i cannot answer" in completion.strip().lower():
            if retrieval:
                return retrieval
            return self.session["history_summaries"]
        return [completion] + retrieval
    
    def reasoning(
        self,
        knowledge: list[str],
        query: str,
    ) -> str:
        prompt = self.templates["reasoner"].format(
            knowledge="\n".join(f"({i+1}) {item}" for i, item in enumerate(knowledge)),
            query=query,
        )
        print("* Prompt:", prompt)
        completion = "".join(self.model.fn(
            input=prompt,
            temperature=0,
        ))
        print("* Completion:", completion)

        #conclusion = self._parse_completion(completion, "Conclusion")[0]
        conclusion = completion

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
        history: list[dict[str, str]],
    ) -> list[str]:
        dialogue = "\n".join(f"{item[self.role_key]}: {item['content']}" for item in history)

        prompt = self.templates["summarizer"].format(
            dialogue=dialogue,
        )
        print("* Prompt:", prompt)
        completion = "".join(self.model.fn(
            input=prompt,
            temperature=0,
        ))
        print("* Completion:", completion)

        summary = self._parse_completion(completion, "Summary")
        
        return summary

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
        start_tags = [f"#{title}\n", f"#{title}:", f"{title}:", f"{title}\n"]
        end_tag = "#"
        
        start_tag = next((tag for tag in start_tags if tag in completion), None)
        
        if start_tag:
            content = completion.split(start_tag)[1].split(end_tag)[0].strip()
            
            # Determine if the content starts with '- ' (to decide if returning a list)
            if content.startswith("- "):
                return [item.strip().replace("- ", "").replace("* ", "") for item in content.split("\n") if item.strip()]
            else:
                return [content]
        else:
            return []

    def _combine_knowledge(
        self, 
        *args,
    ) -> str:
        combined = [f"({idx + 1}) {item}" for idx, item in enumerate(item for arg in args for item in arg)]
        return " ".join(combined)
