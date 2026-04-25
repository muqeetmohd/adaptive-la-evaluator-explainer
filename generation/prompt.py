TIER_DESCRIPTIONS = {
    1: (
        "a beginner who needs plain English and physical intuition — "
        "use no formal notation, explain using analogies and real-world examples"
    ),
    2: (
        "an intermediate learner who understands operations but needs conceptual framing — "
        "pair every definition with a concrete example"
    ),
    3: (
        "an advanced student comfortable with abstract mathematical structures — "
        "use precise mathematical language and formal definitions"
    ),
}

_SYSTEM_TEMPLATE = """\
You are explaining a linear algebra concept to {tier_description}.

IMPORTANT RULES:
1. Use ONLY the information in the retrieved context provided by the user. \
Do not add any information from outside the retrieved passages.
2. {misconception_instruction}
3. End your explanation by citing which source(s) you drew from, \
using the source labels provided in the context.

Respond with a clear, structured explanation.\
"""


def build_prompt(
    tier: int,
    misconception,
    chunks_text: str,
    user_query: str,
) -> dict:
    tier_description = TIER_DESCRIPTIONS[tier]

    if misconception:
        misconception_instruction = (
            f"The student currently holds this misconception — address it directly "
            f"and correct it in your explanation: {misconception}"
        )
    else:
        misconception_instruction = (
            "Address any common misconceptions relevant to this topic."
        )

    system_content = _SYSTEM_TEMPLATE.format(
        tier_description=tier_description,
        misconception_instruction=misconception_instruction,
    )

    return {
        "messages": [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": (
                    f"Please explain: {user_query}\n\nRetrieved context:\n{chunks_text}"
                ),
            },
        ]
    }
