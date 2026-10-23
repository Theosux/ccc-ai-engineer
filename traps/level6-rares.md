# Level 6 Traps - rares

- **Exact Count Requirement**: The statement says "how many times each must be submitted" (line 15) and "generate a program that creates the pattern the required number of times" (line 16). This implies `acc == cnt`, not `acc >= cnt`.
- **Score is Total Lines**: "Your score is the total number of instruction lines in your programs" (line 18). This is a global optimization problem across all patterns.
- **Matter-Pattern-Skirt Logic**: Matter is created when exactly 2 rays hit a cell (simulate:88) and destroyed when 3+ rays hit (simulate:90). A pattern is accepted if `pcells <= matter` (all pattern cells are matter) AND `not (skirt & matter)` (no skirt cells are matter) (simulate:92).
- **Skirt Definition**: The skirt consists of all cells in the interior that are neighbors of a pattern cell but are not themselves part of the pattern (simulate:65-69).
- **Pattern Consumption**: When a pattern is accepted, those cells are removed from the matter set (`matter -= pcells`, simulate:93). This means the same cells cannot be used to form the same pattern twice without being re-created.
- **Emitter-Position Loop**: Emitters move on a ring of size $6 \times r$ (simulate:77, 79). The ring is indexed $0 \dots (6r-1)$.
- **Instruction Set**: Only `F` (Forward), `B` (Backward), and `T` (Toggle) are allowed (lines 26-35).
- **Output Format**: Programs must be separated by a "Mandatory empty line between programs" (line 36). Each program line must contain exactly 6 instructions separated by spaces (line 25).
- **Input Scale**: The largest input `in_level-6_4-enormous.txt` contains patterns with $r$ up to 12, $h$ up to 25, $w$ up to 49, and counts up to 140.
- **Coordinate System**: The board radius $r$ defines the board size. The ring is the outer boundary. Emitters are on the ring, and they fire rays into the interior.
- **Precision/Rounding**: Not applicable as this is a discrete grid problem.
- **Tie-breaks**: Not mentioned; the objective is simply the minimum total lines.
