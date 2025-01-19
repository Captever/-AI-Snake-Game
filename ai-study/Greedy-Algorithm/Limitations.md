# Limitations
- Situations where the AI traps itself in a closed space formed by its own body still occur.
- Even when survival is possible after entering a trapped space, the AI fails to handle the situation skillfully, leading to game over.

---

# Solutions

## Simulating Predicted Paths
- Evaluate the long-term impact of the current move by calculating expected paths and assessing the remaining space a few turns ahead.

## `A* Algorithm` to Tail
- When entering a trapped space is unavoidable, use the `A* Algorithm` to explore exits by ensuring there is a path to the tail.

## Defensive Movement in Mid-to-Late Game
- Adopt defensive movements when the player's body starts to occupy most of the map, minimizing future risks while progressing.

---

# Evaluation of Solutions

## Simulating Predicted Paths
- If multiple feeds exist, the target feed may change with every move, making it difficult to fix a path.
- Designating one target feed based on a specific mechanism could fix the path, but this would require global settings.
- The process of fixing a path may lead to high computational overhead.

## `A* Algorithm` to Tail
- Methodologically sound, but requires global settings to remember and follow paths. Additionally, the `A* Algorithm` demands greedy exploration, which increases computational load as the search radius expands. To avoid disrupting gameplay, asynchronous calculation and re-routing would be necessary, potentially prolonging implementation time.

## Defensive Movement in Mid-to-Late Game
- Requires a clear definition of 'defensive movement'.
- Likely to involve a combination with **Rule-based** methods. For instance, the AI could circle the map once, target the next feed, and return to the tail repeatedly.
- May slow down game progress.
- Current movement states would need to be globally defined for each target. For example, when moving to the tail, the state must be set to 'to-tail'.

---

# Conclusion

Adopting defensive movements in the mid-to-late game combined with **Rule-based** methods could improve scores. However, the plan will be revisited after transitioning to **RL (Reinforcement Learning)** by implementing **Q-Learning** first and conducting a thorough comparison.