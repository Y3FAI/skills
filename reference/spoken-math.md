# Writing math for the ear

All of these lines were voiced with Kokoro `af_heart` in the MATH251 guide and passed Whisper checks.
The pattern: say what the formula **does**, in the order you would do it, and keep one spoken form per notation.

## Shown → said

| On the page | data-say |
|---|---|
| `det(A) = ad − bc` | The determinant is A times d, minus b times c: the main diagonal minus the other diagonal. |
| `d(u,v) = √((u₁−v₁)² + (u₂−v₂)² + (u₃−v₃)²)` | The distance between u and v: subtract matching coordinates, square each difference, add them, then take the square root. |
| `u·v = u₁v₁ + u₂v₂ + u₃v₃` | The dot product u dot v: multiply matching coordinates, then add. That is u 1 v 1, plus u 2 v 2, plus u 3 v 3. |
| `u×v = (u₂v₃−u₃v₂, u₃v₁−u₁v₃, u₁v₂−u₂v₁)` | u cross v has three entries. First, u 2 v 3 minus u 3 v 2. Second, u 3 v 1 minus u 1 v 3. Third, u 1 v 2 minus u 2 v 1. |
| `Cᵢⱼ = (−1)^(i+j) Mᵢⱼ` | The cofactor C i j is the minor M i j, times minus one to the power i plus j. |
| `det(kA) = kⁿ det(A)` | The determinant of k times A is k to the power n, times the determinant of A, where n is the size of the matrix. |
| `A⁻¹ = 1/(ad−bc) [d −b; −c a]` | A inverse is one over A d minus b c, times a new matrix: swap A and d, and put minus signs on b and c. |
| `Rank(A) + Nullity(A) = n` | Rank plus nullity equals n, the number of columns. |
| `xᵢ = det(Aᵢ)/det(A)` | Each unknown x i is the determinant of A i, divided by the determinant of A. |
| `[1 2; 3 4]` | the matrix with rows 1, 2 and 3, 4 |
| `T: ℝⁿ → ℝᵐ` | T, from R n to R m |
| `θ = 90°` | the angle is 90 degrees |
| `2/3` | two thirds |
| `(AB)ᵀ = BᵀAᵀ` | The transpose of A B is B transpose times A transpose. The order flips. |

## Rules of thumb

- **Words for every symbol.** Equals, plus, minus, times, over, "to the power", "squared", "dot", "cross", "transpose", "inverse".
- **Subscripts:** say "u 1", "C i j" and "x i" with spaces, and never "sub". The checker treats "u 2 v 3" and "U2V3" as the same.
- **Tuples:** read them as lists: "minus 2, 3, minus 6".
- **Matrix sizes:** "2 by 3", never "2 times 3".
- **Worked steps:** one step per line, numbers spoken plainly: "Multiply matching numbers and add: 1 times 0, plus 2 times 3, gives 6."
- **The variable `a`:** write it as capital `A` in speech; see SKILL.md.
- **Reading a symbol aloud is a last resort.** If a formula has no natural reading, describe its job instead: "The adjugate is the transpose of the cofactor matrix."
- **Sentence-initial "A" is risky** when it means the article *a* followed by a word in the NOT_A_NOUN list (is, inverse, transpose, times, …): "A transpose changes nothing" will be read as the matrix *A*. Reword it to "Transposing changes nothing".

## False alarms the checker reports (publish with --force)

- Cramer ↔ Kramer
- B A ↔ "be A"
- c 1, c 2 ↔ C1, C2
- Sarrus ↔ "Saris"
- read along ↔ "read a long"

When both Whisper and Nova write the same different word and it **isn't** a homophone, the voice really said it wrong. Reword that line.
