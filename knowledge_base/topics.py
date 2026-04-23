TOPIC_LIST = [
    "vectors",
    "matrix_multiplication",
    "linear_transformations",
    "determinants",
    "eigenvalues",
    "eigenvectors",
    "vector_spaces",
    "linear_independence",
    "basis",
    "rank",
    "dot_product",
    "orthogonality",
    "systems_of_equations",
    "row_reduction",
    "matrix_inverse",
]

PREREQUISITES = {
    "eigenvalues": ["linear_transformations", "determinants"],
    "eigenvectors": ["eigenvalues", "linear_transformations"],
    "linear_transformations": ["matrix_multiplication", "vectors"],
    "matrix_multiplication": ["vectors"],
    "vector_spaces": ["vectors", "linear_independence"],
    "linear_independence": ["vectors", "basis"],
    "basis": ["linear_independence", "vector_spaces"],
    "rank": ["row_reduction", "linear_independence"],
    "orthogonality": ["dot_product", "vector_spaces"],
    "determinants": ["matrix_multiplication", "row_reduction"],
    "row_reduction": ["systems_of_equations"],
    "matrix_inverse": ["matrix_multiplication", "determinants"],
    "dot_product": ["vectors"],
    "systems_of_equations": ["vectors"],
    "vectors": [],
}


def get_prerequisites(topic: str) -> list:
    return PREREQUISITES.get(topic, [])
