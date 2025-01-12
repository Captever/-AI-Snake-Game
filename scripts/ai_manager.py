from typing import Dict, List

from instances.ai_instance import AI

class AIManager:
    def __init__(self):
        self.ai_list: List[str] = []

        self.ai_list.append("Rule-based")
        self.ai_list.append("Greedy-algorithm")
    
    def get_ai_list_with_auto_lined(self) -> List[str]:
        auto_lined_target: Dict[str, str] = {
            '-': ' ',
            ' ': '\n',
        }

        ret = []

        for ai_name in self.ai_list.copy():
            for t_from, t_to in auto_lined_target.items():
                if t_from in ai_name:
                    ai_name = ai_name.replace(t_from, t_to)
            
            ret.append(ai_name)

        return ret

    def get_ai(self, ai_name: str) -> AI:
        return AI(ai_name)