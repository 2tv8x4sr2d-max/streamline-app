import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI（観察UI 完全版）")

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

    # 自然回復
    drive["explore"] += 0.02
    drive["social"] += 0.01

    drive["explore"] += energy * 0.05
    drive["social"] += emotion * 0.05

    # 葛藤
    drive["explore"] -= drive["social"] * 0.03
    drive["social"] -= drive["explore"] * 0.03

    # 減衰
    for k in drive:
        drive[k] *= 0.998

    # 最低保証
    drive["explore"] = max(0.2, drive["explore"])

    # clamp
    for k in drive:
        drive[k] = max(0, min(1, drive[k]))

    return drive

# ------------------------
# 他者推定
# ------------------------
def update_user_model(user_model, text):

    target = 0
    for w, v in word_dict.items():
        if w in text:
            target += v

    user_model["emotion"] = 0.8 * user_model["emotion"] + 0.2 * target
    return user_model

# ------------------------
# 記憶
# ------------------------
def store_memory(memory, text, emotion):

    memory.append({
        "text": text,
        "value": round(abs(emotion) + random.uniform(0, 0.2), 3),
        "emotion": round(emotion, 3)
    })

    return sorted(memory, key=lambda x: x["value"], reverse=True)[:10]

# ------------------------
# 思考
# ------------------------
def spontaneous_thought(e, drive, story):

    thoughts = []

    if drive["explore"] > 0.4:
        thoughts.append("何か試したい")

    if drive["social"] > 0.4:
        thoughts.append("誰かと話したい")

    if e < -0.5:
        thoughts.append("うまくいかない")

    if story:
        thoughts.append("自分って何だろう")

    return random.choice(thoughts) if thoughts else "…"

# ------------------------
# 発話判断
# ------------------------
def should_speak(drive, energy):
    if drive["social"] > 0.6:
        return True
    if random.random() < 0.2:
        return True
    return False

# ------------------------
# UI入力
# ------------------------
user_id = st.text_input("名前")
user_input = st.text_input("入力（空でもOK）")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "memory": [],
            "user_model": {"emotion": 0.0},
            "story": ""
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

    # ------------------------
    # 入力処理
    # ------------------------
    if user_input:
        u["user_model"] = update_user_model(u["user_model"], user_input)
        u["memory"] = store_memory(u["memory"], user_input, u["emotion"])

    # ------------------------
    # 思考
    # ------------------------
    thought = spontaneous_thought(
        u["emotion"], u["drive"], u["story"]
    )

    # ------------------------
    # 表示レイアウト
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 AIの状態")

        if should_speak(u["drive"], st.session_state.energy):
            st.write("🤖 発話:", thought)
        else:
            st.write("🤖 内部思考:", thought)

        st.write("emotion:", round(u["emotion"], 3))
        st.write("energy:", round(st.session_state.energy, 3))

        st.subheader("🔥 欲求")
        st.write(u["drive"])

        st.subheader("👤 他者モデル")
        st.write(u["user_model"])

    with col2:
        st.subheader("🧠 記憶（重要度順）")
        for m in u["memory"]:
            st.write(m)

        st.subheader("🧩 ストーリー")
        st.write(u["story"])

# ------------------------
# ループ
# ------------------------
time.sleep(0.3)
st.rerun()
