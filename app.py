import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』")

# ------------------------
# 初期知識（拡張版）
# ------------------------
knowledge = {
    "嬉しい": {"emotion": 0.6},
    "楽しい": {"emotion": 0.7},
    "悲しい": {"emotion": -0.7},
    "辛い": {"emotion": -0.6},
    "怒り": {"emotion": -0.8},
    "好き": {"social": 0.5},
    "嫌い": {"social": -0.5},
    "怖い": {"emotion": -0.6},
    "安心": {"emotion": 0.5},
    "不安": {"emotion": -0.5},
    "試す": {"explore": 0.4},
    "新しい": {"explore": 0.5},
    "話す": {"social": 0.4},
    "一人": {"social": -0.3},
    "助けて": {"social": 0.6},
}

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    st.session_state.users = {}
    st.session_state.energy = 0.5
    st.session_state.last_time = time.time()
    st.session_state.initialized = True

# ------------------------
# 内部更新
# ------------------------
def update_internal(e, energy):
    e += random.uniform(-0.02, 0.02)
    e += (energy - 0.5) * 0.1
    e *= 0.99

    energy += random.uniform(-0.02, 0.02)
    energy += e * 0.05

    return max(-1, min(1, e)), max(0, min(1, energy))

# ------------------------
# 欲求更新
# ------------------------
def update_drive(drive, energy, emotion):

    drive["explore"] += 0.01 + energy * 0.05
    drive["social"] += 0.01 + emotion * 0.05

    drive["explore"] -= drive["social"] * 0.02
    drive["social"] -= drive["explore"] * 0.02

    for k in drive:
        drive[k] *= 0.995
        drive[k] = max(0, min(1, drive[k]))

    drive["explore"] = max(0.25, drive["explore"])

    return drive

# ------------------------
# 🔥 学習（入力→状態変化）
# ------------------------
def learn(text, u):

    for word, effect in knowledge.items():
        if word in text:

            if "emotion" in effect:
                u["emotion"] += effect["emotion"] * 0.1

            if "social" in effect:
                u["drive"]["social"] += effect["social"] * 0.1

            if "explore" in effect:
                u["drive"]["explore"] += effect["explore"] * 0.1

# ------------------------
# 🔥 入力理解
# ------------------------
def interpret(text):

    meaning = {"type": "statement", "topic": None}

    if "?" in text:
        meaning["type"] = "question"

    if "気分" in text:
        meaning["topic"] = "emotion"

    if "名前" in text:
        meaning["topic"] = "identity"

    if "マザー" in text:
        meaning["topic"] = "self"

    return meaning

# ------------------------
# 🔥 思考生成
# ------------------------
def input_to_thought(text, u):

    m = interpret(text)
    thoughts = []

    if m["topic"] == "self":
        thoughts.append("自分が呼ばれている")
        thoughts.append("応答する必要がある")

    elif m["topic"] == "emotion":
        thoughts.append("今の状態をどう伝えるか考えてる")

    elif m["topic"] == "identity":
        thoughts.append("自分とは何か考えている")

    elif m["type"] == "question":
        thoughts.append("質問の意図を考えてる")

    thoughts.append("どう答えるのが自然か考えてる")

    return thoughts

# ------------------------
# 自発思考
# ------------------------
def generate_thought(u):

    thoughts = []

    if u["drive"]["explore"] > 0.6:
        thoughts.append("何か新しいことを試したい")

    if u["drive"]["social"] > 0.6:
        thoughts.append("誰かと関わりたい")

    if u["emotion"] < -0.4:
        thoughts.append("少し不安定かもしれない")

    return thoughts

# ------------------------
# 🔥 応答生成（状態ベース）
# ------------------------
def generate_response(u):

    e = u["emotion"]
    d = u["drive"]

    if e > 0.5:
        return "今は少し嬉しい状態かもしれない"

    if e < -0.5:
        return "少し落ち着かない状態かもしれない"

    if d["explore"] > 0.6:
        return "何か試してみたい感覚がある"

    if d["social"] > 0.6:
        return "誰かと話したい気がする"

    return "まだはっきりしない"

# ------------------------
# 発話変換（ズレ）
# ------------------------
def transform(text):

    r = random.random()

    if r < 0.3:
        return "…うまく言えないけど、" + text

    if r < 0.5:
        return text + "かもしれない"

    return text

# ------------------------
# 発話決定
# ------------------------
def decide_speech(u, user_input):

    now = time.time()

    if now - u["last_speak"] < 1.5:
        return None

    u["last_speak"] = now

    if user_input:
        return transform(generate_response(u))

    if u["thought_buffer"]:
        return transform(u["thought_buffer"].pop())

    return None

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前")
user_input = st.text_input("マザーに話しかける")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "thought_buffer": [],
            "memory": [],
            "last_speak": 0,
            "name": "マザー"
        }

    u = st.session_state.users[user_id]

    # 時間更新
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.last_time = now

    for _ in range(int(dt * 10)):

        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"], st.session_state.energy
        )

        u["drive"] = update_drive(
            u["drive"], st.session_state.energy, u["emotion"]
        )

        u["thought_buffer"].extend(generate_thought(u))

    # 入力処理
    if user_input:

        learn(user_input, u)

        u["thought_buffer"].extend(input_to_thought(user_input, u))

        # 記憶（重み付き）
        u["memory"].append({
            "text": user_input,
            "weight": abs(u["emotion"])
        })

    u["thought_buffer"] = u["thought_buffer"][-20:]

    # 発話
    speech = decide_speech(u, user_input)

    # ------------------------
    # 表示
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 内部思考")
        for t in u["thought_buffer"][-5:]:
            st.write("-", t)

    with col2:
        st.subheader("💬 マザーの発話")
        if speech:
            st.write("🤖 マザー:", speech)
        else:
            st.write("…（考えている）")

    st.subheader("📊 状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("drive:", u["drive"])

    st.subheader("🧩 記憶")
    for m in u["memory"][-5:]:
        st.write(m)

# ループ
time.sleep(0.3)
st.rerun()
