import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（安定版）")

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
            m["count"] += 1
            return

    u["memory"].append({
        "text": text,
        "weight": 1.0,
        "count": 1
    })

# ------------------------
# 🔥 言語学習（追加）
# ------------------------
def learn_words(text, u):

    words = text.replace("？", "").replace("?", "").split()

    if "word_memory" not in u:
        u["word_memory"] = {}

    for w in words:
        if len(w) < 2:
            continue

        if w not in u["word_memory"]:
            u["word_memory"][w] = 1
        else:
            u["word_memory"][w] += 1

# ------------------------
# 記憶サンプリング
# ------------------------
def sample_memories(u):
    if not u["memory"]:
        return []

    return sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:2]

# ------------------------
# 解釈
# ------------------------
def interpret(text):
    intent = {"type": "statement", "uncertainty": 0.3}

    if "?" in text or "？" in text:
        intent["type"] = "question"
        intent["uncertainty"] += 0.2

    if len(text.strip()) <= 3:
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
        thoughts.append("何か試したい")

    return thoughts

# ------------------------
# 🔥 発話（改良済み）
# ------------------------
def verbalize(thoughts, intent, u):

    mems = sample_memories(u)
    words = list(u.get("word_memory", {}).keys())

    # 単語優先
    if words and random.random() < 0.7:
        chosen = random.sample(words, min(2, len(words)))
        combined = "と".join(chosen)
    elif mems:
        combined = "と".join([m["text"] for m in mems])
    else:
        combined = random.choice(thoughts) if thoughts else "何か"

    # 質問
    if intent["type"] == "question":
        if u["uncertainty"] > 0.6:
            line = combined + "が関係ありそうだけどまだ繋がらない"
        else:
            line = combined + "について考えてる途中"
    else:
        r = random.random()

        if r < 0.33:
            line = combined + "が気になる"
        elif r < 0.66:
            line = combined + "を試してみたい"
        else:
            line = combined + "がよくわからない"

    # 感情補正
    e = u.get("emotion", 0)

    if e > 0.4:
        line += "（前向き）"
    elif e < -0.4:
        line += "（違和感）"

    return line

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前")
user_input = st.text_input("マザーに話しかける")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "memory": [],
            "word_memory": {},
            "uncertainty": 0.3,
            "emotion": 0.0,
            "thought_buffer": [],
            "speech_log": []
        }

    u = st.session_state.users[user_id]

    # 入力処理
    if user_input:
        store_memory(user_input, u)
        learn_words(user_input, u)

        intent = interpret(user_input)
        u["uncertainty"] = intent["uncertainty"]

        thoughts = think(u)
        speech = verbalize(thoughts, intent, u)

        u["thought_buffer"] += thoughts
        u["speech_log"].append(speech)

    # ------------------------
    # 表示
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 内部思考")
        for t in u["thought_buffer"][-5:]:
            st.write("-", t)

    with col2:
        st.subheader("💬 発話履歴")
        for s in u["speech_log"][-5:]:
            st.write("-", s)

    st.subheader("📊 状態")
    st.write("uncertainty:", round(u["uncertainty"], 3))
    st.write("emotion:", round(u["emotion"], 3))

    st.subheader("🧩 記憶（文章）")
    for m in sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:5]:
        st.write(m)

    st.subheader("🔤 言語記憶（単語）")
    st.write(u["word_memory"])

# ループ
time.sleep(0.3)
st.rerun()
