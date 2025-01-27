from enum import Enum

class GameState(Enum):
    ACTIVE = 100
    COUNTDOWN = 101
    PAUSED = 102
    SURRENDER = 103
    GAMEOVER = 110
    CLEAR = 109