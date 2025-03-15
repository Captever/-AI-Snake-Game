# Prototype (Initial Version)

Focusing on the 6-8 point range, it's easy to see that since there are definite safe moves when moving into empty spaces, the AI tends to circle around the food instead of eating it, even when the food is right next to it.

After surpassing the TOP score of 20 points, progress has been slowing down. Personally, I think the high probability of exploration plays a role. Up until around 17-18 points, the AI still has safe moves available, but it tends to explore instead, leading to occasional failures before reaching 20 points.

Between epochs 1400-1700, the last 100 epoch scores dropped to around 7 points. Why is this happening?

Currently, at around epoch 1700, there is still at least one game in every ten that ends with a score of 0. Has the AI still not adapted to wall and body collisions? Or is this an unusual case where exploration due to epsilon leads to bad moves?  
Considering that the AI generally reaches 15+ points without major issues, I suspect this is an anomaly caused by exploration.

As the AI reaches the late 2000s in epoch count, games ending with a score of 0 now occur only once in about 100 games.  
At epoch 3,200, the highest recorded score is 33 points, and the average over the last 100 epochs is around 14 points.

In the mid-3000 epochs, the last 100 epoch average dropped to the 12-point range but later recovered to 13 points. Currently, in the 3,700s, it briefly dipped to 12 again before recovering to 13, and it seems to be fluctuating around 13 points.  
From previous observations with the Greedy Algorithm, on a 10x10 grid, surpassing 21 points increases the likelihood of getting trapped even when taking a longer route such as (0, y) → (9, y) → (9, y±1) → (0, y±1).  
From that point, the number of points the AI can reach depends on the random placement of food, rather than its intelligence.  
It seems like the DQN AI is exhibiting similar behavior.

At epoch 4,200, the last 100 epoch average dropped to the low 6s, possibly due to overfitting.

Now at epoch 5,200, the AI has become familiar with moving toward food. However, it frequently dies by getting trapped in isolated paths created by its own body.  
I’ll leave it running overnight to see if this issue resolves over time.

# Applied Improvements
- Delayed Epsilon scheduling: Changed `epsilon_decay` from 0.995 to 0.999. Applied `epsilon_decay` every 5,000 steps instead of every step.
- Improved `ReplayBuffer.sample()` function to give higher weight to more recent data instead of purely random sampling.
- Reward system improvement: Previously, only ±0.1 based on distance to food and +1 for eating food existed. Now, added +0.01 survival points per step and -1 for GameOver.
- Removed mapped integer values for neck direction from `state`.

After running 240,000 epochs, the highest score is only 5 points, with an average score of 0.156. It seems I set the epsilon range too wide.

# Applied Improvements
- Accelerated Epsilon scheduling: Changed `epsilon_decay` back from 0.999 to 0.995 and applied `epsilon_decay` every 1,000 steps instead of every 5,000.
- Modified reward system: Changed distance-based reward from ±0.1 to ±0.5, and increased survival reward from +0.01 to +0.1.
- Improved `ReplayBuffer.sample()` function: Changed weight calculation from linear to logarithmic (`log(i + 1)`).

Oh! I left it running overnight, so I’ll need to review the footage, but at epoch 55,242, it achieved 50 points.

# Attempting MCTS (Monte Carlo Tree Search) Implementation

The attempt to apply Monte Carlo Tree Search failed. I tried integrating a prototype code, but it didn’t work as expected.  
Given my current skill level, I will try implementing `Policy Gradient` first instead.  
In reality, even if MCTS had worked, it wouldn't have solved the long-term issue, so skipping it shouldn't be a big problem.