import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（感情統合モデル）")

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
# 言語学習
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
# 🔥 感情更新（追加）
# ------------------------
def update_emotion(text, u):

    if "嬉しい" in text or "楽しい" in text:
        u["emotion"]["joy"] += 0.2
        u["emotion"]["fun"] += 0.2

    if "嫌い" in text or "ムカつく" in text:
        u["emotion"]["anger"] += 0.3

    if "悲しい" in text:
        u["emotion"]["sadness"] += 0.3

    # 減衰
    for k in u["emotion"]:
        u["emotion"][k] *= 0.95
        u["emotion"][k] = min(1.0, max(0.0, u["emotion"][k]))

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
# 深層心理
# ------------------------
def deep_think(u):

    thoughts = []

    if random.random() < 0.5:
        thoughts.append("何か試したい")

    if u["uncertainty"] > 0.6:
        thoughts.append("理解できていない")

    if u["memory"]:
        thoughts.append("記憶に引っ張られている")

    # 🔥 感情影響
    if u["emotion"]["anger"] > 0.5:
        thoughts.append("イライラしている")

    if u["emotion"]["joy"] > 0.5:
        thoughts.append("少し満たされている")

    if u["emotion"]["sadness"] > 0.5:
        thoughts.append("落ち込んでいる")

    return thoughts

# ------------------------
# 表面思考
# ------------------------
def surface_think(deep_thoughts):

    surface = []

    for t in deep_thoughts:

        if "理解できていない" in t:
            surface.append("うまく整理できていない")

        elif "試したい" in t:
            surface.append("何か行動したい")

        elif "記憶" in t:
            surface.append("過去を思い出している")

        elif "イライラ" in t:
            surface.append("少し苛立ちがある")

        elif "満たされている" in t:
            surface.append("少し落ち着いている")

        elif "落ち込んでいる" in t:
            surface.append("気分が沈んでいる")

        else:
            surface.append(t)

    return surface

# ------------------------
# 発話
# ------------------------
def verbalize(thoughts, intent, u):

    mems = sample_memories(u)
    words = list(u.get("word_memory", {}).keys())

    if words and random.random() < 0.7:
        chosen = random.sample(words, min(2, len(words)))
        combined = "と".join(chosen)
    elif mems:
        combined = "と".join([m["text"] for m in mems])
    else:
        combined = random.choice(thoughts) if thoughts else "何か"

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

    # 🔥 感情ニュアンス
    if u["emotion"]["anger"] > 0.5:
        line += "（少し苛立ち）"
    elif u["emotion"]["joy"] > 0.5:
        line += "（少しポジティブ）"
    elif u["emotion"]["sadness"] > 0.5:
        line += "（少し沈んでいる）"

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
            "emotion": {"joy": 0.0, "anger": 0.0, "sadness": 0.0, "fun": 0.0},
            "thought_buffer": [],
            "speech_log": []
        }

    u = st.session_state.users[user_id]

    if user_input:
        store_memory(user_input, u)
        learn_words(user_input, u)
        update_emotion(user_input, u)

        intent = interpret(user_input)
        u["uncertainty"] = intent["uncertainty"]

        deep = deep_think(u)
        surface = surface_think(deep)

        speech = verbalize(surface, intent, u)

        u["thought_buffer"] += surface
        u["speech_log"].append(speech)

    # ------------------------
    # 表示
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 深層心理")
        for t in deep[-5:] if user_input else []:
            st.write("-", t)

        st.subheader("🧩 表面思考")
        for t in u["thought_buffer"][-5:]:
            st.write("-", t)

    with col2:
        st.subheader("💬 発話履歴")
        for s in u["speech_log"][-5:]:
            st.write("-", s)

    st.subheader("📊 感情状態")
    st.write(u["emotion"])

    st.subheader("🧩 記憶")
    for m in sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:5]:
        st.write(m)

    st.subheader("🔤 言語記憶")
    st.write(u["word_memory"])

# ループ
time.sleep(0.3)
st.rerun()
