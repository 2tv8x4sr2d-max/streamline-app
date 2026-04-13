import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI（思考 / 発話 分離モデル）")

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:

    st.session_state.energy = random.uniform(0.4, 0.6)
    st.session_state.users = {}
    st.session_state.last_time = time.time()

    st.session_state.initialized = True

# ------------------------
# 内面更新
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
# 🔥 内部行動（思考）
# ------------------------
def internal_action(drive):

    actions = []

    if drive["explore"] > 0.5:
        actions.append("新しい考えを試す")

    if drive["social"] > 0.5:
        actions.append("誰かに問いを投げる")

    return actions

# ------------------------
# 🔥 行動結果（仮想）
# ------------------------
def simulate_outcome(action):

    if "試す" in action:
        success = random.random() < 0.5
        return "成功した" if success else "うまくいかなかった"

    if "問い" in action:
        return "反応がある気がする"

    return "変化なし"

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
# 🔥 内部思考生成
# ------------------------
def generate_thought(u):

    thoughts = []

    actions = internal_action(u["drive"])

    for act in actions:
        result = simulate_outcome(act)

        # 記憶として保存
        u["memory"] = store_memory(u["memory"], act + " → " + result, u["emotion"])

        thoughts.append(act + "（" + result + "）")

    # 感情ベース思考
    if u["emotion"] < -0.5:
        thoughts.append("なんかうまくいかない")

    if u["drive"]["explore"] > 0.6:
        thoughts.append("もっと試したい")

    return thoughts

# ------------------------
# 🔥 発話フィルタ
# ------------------------
def select_speech(thoughts, drive):

    if not thoughts:
        return None

    # social高いと発話しやすい
    if drive["social"] > 0.5:
        return random.choice(thoughts)

    # 低いとランダム
    if random.random() < 0.2:
        return random.choice(thoughts)

    return None

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
            "memory": [],
        }

    u = st.session_state.users[user_id]

    # ------------------------
    # 時間進行
    # ------------------------
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.last_time = now

    ticks = int(dt * 15)

    all_thoughts = []

    for _ in range(max(1, ticks)):

        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"], st.session_state.energy
        )

        u["drive"] = update_drive(
            u["drive"], st.session_state.energy, u["emotion"]
        )

        thoughts = generate_thought(u)
        all_thoughts.extend(thoughts)

    # ------------------------
    # 発話
    # ------------------------
    speech = select_speech(all_thoughts, u["drive"])

    # ------------------------
    # 表示
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 内部思考")
        for t in all_thoughts[-5:]:
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

    st.subheader("🧠 記憶")
    for m in u["memory"]:
        st.write(m)

# ------------------------
# ループ
# ------------------------
time.sleep(0.3)
st.rerun()


