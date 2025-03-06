from typing import Dict, List

from scripts.ai.rule_based_ai import RuleBasedAI
from scripts.ai.greedy_ai import GreedyAI
from scripts.ai.q_learning import QLearningAI
from scripts.ai.dqn import DQNAI

class AIManager:
    def __init__(self):
        self.ai_list: Dict[str, any] = {}

        self.ai_list["Rule-based-Smaller"] = RuleBasedAI("priority-smaller")
        self.ai_list["Rule-based-Larger"] = RuleBasedAI("priority-larger")
        self.ai_list["Rule-based-Maximalism"] = RuleBasedAI("maximalism")
        self.ai_list["Greedy-Algorithm"] = GreedyAI()
        self.ai_list["Q-Learning"] = QLearningAI()
        self.ai_list["DQN"] = DQNAI()
        # self.ai_list["Policy-Gradient"] = PolicyGradient()
        # self.ai_list["PPO"] = PPO()
    
    def get_ai_list(self) -> List[str]:
        return self.ai_list.keys()

    def get_ai(self, ai_name: str):
        return self.ai_list[ai_name]