# Example: Eigenvalues — Tier 3 (Algebraically Grounded)

**User diagnostic responses:**
- Q1 "What is a vector?": "an element of a vector space over a field"
- Q2 "What does a matrix do?": "it represents a linear map between finite-dimensional vector spaces"
- Q3 "What is an eigenvalue?": "a scalar in the spectrum of a linear operator"

**Diagnosed tier:** 3 — Algebraically Grounded

**Topic selected:** eigenvalues

**User query:** What is an eigenvalue?

---

**Assistant (Tier 3 response):**

Let V be a finite-dimensional vector space over a field F, and let T: V → V be a linear operator. A scalar λ ∈ F is an **eigenvalue** of T if there exists a non-zero vector v ∈ V such that:

T(v) = λv

The vector v is the corresponding **eigenvector**. The set of all eigenvectors associated with λ, together with the zero vector, forms the **eigenspace** E_λ = ker(T - λI), which is a T-invariant subspace of V.

**Characteristic polynomial:**

λ is an eigenvalue of T if and only if (T - λI) is not invertible, equivalently:

p(λ) = det(T - λI) = 0

The polynomial p ∈ F[x] of degree n = dim(V) is the **characteristic polynomial** of T. Its roots (in the algebraic closure of F) are the eigenvalues. The **algebraic multiplicity** of λ is its multiplicity as a root of p; the **geometric multiplicity** is dim(E_λ).

**Key theorem:** The geometric multiplicity of any eigenvalue never exceeds its algebraic multiplicity. T is diagonalizable over F if and only if the algebraic and geometric multiplicities coincide for every eigenvalue and the characteristic polynomial splits completely over F.

**Spectral decomposition:** When T is diagonalizable, V decomposes as a direct sum of eigenspaces:

V = E_{λ_1} ⊕ E_{λ_2} ⊕ ... ⊕ E_{λ_k}

and T acts as scalar multiplication by λ_i on each E_{λ_i}.

**Source:** eigen_notes
**Tier badge:** Algebraically Grounded
