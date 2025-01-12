# screen
# SCREEN_WIDTH = 360
# SCREEN_HEIGHT = 640
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
IS_LANDSCAPE = bool(SCREEN_WIDTH > SCREEN_HEIGHT)

# ui color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GARY = (70, 70, 70)

# ui size
FONT_SIZE_RATIO = 0.075
UI_LAYOUT = {
    "default_color": (128, 128, 128, 150),
}

UI_BUTTON = {
    "default_color": WHITE,
    "hover_color": LIGHT_GRAY,
    "disable_color": GRAY,
    "font_ratio": 0.6,
}
UI_SCROLLBAR = {
    "bar_default_color": GRAY,
    "bar_hover_color": DARK_GARY,
    "handle_default_color": WHITE,
    "handle_hover_color": LIGHT_GRAY,
    "bar_ratio": 0.2,
    "font_ratio": 0.5,
}

# object
OBJECT_DICT = {
    'none': 0,
    'wall': 1,
    'body': 2,
    'feed': 3, 
}
OBJECT_OUTLINE_RATIO = 0.2

# object color
BODY_OUTLINE_COLOR = (59, 92, 70)
BODY_COLOR = (7, 255, 82)
FEED_OUTLINE_COLOR = (187, 113, 40)
FEED_COLOR = (255, 255, 15)
DIR_COLOR = (255, 255, 255)

# direction
DIR_ARROW_RATIO = 0.5
DIR_OFFSET_DICT = {
    'E': (1, 0),
    'W': (-1, 0),
    'S': (0, 1),
    'N': (0, -1)
}
DIR_ANGLE_DICT = {
# pygame.transform.rotate operates counterclockwise
    'E': 0,
    'W': 180,
    'S': 270,
    'N': 90
}

# etc
GRID_NUM = (20, 20)
GRID_ALPHA = 128
GRID_THICKNESS = 1 # grid line thickness of map
FEED_NUM = 3
MOVE_DELAY = 5 # frame
INIT_LENGTH = 3 # initial length of snake
MAP_OUTERLINE_THICKNESS = 1
GRID_OUTERLINE_THICKNESS = 3