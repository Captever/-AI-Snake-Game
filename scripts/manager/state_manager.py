from enum import Enum

class GameState(Enum):
    ACTIVE = 100
    COUNTDOWN = 101
    PAUSED = 102
    SURRENDER = 103
    GAMEOVER = 110
    CLEAR = 109

class ReplayState(Enum):
    PLAY = 1
    PAUSE = 2
    REWIND = 3
    FAST_FORWARD = 4