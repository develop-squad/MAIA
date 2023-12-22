from parlai.core.agents import Agent, register_agent
from models.chatgpt.core import ChatGPT
from conversation.prompter import AugmentedPrompter, BasePrompter

@register_agent("maia")
class MaiaAgent(Agent):
    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        
        # 모델 구조 및 파라미터 초기화
        self.prompter = BasePrompter(ChatGPT)
        self.prompter.reset()

    def observe(self, observation):
        # 메시지 처리 로직
        self.observation = observation.get('text', '')
        return observation

    def act(self):
        # 응답 생성 로직
        if self.observation:
            response_text = self.prompter.prompt(self.observation)
        else:
            response_text = "Error: No observation data."
        
        response = {"text": response_text}
        return response
