# Limitation 1: Situations Where the AI Traps Itself in a Closed Space Formed by Its Own Body

## Solution: `Flood Fill`
- Use `Flood Fill` to evaluate the safety score* of the next move, and allow movement only if it meets a user-defined safety score threshold.

**Safety score\***: the amount of area that can be secured relative to a given point.

### Evaluation of the Solution
- Even if the AI moves only to safe spaces, it still faces the same challenges in mid-to-late game scenarios where similar situations arise.
- The safety score threshold needs to be dynamically adjusted based on the game's progress. Additionally, improving **Rule-based AI** in a highly random game like 'Snake' is less efficient compared to employing an alternative model.

---

# Conclusion

It is more prudent to transition from the current **Rule-based AI** to a **Greedy-Algorithm-based AI** and conduct further research.