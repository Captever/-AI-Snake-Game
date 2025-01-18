# Weight Research

## Weight 0.8
The AI consistently chooses completely safe paths, even if it means taking a longer route. However, this behavior often leads to unnecessary movements, which can be disadvantageous in the long term.

## Weight 0.3
This value was deemed appropriately optimized. The AI avoids choosing nearby feeds if the surrounding space isn't safe. During testing, it achieved a highest score of 57, significantly outperforming all previous tests.

## Weight 0.05
While the AI calculates safety scores, the low weight means safety has minimal impact on decision-making. Early in the game, with abundant empty spaces, it helps avoid lethal paths. However, in the mid-to-late game, the difference between safe and unsafe spaces diminishes, leading to suboptimal decisions akin to previous implementations.

# Conclusion
While the AI has shown improved average scores and early-game performance with near-zero fatalities, there are instances where it blocks its escape route by over-prioritizing safe paths. Without further enhancements, such as better handling of its elongated body in the late game or strategic coiling for favorable positioning, significant improvements are unlikely.