import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（自己改善モデル）")

MIN_WEIGHT = 0.2

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    st.session_state.users = {}
    st.session_state.last_time = time.time()
    st.session_state.initialized = True

# ------------------------
# 記憶
# ------------------------
def store_memory(text, u):
    for m in u["memory"]:
        if text in m["text"]:
            m["weight"] += 0.5
            return
    u["memory"].append({"text": text, "weight": 1.0})

# ------------------------
# 解釈（？理解）
# ------------------------
def interpret(text):
    intent = {"type": "statement", "uncertainty": 0.3}

    if "?" in text or "？" in text:
        intent["type"] = "question"
        intent["uncertainty"] += 0.3

    if len(text) < 5:
        intent["uncertainty"] += 0.2

    return intent

# ------------------------
# 思考
# ------------------------
def think(u):
    thoughts = []

    if u["memory"]:
        thoughts.append("記憶を参照している")

    if u["uncertainty"] > 0.6:
        thoughts.append("よくわからない")

    if random.random() < 0.5:
        thoughts.append("何か考えようとしている")

    return thoughts

# ------------------------
# 発話（変換）
# ------------------------
def verbalize(thoughts, intent, u):

    if u["uncertainty"] > 0.7:
        return "まだうまく理解できてない"

    base = random.choice(thoughts) if thoughts else "何かある"

    patterns = [
        "{}気がする",
        "{}かもしれない",
        "なんとなく{}",
        "{}感じがある"
    ]

    if intent["type"] == "question":
        return "まだはっきりしないけど、少し考えてる"

    return random.choice(patterns).format(base)

# ------------------------
# 自己評価
# ------------------------
def evaluate_speech(text):
    score = 0.5

    if "わからない" in text:
        score -= 0.2

    if "気がする" in text:
        score += 0.1

    if len(text) > 10:
        score += 0.2

    return max(0, min(1, score))

# ------------------------
# 改善
# ------------------------
def improve(u, score):

    if score < 0.4:
        u["uncertainty"] += 0.1

    if score > 0.7:
        u["uncertainty"] *= 0.9

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前")
user_input = st.text_input("話しかける")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "memory": [],
            "uncertainty": 0.3,
            "speech_log": [],
            "eval_log": []
        }

    u = st.session_state.users[user_id]

    if user_input:
        store_memory(user_input, u)

        intent = interpret(user_input)
        u["uncertainty"] = intent["uncertainty"]

        thoughts = think(u)
        speech = verbalize(thoughts, intent, u)

        score = evaluate_speech(speech)
        improve(u, score)

        u["speech_log"].append(speech)
        u["eval_log"].append(score)

    # ------------------------
    # 表示
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 思考")
        for t in thoughts[-5:] if user_input else []:
            st.write("-", t)

    with col2:
        st.subheader("💬 発話履歴")
        for s in u["speech_log"][-10:]:
            st.write("-", s)

    st.subheader("📊 状態")
    st.write("uncertainty:", round(u["uncertainty"], 3))

    st.subheader("📈 発話評価")
    for e in u["eval_log"][-5:]:
        st.write(e)

# ループ
time.sleep(0.3)
st.rerun()

