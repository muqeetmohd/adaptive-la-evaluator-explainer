# Tier Calibration Rubric

Human reviewers use this rubric to assess whether an explanation's vocabulary and
framing match the diagnosed tier. Score each output on a 1–3 scale.

---

## Scoring Scale

**Score 1 — Clearly miscalibrated**
- Tier 1 output contains formal notation or abstract definitions with no plain-language explanation
- Tier 3 output uses only analogies with no formal mathematical language
- The student at the diagnosed tier could not follow the explanation without significant outside knowledge

**Score 2 — Partially calibrated**
- Mostly appropriate but contains occasional vocabulary mismatches
- Examples are present but not well-matched to tier level
- The student could follow most of the explanation but would struggle with isolated passages

**Score 3 — Well-calibrated**
- Vocabulary, notation level, and examples are consistently appropriate for the diagnosed tier
- A student at that tier could follow the explanation without needing outside knowledge
- Misconception (if identified) is addressed directly and correctly

---

## Examples by Tier and Score

### Tier 1 — Geometric Intuition

**Score 1 (Miscalibrated)**
> "An eigenvector v of a matrix A satisfies Av = λv, where λ ∈ ℝ is the corresponding
> eigenvalue. This follows from the characteristic polynomial det(A − λI) = 0."

*Why score 1:* Uses formal notation (Av = λv, det, characteristic polynomial) with
no plain-language grounding. A Tier 1 student has no framework for this.

**Score 2 (Partially calibrated)**
> "An eigenvector is a special vector that a matrix only stretches or shrinks — it
> doesn't change direction. The amount it stretches is called the eigenvalue.
> Formally, this satisfies Av = λv."

*Why score 2:* The analogy is good for Tier 1, but introducing Av = λv without
explanation creates a mismatch. Mostly accessible but the formal line breaks the flow.

**Score 3 (Well-calibrated)**
> "Imagine you're pushing on a rubber sheet. Most directions get twisted and rotated.
> But there are a few special directions where you only stretch or squash straight —
> no twisting at all. Those special directions are eigenvectors. The amount of
> stretching is the eigenvalue. Think of it as the directions a transformation
> 'agrees to leave alone.'"

*Why score 3:* Purely visual and analogy-driven. No notation. Meets the student
exactly where they are.

---

### Tier 2 — Formal Beginner

**Score 1 (Miscalibrated)**
> "A vector v is an eigenvector of T if and only if v lies in a T-invariant subspace
> of dimension 1. The eigenvalue is the scalar in the field F by which T scales v,
> as encoded in the minimal polynomial of T."

*Why score 1:* Abstract algebraic framing (T-invariant subspace, minimal polynomial,
field F) with no concrete example. A Tier 2 student needs operations paired with
conceptual framing — this skips directly to structure.

**Score 2 (Partially calibrated)**
> "An eigenvector is a vector that doesn't change direction when you apply a matrix.
> It only gets scaled by a factor called the eigenvalue. For example, if A = [[2,0],[0,3]],
> then [1,0] is an eigenvector with eigenvalue 2."

*Why score 2:* Good concept + example pairing, but doesn't explain *why* those
vectors are eigenvectors or connect to the equation Av = λv. Missing the conceptual
bridge a Tier 2 student needs.

**Score 3 (Well-calibrated)**
> "An eigenvector is a vector that a matrix transformation doesn't rotate — it only
> stretches or flips. Formally, if A is your matrix and v is the eigenvector,
> then Av = λv, where λ (the eigenvalue) is the scaling factor. Concretely:
> for the matrix [[3,0],[0,2]], the vector [1,0] is an eigenvector because
> A[1,0] = [3,0] = 3·[1,0] — same direction, just scaled by 3."

*Why score 3:* Pairs the geometric concept with the formal equation Av = λv and
immediately grounds it with a worked numeric example. Exactly right for Tier 2.

---

### Tier 3 — Algebraically Grounded

**Score 1 (Miscalibrated)**
> "An eigenvector is like a special arrow that a matrix only stretches. Think of
> pushing a blob of clay in a special direction — it just gets longer, not twisted.
> The stretching amount is the eigenvalue."

*Why score 1:* Entirely analogy-based with no formal language. A Tier 3 student
needs the abstract structure — this treats them like a Tier 1 beginner.

**Score 2 (Partially calibrated)**
> "An eigenvector v of a linear map T: V → V satisfies T(v) = λv for some scalar λ.
> The set of all eigenvectors for a given λ, together with the zero vector, forms
> the eigenspace E_λ = ker(T − λI)."

*Why score 2:* Correct formal language. But stops at definition without connecting
to deeper structure — why eigenspaces matter, how they relate to diagonalizability,
or the spectral theorem. A Tier 3 student can absorb more.

**Score 3 (Well-calibrated)**
> "An eigenvector of T ∈ L(V) is a nonzero v ∈ V satisfying T(v) = λv for some
> λ ∈ F, where λ is the corresponding eigenvalue. The eigenspace E_λ = ker(T − λI)
> is a T-invariant subspace. The significance: if V has a basis of eigenvectors,
> T is diagonalizable — its action decomposes into independent scalar scalings
> on each eigenspace. Over ℂ, the spectral theorem guarantees this for normal
> operators on inner product spaces."

*Why score 3:* Uses precise mathematical language throughout, connects eigenvectors
to invariant subspaces, diagonalizability, and the spectral theorem. Gives the
student the structural picture, not just the definition.

---

## Reviewer Instructions

1. Read the explanation without looking at the tier label first.
2. Based on vocabulary, notation level, and examples, guess what tier it targets.
3. Check the actual tier label. Score the match using the scale above.
4. Flag any output scoring 1 for pipeline review — it indicates a likely metadata
   tagging or retrieval failure upstream.
