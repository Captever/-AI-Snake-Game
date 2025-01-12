from typing import Dict, List

from scripts.ai.rule_based_ai import RuleBasedAI
from scripts.ai.greedy_ai import GreedyAI

class AIManager:
    def __init__(self):
        self.ai_list: Dict[str, any] = {}

        self.ai_list["Rule-based"] = RuleBasedAI
        self.ai_list["Greedy-algorithm"] = GreedyAI
    
    def get_ai_list(self) -> List[str]:
        return self.ai_list.keys()

    def get_ai(self, ai_name: str):
        return self.ai_list[ai_name]()