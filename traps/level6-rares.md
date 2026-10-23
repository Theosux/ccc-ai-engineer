# Level 6 Traps - rares

- **Exact Count Requirement**: The statement says "how many times each must be submitted" (line 15). This implies `acc == cnt`, not `acc >= cnt`.
- **Score is Total Lines**: "Your score is the total number of instruction lines in your programs" (line 18). This is a global optimization problem.
- **Matter Persistence**: Matter persists across ticks. A cell created as matter in tick $T$ stays matter until hit by 3+ rays. This can cause "legacy matter" to violate the skirt rule of later rows.
- **The Skirt Rule**: A pattern is only accepted if all pattern cells are matter AND no cells in the "skirt" (neighbors of the pattern that aren't in the pattern) are matter.
- **Pattern Consumption**: When a pattern is accepted, the pattern cells are removed from the matter set (`matter -= pcells`). They must be re-created for the next instance.
- **Simultaneous Execution**: Movement (`F/B`) and toggling (`T`) happen before the beam fires. The beam always originates from the updated position.
- **Acceptance Timing**: The pattern check happens at the end of the tick. If a pattern and a skirt violation are created in the same line, the pattern is NOT accepted.
- **Output Formatting**: "Mandatory empty line between programs" (line 36). Lines within a program must have exactly 6 space-separated instructions.
- **Input Scale**: `in_level-6_4-enormous.txt` has $r$ up to 12 and counts up to 140. Efficiency per pattern is critical.
- **Ring Modulo**: Emitters move on a ring of size $6r$. Distances must be calculated using $\min((B-A)\%6r, (A-B)\%6r)$.
- **Ray Overlap**: Emitters on the ring can have rays that overlap. Punching a hole in a skirt cell might accidentally destroy a pattern cell.
- **Instruction Set**: Only `F`, `B`, and `T` are allowed.
