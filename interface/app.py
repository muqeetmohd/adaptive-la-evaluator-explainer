import gradio as gr
from sentence_transformers import SentenceTransformer

from knowledge_base.embed import load_knowledge_base
from knowledge_base.topics import TOPIC_LIST
from diagnostic.diagnostic import QUESTIONS
from pipeline import run_session

_EMBED_MODEL = "all-MiniLM-L6-v2"

print("Loading embedding model...")
_model = SentenceTransformer(_EMBED_MODEL)

print("Loading ChromaDB collection...")
try:
    _collection = load_knowledge_base()
    print("Knowledge base loaded.")
except Exception as e:
    _collection = None
    print(f"WARNING: Could not load knowledge base: {e}")


def _build_initial_state():
    return {"responses": [], "stage": "diagnostic", "topic": TOPIC_LIST[0]}


def respond(user_message, history, state, topic):
    if state is None:
        state = _build_initial_state()

    state["topic"] = topic

    if state["stage"] == "diagnostic":
        state["responses"].append(user_message)
        history.append((user_message, None))
        q_index = len(state["responses"])

        if q_index < 3:
            bot_reply = QUESTIONS[q_index]
        else:
            state["stage"] = "query"
            bot_reply = (
                f"Thanks! Now ask me anything about **{topic}**. "
                "I'll explain it at your level."
            )

        history[-1] = (user_message, bot_reply)
        return history, state, "", ""

    # Query stage
    if _collection is None:
        bot_reply = (
            "ERROR: Knowledge base not loaded. "
            "Please build it first by running `knowledge_base/embed.py`."
        )
        history.append((user_message, bot_reply))
        return history, state, "", ""

    history.append((user_message, "Generating explanation..."))

    try:
        result = run_session(
            user_query=user_message,
            diagnostic_responses=state["responses"],
            topic=topic,
            collection=_collection,
            embed_model=_model,
        )
        explanation = result["explanation"]
        meta = (
            f"**Diagnosed tier:** {result['tier']}  |  "
            f"**Sources used:** {', '.join(result['sources_used'])}"
        )
    except RuntimeError as e:
        explanation = f"ERROR: {e}"
        meta = ""

    history[-1] = (user_message, explanation)
    return history, state, "", meta


def reset(topic):
    state = _build_initial_state()
    state["topic"] = topic
    opening = QUESTIONS[0]
    return [(None, opening)], state, "", ""


with gr.Blocks(title="Adaptive Linear Algebra Explainer") as demo:
    gr.Markdown("# Adaptive Linear Algebra Explainer")
    gr.Markdown("Answer 3 quick questions so I can explain at your level.")

    with gr.Row():
        topic_dropdown = gr.Dropdown(
            choices=TOPIC_LIST,
            value=TOPIC_LIST[0],
            label="Topic",
        )

    chatbot = gr.Chatbot(height=450)
    meta_display = gr.Markdown("")

    with gr.Row():
        user_input = gr.Textbox(
            placeholder="Type your answer or question here...",
            show_label=False,
            scale=8,
        )
        submit_btn = gr.Button("Send", scale=1)
        reset_btn = gr.Button("Restart", scale=1)

    session_state = gr.State(None)

    submit_btn.click(
        respond,
        inputs=[user_input, chatbot, session_state, topic_dropdown],
        outputs=[chatbot, session_state, user_input, meta_display],
    )
    user_input.submit(
        respond,
        inputs=[user_input, chatbot, session_state, topic_dropdown],
        outputs=[chatbot, session_state, user_input, meta_display],
    )
    reset_btn.click(
        reset,
        inputs=[topic_dropdown],
        outputs=[chatbot, session_state, user_input, meta_display],
    )

    demo.load(
        reset,
        inputs=[topic_dropdown],
        outputs=[chatbot, session_state, user_input, meta_display],
    )

if __name__ == "__main__":
    demo.launch()
