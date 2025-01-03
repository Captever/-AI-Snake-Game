import math

# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# object
OBJECT_DICT = {
    'none': 0,
    'wall': 1,
    'body': 2,
    'feed': 3, 
}

# color
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
BLACK = (0, 0, 0)

BODY_OUTLINE_COLOR = (59, 92, 70)
BODY_COLOR = (7, 255, 82)
FEED_OUTLINE_COLOR = (187, 113, 40)
FEED_COLOR = (255, 255, 15)
DIR_COLOR = (255, 255, 255)

# direction
DIR_ARROW_HEIGHT = 10
DIR_ARROW_VERTEX_DICT = {
    'E': ((-DIR_ARROW_HEIGHT, DIR_ARROW_HEIGHT / math.sqrt(3)), (-DIR_ARROW_HEIGHT, -DIR_ARROW_HEIGHT / math.sqrt(3))),
    'W': ((DIR_ARROW_HEIGHT, DIR_ARROW_HEIGHT / math.sqrt(3)), (DIR_ARROW_HEIGHT, -DIR_ARROW_HEIGHT / math.sqrt(3))),
    'S': ((DIR_ARROW_HEIGHT / math.sqrt(3), -DIR_ARROW_HEIGHT), (-DIR_ARROW_HEIGHT / math.sqrt(3), -DIR_ARROW_HEIGHT)),
    'N': ((DIR_ARROW_HEIGHT / math.sqrt(3), DIR_ARROW_HEIGHT), (-DIR_ARROW_HEIGHT / math.sqrt(3), DIR_ARROW_HEIGHT)),
}
DIR_OFFSET_DICT = {
    'E': (1, 0),
    'W': (-1, 0),
    'S': (0, 1),
    'N': (0, -1),
}

# etc
GRID_NUM = (20, 20)
GRID_ALPHA = 128
GRID_THICKNESS = 1 # grid line thickness of map
FEED_NUM = 3
MOVE_DELAY = 30 # frame
INIT_LENGTH = 3 # initial length of snake
OUTERLINE_THICKNESS = 3 # outline thickness of map