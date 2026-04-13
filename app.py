import streamlit as st
import random
import time

st.title("🧠 成長するAI（時間・思考・主導 完全版）")

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:

    st.session_state.energy = random.uniform(0.4, 0.6)
    st.session_state.users = {}
    st.session_state.last_time = time.time()

    st.session_state.initialized = True

# ------------------------
# 意味辞書
# ------------------------
word_dict = {
    "楽しい": 0.8,
    "嬉しい": 0.9,
    "嫌い": -0.8,
    "悲しい": -0.7,
}

# ------------------------
# 基本更新
# ------------------------
def update_internal(e, energy):
    e += random.uniform(-0.03, 0.03)
    e += (energy - 0.5) * 0.1
    e *= 0.98

    energy += random.uniform(-0.03, 0.03)
    energy += e * 0.05

    return max(-1, min(1, e)), max(0, min(1, energy))

def update_drive(drive, energy, emotion):
    drive["explore"] += energy * 0.06
    drive["social"] += emotion * 0.06

    drive["explore"] -= drive["social"] * 0.04
    drive["social"] -= drive["explore"] * 0.04

    for k in drive:
        drive[k] *= 0.995
        drive[k] = max(0, min(1, drive[k]))

    return drive

# ------------------------
# 思考
# ------------------------
def spontaneous_thought(e, drive, story):

    thoughts = []

    if e > 0.5:
        thoughts.append("この状態続くかな？")

    if drive["explore"] > 0.6:
        thoughts.append("他に何ができる？")

    if drive["social"] > 0.6:
        thoughts.append("誰かと関わりたい")

    if story:
        thoughts.append("自分って何なんだろう")

    return random.choice(thoughts) if thoughts else None

# ------------------------
# 発話判断
# ------------------------
def should_speak(drive, energy):

    # 社交欲 or エネルギー高いと喋る
    if drive["social"] > 0.7:
        return True

    if energy > 0.75 and random.random() < 0.3:
        return True

    return False

# ------------------------
# UI
# ------------------------
user_id = st.text_input("名前")
user_input = st.text_input("入力（空でもOK）")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "story": ""
        }

    u = st.session_state.users[user_id]

    # ------------------------
    # 🔥 時間進行
    # ------------------------
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.last_time = now

    ticks = int(dt * 3)  # 時間スケール調整

    for _ in range(max(1, ticks)):

        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"], st.session_state.energy
        )

        u["drive"] = update_drive(
            u["drive"], st.session_state.energy, u["emotion"]
        )

    # ------------------------
    # 入力処理
    # ------------------------
    if user_input:

        if "楽しい" in user_input:
            u["emotion"] += 0.2
        if "嫌い" in user_input:
            u["emotion"] -= 0.3

    # ------------------------
    # 思考
    # ------------------------
    thought = spontaneous_thought(
        u["emotion"], u["drive"], u["story"]
    )

    # ------------------------
    # 発話
    # ------------------------
    if should_speak(u["drive"], st.session_state.energy):

        if thought:
            st.write("🤖 AI:", thought)
        else:
            st.write("🤖 AI:", "…何かしたい")

    else:
        st.write("🤖 AI（内部思考中）:", thought if thought else "…")

    # ------------------------
    # 可視化
    # ------------------------
    st.subheader("状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("energy:", round(st.session_state.energy, 3))
    st.write("drive:", u["drive"])

# ------------------------
# 🔥 自動ループ
# ------------------------
time.sleep(1)
st.rerun()
