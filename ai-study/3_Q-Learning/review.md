# 10,000 Epoch Evaluation: total average: 1.7

Executed 10,000 epochs, but the overall average remained around 1.7. The fluctuation within this range suggests that increasing the epochs further may not yield significant improvements.

## Improvement Directions
- Instead of absolute cell count to the target, apply relative distance values within the -1 to 1 range in the state.
- Gradually decrease epsilon from 0.9 to 0.01.
- Significantly reduce the penalty for movement without state changes: -0.1 → -0.001.

---

# 2,000 Epoch Evaluation

After modifying the code and running the 'Relative Value Applied 2,000 Epoch' test, the recorded video showed many looping sections.

## Improvement Directions
- Add feedback based on distance:
  - Distance increase: -0.1
  - Distance decrease: +0.1
- Allow unlimited deaths and incorporate four-directional collision values into the state.
  - To enhance long-term scalability and flexibility, the learning process should naturally filter out unnecessary deaths.

---

# 10,000 Epoch Evaluation: total average: 15

Still not achieving high scores. Occasionally, a score in the 30s appears, but the frequency is very low, and the average score does not exceed 15.

## Improvement Directions
- Set the minimum epsilon value to 0.1% to stabilize breakthroughs after a certain level of learning is achieved.

---

# 10,000 Epoch Evaluation

Average score: +-14, Maximum score: 32. Still not a satisfactory result.

## Improvement Ideas
- Add to state:
  - Head position
  - Tail position
  - Neck direction
  - Body length

## Changes
- Reset epsilon to 1%.

---

# 15,000 Epoch Evaluation

Average score: 0.45, Maximum score: 2. Likely added too many features to the state.

## Improvement Directions
- Remove from state:
  - Head position
  - Tail position
- Add to state:
  - Distance to the nearest wall

### Recording Attempt
- Open two windows simultaneously to compare penalties for dying: -1 vs. -5.

---

# 10,000 Epoch Evaluation

The concept of the nearest wall distance seems ineffective. It was intended to prevent crashing into walls, but in hindsight, each wall’s distance should have been considered instead.

## Improvement Directions
- Replace the nearest wall distance with the individual distances to each wall.

---

# 50,000+ Epoch Evaluation

Possibly due to the increased state complexity, the last 100 epoch average fluctuates around 2.5, with a maximum score of only 6. The AI keeps crashing into itself—it's unclear whether epsilon-triggered exploration is causing it or if it still hasn't learned that hitting itself results in death. It's frustratingly baffling.

At the time of writing, I’ve just passed 60,000 epochs. The last 100 epoch average peaked at 3.0 before dropping again. This suggests slight improvements, but whether there's an end in sight is questionable. It might be time to stop and move on to the next phase.

---

# Conclusion: Transitioning to DQN