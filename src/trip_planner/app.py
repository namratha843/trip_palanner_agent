import requests
import streamlit as st

BASE_URL = "http://localhost:8001"

OCEAN = "#0B3A53"
LAGOON = "#12858C"
SAFFRON = "#F6A91B"

st.set_page_config(page_title="Trip Planner", page_icon="🧭", layout="centered")

# ---------- Styling ----------
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=DM+Sans:wght@400;500;700&display=swap');
        html, body, [class*="st-"] {{ font-family: 'DM Sans', sans-serif; }}
        .block-container {{ max-width: 820px; padding-top: 1.5rem; padding-bottom: 6rem; }}
        header[data-testid="stHeader"] {{ background: transparent; }}

        .hero {{
            background: {OCEAN}; border-radius: 20px;
            padding: 2rem 2rem 1.8rem; margin-bottom: 1.2rem;
        }}
        .hero .tag {{
            display: inline-block; background: {SAFFRON}; color: {OCEAN};
            font-weight: 700; font-size: 0.8rem; padding: 0.2rem 0.7rem;
            border-radius: 999px; margin-bottom: 0.8rem;
        }}
        .hero h1 {{
            font-family: 'Bricolage Grotesque', sans-serif; color: #fff;
            font-size: 2.4rem; line-height: 1.1; margin: 0 0 0.4rem; padding: 0;
        }}
        .hero p {{ color: #BCD8E3; font-size: 1.05rem; margin: 0; }}

        [data-testid="stChatMessage"] {{
            background: #fff; border: 1px solid #DCE8EE;
            border-radius: 16px; padding: 0.9rem 1.1rem; margin-bottom: 0.7rem;
        }}
        .stMarkdown h3 {{ color: {LAGOON}; font-family: 'Bricolage Grotesque', sans-serif; margin-top: 1rem; }}

        .stButton > button {{
            border-radius: 999px; border: 1.5px solid {LAGOON}; color: {LAGOON};
            background: #fff; font-weight: 600;
        }}
        .stButton > button:hover {{ background: {LAGOON}; color: #fff; border-color: {LAGOON}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- State ----------
st.session_state.setdefault("chat_history", [])


def start_over() -> None:
    st.session_state.chat_history = []


# ---------- Backend ----------
def ask_backend(query: str):
    try:
        r = requests.post(f"{BASE_URL}/query", json={"query": query}, timeout=120)
        r.raise_for_status()
        return True, r.json()["response"]
    except requests.exceptions.ConnectionError:
        return False, "Couldn't reach the planner. Make sure the backend is running."
    except requests.exceptions.Timeout:
        return False, "Planning took too long. Try again or simplify your request."
    except requests.exceptions.HTTPError as e:
        return False, f"The planner returned an error ({e.response.status_code})."
    except (KeyError, ValueError):
        return False, "The planner sent a response in an unexpected format."


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Ideas to try")
    st.markdown(
        "- 3 days in Goa for two, under ₹30,000\n"
        "- Weekend trip near Bengaluru\n"
        "- Make day 2 more relaxed"
    )
    st.button("Start over", on_click=start_over, use_container_width=True)

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
        <span class="tag">AI trip planner</span>
        <h1>Where to next?</h1>
        <p>Ask anything about your trip. Type it your way.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Chat ----------
for message in st.session_state.chat_history:
    avatar = "🧳" if message["role"] == "user" else "🧭"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

user_input = st.chat_input("Ask about a trip, or just say hi")

if user_input and user_input.strip():
    text_in = user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": text_in})
    with st.chat_message("user", avatar="🧳"):
        st.markdown(text_in)

    with st.chat_message("assistant", avatar="🧭"):
        with st.spinner("Thinking…"):
            ok, answer = ask_backend(text_in)
        if ok:
            st.markdown(answer)
        else:
            st.error(answer)

    if ok:
        st.session_state.chat_history.append({"role": "assistant", "content": answer})