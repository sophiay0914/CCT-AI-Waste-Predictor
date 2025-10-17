import streamlit as st

st.divider()

# ---------- Rule-based conversation graph (edit this to fit your flows) ----------
FLOW = {
    "start": {
        "text": "Hi! I’m here to help you start your sustainability journey based off of your results. What do you need?",
        "options": [
            {"label": "Product Catalog", "next": "product_catalog"},
            {"label": "Recommendation", "next": "recommendation"},
            {"label": "Contact support", "next": "contact"},
        ],
    },
    "product_info": {
        "text": "Sustainable packaging comes in different forms: honeycomb padded mailers, paper mailers, honeycomb paper, kraft tape. What would you like to learn about?",
        "options": [
            {"label": "Hone", "next": "alpha"},
            {"label": "Beta", "next": "beta"},
            {"label": "Gamma", "next": "gamma"},
            {"label": "⬅️ Back", "next": "start"},
        ],
    },
    "alpha": {
        "text": "Alpha includes core features and email support. Anything else?",
        "options": [
            {"label": "See pricing", "next": "pricing"},
            {"label": "⬅️ Back to Products", "next": "product_info"},
        ],
    },
    "beta": {
        "text": "Beta adds automation and team collaboration. Anything else?",
        "options": [
            {"label": "See pricing", "next": "pricing"},
            {"label": "⬅️ Back to Products", "next": "product_info"},
        ],
    },
    "gamma": {
        "text": "Gamma includes everything in Beta plus SSO and a dedicated manager.",
        "options": [
            {"label": "See pricing", "next": "pricing"},
            {"label": "⬅️ Back to Products", "next": "product_info"},
        ],
    },
    "pricing": {
        "text": "Pricing: Alpha $9/mo, Beta $29/mo, Gamma custom. Need a quote?",
        "options": [
            {"label": "Get a quote", "next": "quote_form"},
            {"label": "⬅️ Back to Start", "next": "start"},
        ],
    },
    # Example node with a small form (no AI)
    "quote_form": {
        "text": "Great—tell us a bit and we’ll email a quote.",
        "form": {
            "fields": [
                {"key": "name", "label": "Your name", "type": "text", "required": True},
                {"key": "email", "label": "Email", "type": "text", "required": True},
                {"key": "plan", "label": "Plan", "type": "select", "choices": ["Alpha", "Beta", "Gamma"], "required": True},
            ],
            "submit_label": "Request quote",
            "next_on_submit": "quote_done",
        },
        "options": [{"label": "⬅️ Back to Pricing", "next": "pricing"}],
    },
    "quote_done": {
        "text": "Thanks! We’ll send a quote shortly. Anything else?",
        "options": [
            {"label": "Back to Start", "next": "start"},
        ]
    },
    "contact": {
        "text": "You can reach support at support@example.com or (555) 555-5555.",
        "options": [
            {"label": "Back to Start", "next": "start"},
        ],
    },
}

# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "current_node" not in st.session_state:
    st.session_state.current_node = "start"
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

def go(node_id: str):
    st.session_state.current_node = node_id
    node = FLOW[node_id]
    st.session_state.history.append({"role": "assistant", "content": node["text"]})

def reset_chat():
    st.session_state.history = []
    st.session_state.current_node = "start"
    st.session_state.form_data = {}
    go("start")

if not st.session_state.history:
    go("start")

# ---------- Chat UI renderer (used inside the floating popover) ----------
def render_chat_ui():
    # Controls row
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⟳ Restart", use_container_width=True):
            reset_chat()
            st.rerun()
    with c2:
        st.download_button(
            "⬇️ Export transcript",
            data="\n".join([f'{m["role"]}: {m["content"]}' for m in st.session_state.history]),
            file_name="chat_transcript.txt",
            use_container_width=True
        )

    st.divider()

    # History
    for m in st.session_state.history[-12:]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    node_id = st.session_state.current_node
    node = FLOW[node_id]

    # Optional form
    if "form" in node:
        with st.chat_message("assistant"):
            st.markdown(node["text"])
            form_cfg = node["form"]
            with st.form("mini_chat_form", clear_on_submit=False):
                data = st.session_state.form_data.setdefault(node_id, {})
                for field in form_cfg["fields"]:
                    key = field["key"]
                    label = field["label"]
                    ftype = field.get("type", "text")
                    required = field.get("required", False)
                    if ftype == "text":
                        data[key] = st.text_input(label, value=data.get(key, ""))
                    elif ftype == "select":
                        choices = field.get("choices", [])
                        idx = choices.index(data.get(key, choices[0])) if data.get(key) in choices and choices else 0
                        data[key] = st.selectbox(label, choices, index=idx)
                    else:
                        data[key] = st.text_input(label, value=data.get(key, ""))  # fallback

                submitted = st.form_submit_button(form_cfg.get("submit_label", "Submit"))
                if submitted:
                    missing = [f["label"] for f in form_cfg["fields"] if f.get("required") and not data.get(f["key"], "").strip()]
                    if missing:
                        st.warning("Please fill: " + ", ".join(missing))
                    else:
                        summary = ", ".join(f"{f['label']}: {data.get(f['key'])}" for f in form_cfg["fields"])
                        st.session_state.history.append({"role": "user", "content": f"(submitted) {summary}"})
                        go(form_cfg["next_on_submit"])
                        st.rerun()

    # Options as buttons
    if "options" in node and node["options"]:
        with st.chat_message("assistant"):
            st.caption("Choose an option:")
            cols = st.columns(min(3, len(node["options"])))
            for i, opt in enumerate(node["options"]):
                col = cols[i % len(cols)]
                if col.button(opt["label"], key=f"opt_{node_id}_{i}", use_container_width=True):
                    st.session_state.history.append({"role": "user", "content": opt["label"]})
                    go(opt["next"])
                    st.rerun()
    else:
        with st.chat_message("assistant"):
            st.info("End of this path. Use **Restart** to begin again.")

# ---------- Floating launcher styles ----------
st.markdown("""
<style>
/* Position the launcher container at bottom-right */
._chat_launcher_anchor { position: fixed; right: 16px; bottom: 16px; z-index: 1000; }

/* Make the popover panel a nice compact size */
[data-testid="stPopover"] > div { width: 360px; max-width: 90vw; }
</style>
""", unsafe_allow_html=True)

# ---------- Floating launcher + popover ----------
# NOTE: Requires Streamlit >= 1.32 for st.popover.
# If your version doesn't have st.popover, replace the block below with:
#   with st.expander("💬 Get Personalized Recommendations", expanded=True): render_chat_ui()
# and remove the floating CSS to keep it simple.

anchor = st.container()
with anchor:
    # The next two lines "wrap" the launcher so the CSS can pin it to bottom-right
    st.markdown('<div class="_chat_launcher_anchor">', unsafe_allow_html=True)
    try:
        # Popover trigger (click to open the mini chat)
        with st.popover("💬 Get Personalized Recommendations"):
            render_chat_ui()
    except Exception:
        # Fallback for older Streamlit: use an expander instead of popover
        with st.expander("💬 Get Personalized Recommendations", expanded=False):
            render_chat_ui()
    st.markdown('</div>', unsafe_allow_html=True)
