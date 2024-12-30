# game.py
main file

## class Game
- .screen -> Surface: overall screen
- .origin -> Tuple(int, int): origin vertex of game map
- About map
  - .map -> Map: map object
  - .bodies -> List: position values of the player's body
  - .feed -> Dictionary{Tuple(int, int): str}
    - Tuple(int, int): position value of the feed
    - str: type of the feed