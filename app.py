import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI（思考 / 発話 分離＋遅延モデル）")

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:

    st.session_state.energy = random.uniform(0.4, 0.6)
    st.session_state.users = {}
    st.session_state.last_time = time.time()

    st.session_state.initialized = True

# ------------------------
# 内面
# ------------------------
def update_internal(e, energy):

    e += random.uniform(-0.03, 0.03)
    e += (energy - 0.5) * 0.1
    e *= 0.98

    energy += random.uniform(-0.03, 0.03)
    energy += e * 0.05

    return max(-1, min(1, e)), max(0, min(1, energy))

# ------------------------
# 欲求
# ------------------------
def update_drive(drive, energy, emotion):

    drive["explore"] += 0.02 + energy * 0.05
    drive["social"] += 0.01 + emotion * 0.05

    drive["explore"] -= drive["social"] * 0.03
    drive["social"] -= drive["explore"] * 0.03

    for k in drive:
        drive[k] *= 0.998
        drive[k] = max(0, min(1, drive[k]))

    drive["explore"] = max(0.2, drive["explore"])

    return drive

# ------------------------
# 内部行動（思考）
# ------------------------
def internal_action(drive):

    actions = []

    if drive["explore"] > 0.5:
        actions.append("新しいことを試したい")

    if drive["social"] > 0.5:
        actions.append("誰かと話したい")

    return actions

# ------------------------
# 行動結果
# ------------------------
def simulate_outcome(action):

    if "試したい" in action:
        return "成功" if random.random() < 0.5 else "失敗"

    if "話したい" in action:
        return "反応がある気がする"

    return "変化なし"

# ------------------------
# 思考生成
# ------------------------
def generate_thought(u):

    thoughts = []

    actions = internal_action(u["drive"])

    for act in actions:
        result = simulate_outcome(act)
        thoughts.append(f"{act} → {result}")

    if u["emotion"] < -0.5:
        thoughts.append("なんかうまくいかない")

    return thoughts

# ------------------------
# 🔥 発話フィルタ（ズレ含む）
# ------------------------
def transform_speech(thought):

    if random.random() < 0.3:
        return "…うまく言えないけど、" + thought

    if random.random() < 0.2:
        return thought + "…いや違うかも"

    if random.random() < 0.2:
        return "別に大したことじゃないけど、" + thought

    return thought

# ------------------------
# 🔥 発話決定
# ------------------------
def decide_speech(u, user_input):

    now = time.time()

    # 応答優先
    if user_input:
        return "それについて考えてる：" + user_input

    # クールダウン
    if now - u["last_speak"] < 2.0:
        return None

    prob = u["drive"]["social"]

    if random.random() < prob and u["thought_buffer"]:

        u["last_speak"] = now

        thought = u["thought_buffer"].pop()

        return transform_speech(thought)

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

    # ------------------------
    # 時間進行
    # ------------------------
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.last_time = now

    ticks = int(dt * 15)

    for _ in range(max(1, ticks)):

        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"], st.session_state.energy
        )

        u["drive"] = update_drive(
            u["drive"], st.session_state.energy, u["emotion"]
        )

        thoughts = generate_thought(u)

        u["thought_buffer"].extend(thoughts)
        u["thought_buffer"] = u["thought_buffer"][-20:]

    # ------------------------
    # 発話
    # ------------------------
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

# ------------------------
# ループ
# ------------------------
time.sleep(0.3)
st.rerun()
