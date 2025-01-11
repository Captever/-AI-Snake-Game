from typing import List

from instances.ai_instance import AI

class AIManager:
    def __init__(self):
        self.ai_list = []

        self.ai_list.append("Rule-based")
        self.ai_list.append("Greedy-algorithm")
    
    def get_ai_list(self) -> List[str]:
        return self.ai_list

    def get_ai(self, ai_name: str) -> AI:
        return AI(ai_name)