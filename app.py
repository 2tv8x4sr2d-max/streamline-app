import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI（理解→思考→発話モデル）")

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
# 欲求
# ------------------------
def update_drive(drive, energy, emotion):

    drive["explore"] += 0.01 + energy * 0.05
    drive["social"] += 0.01 + emotion * 0.05

    # 相互抑制
    drive["explore"] -= drive["social"] * 0.02
    drive["social"] -= drive["explore"] * 0.02

    for k in drive:
        drive[k] *= 0.995
        drive[k] = max(0, min(1, drive[k]))

    # 探索は最低維持（止まらないため）
    drive["explore"] = max(0.25, drive["explore"])

    return drive

# ------------------------
# 🔥 入力理解
# ------------------------
def interpret_input(text):

    meaning = {"type": "unknown", "topic": None}

    if "?" in text:
        meaning["type"] = "question"

    if "気分" in text:
        meaning["topic"] = "emotion"

    if "名前" in text:
        meaning["topic"] = "identity"

    return meaning

# ------------------------
# 🔥 思考生成（入力→内面）
# ------------------------
def input_to_thought(text, u):

    m = interpret_input(text)
    thoughts = []

    if m["type"] == "question":

        if m["topic"] == "emotion":
            thoughts.append("自分の状態をどう説明するか考えてる")

        elif m["topic"] == "identity":
            thoughts.append("自分とは何か考えてる")

        else:
            thoughts.append("質問の意図を探ってる")

    # 入力そのままは禁止
    thoughts.append("どう答えるのが自然か考えてる")

    return thoughts

# ------------------------
# 🔥 内部思考（自発）
# ------------------------
def generate_thought(u):

    thoughts = []

    if u["drive"]["explore"] > 0.6:
        thoughts.append("何か試したい")

    if u["drive"]["social"] > 0.6:
        thoughts.append("誰かと関わりたい")

    if u["emotion"] < -0.4:
        thoughts.append("少しうまくいってない気がする")

    return thoughts

# ------------------------
# 🔥 発話生成（状態ベース）
# ------------------------
def generate_response(u):

    e = u["emotion"]
    d = u["drive"]

    if e > 0.4:
        return "少し気分がいいかもしれない"

    if e < -0.4:
        return "あまり良くない感じがある"

    if d["explore"] > 0.6:
        return "何か試してみたい気がする"

    if d["social"] > 0.6:
        return "誰かと話したい感じがある"

    return "まだはっきりしない"

# ------------------------
# 🔥 発話フィルタ（ズレ）
# ------------------------
def transform_speech(text):

    r = random.random()

    if r < 0.25:
        return "…うまく言えないけど、" + text

    if r < 0.45:
        return text + "…かもしれない"

    if r < 0.6:
        return "別に大したことじゃないけど、" + text

    return text

# ------------------------
# 🔥 発話決定
# ------------------------
def decide_speech(u, user_input):

    now = time.time()

    if now - u["last_speak"] < 1.5:
        return None

    u["last_speak"] = now

    # 入力がある場合 → 状態から応答
    if user_input:
        return transform_speech(generate_response(u))

    # 入力なし → 思考から
    if u["thought_buffer"]:
        t = u["thought_buffer"].pop()
        return transform_speech(t)

    return None

# ------------------------
# UI
# ------------------------
user_id = st.text_input("名前")
user_input = st.text_input("入力")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "thought_buffer": [],
            "last_speak": 0
        }

    u = st.session_state.users[user_id]

    # 時間進行
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.last_time = now

    ticks = int(dt * 10)

    for _ in range(max(1, ticks)):

        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"], st.session_state.energy
        )

        u["drive"] = update_drive(
            u["drive"], st.session_state.energy, u["emotion"]
        )

        # 自発思考
        thoughts = generate_thought(u)
        u["thought_buffer"].extend(thoughts)

    # 入力処理
    if user_input:
        u["thought_buffer"].extend(input_to_thought(user_input, u))

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
        st.subheader("💬 発話")
        if speech:
            st.write("🤖", speech)
        else:
            st.write("…（考えている）")

    st.subheader("📊 状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("energy:", round(st.session_state.energy, 3))
    st.write("drive:", u["drive"])

# ループ
time.sleep(0.3)
st.rerun()
