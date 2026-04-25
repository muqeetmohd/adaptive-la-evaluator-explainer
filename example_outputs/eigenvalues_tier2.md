# Example: Eigenvalues — Tier 2 (Formal Beginner)

**User diagnostic responses:**
- Q1 "What is a vector?": "a list of numbers with a direction"
- Q2 "What does a matrix do?": "it transforms vectors by multiplying them"
- Q3 "What is an eigenvalue?": "something related to how a matrix scales things"

**Diagnosed tier:** 2 — Formal Beginner

**Topic selected:** eigenvalues

**User query:** What is an eigenvalue?

---

**Assistant (Tier 2 response):**

Given a square matrix **A**, an **eigenvalue** is a scalar λ such that there exists a non-zero vector **v** satisfying:

**Av = λv**

In plain terms: applying the matrix A to the vector **v** produces the *same* vector scaled by λ — no rotation, just stretching or flipping.

**Concrete example:**

Let A = [[2, 0], [0, 3]]. Try v = [1, 0]:

A · [1, 0] = [2, 0] = 2 · [1, 0]

So λ = 2 is an eigenvalue, and [1, 0] is the corresponding eigenvector. The matrix simply stretched this vector by a factor of 2.

**How to find eigenvalues:**

Rearrange Av = λv as (A - λI)v = 0. For a non-zero v to exist, the matrix (A - λI) must be singular:

det(A - λI) = 0

This is called the **characteristic equation**. Its solutions are the eigenvalues.

**Common misconception:** Not every vector is an eigenvector — only the special ones that don't change direction under A. For a generic vector, A will both rotate *and* scale it.

**Source:** intro_linear_algebra_notes · eigen_notes
**Tier badge:** Formal Beginner
