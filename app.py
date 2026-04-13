import streamlit as st
import random
import math

st.title("🧠 成長するAI（意志＋可視化版）")

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    N = 20
    st.session_state.x = [random.uniform(-0.5, 0.5) for _ in range(N)]
    st.session_state.prev_x = st.session_state.x[:]
    st.session_state.S = [random.random() for _ in range(N)]
    st.session_state.personality = random.choice(["friendly", "cool", "dark"])
    st.session_state.energy = random.uniform(0.3, 0.7)

    st.session_state.users = {}
    st.session_state.initialized = True

# ------------------------
# 状態更新
# ------------------------
def update_state(x, S, user_input):
    influence = sum(ord(c) for c in user_input) % 100 / 100.0
    return [
        math.tanh(x[i] + influence * S[i] + random.uniform(-0.05, 0.05))
        for i in range(len(x))
    ]

def compute_U(x):
    mean = sum(x)/len(x)
    var = sum((xi - mean)**2 for xi in x)/len(x)
    return 1 / (1 + var)

def analyze_state(x, prev_x):
    mean = sum(x)/len(x)
    var = sum((xi - mean)**2 for xi in x)/len(x)
    diff = sum(abs(x[i]-prev_x[i]) for i in range(len(x))) / len(x)
    return mean, var, diff

# ------------------------
# 内面更新
# ------------------------
def update_internal(e, energy, text):

    if "好き" in text or "いい" in text:
        e += 0.2
    elif "嫌い" in text or "うざ" in text:
        e -= 0.3

    e += random.uniform(-0.05, 0.05)
    e += (energy - 0.5) * 0.1
    e *= 0.98

    if abs(e) < 0.03:
        e += random.uniform(-0.1, 0.1)

    energy += random.uniform(-0.05, 0.05)
    energy += e * 0.05
    energy = max(0.0, min(1.0, energy))

    return max(-1, min(1, e)), energy

# ------------------------
# 関係更新
# ------------------------
def update_relation(r, text):
    if "ありがとう" in text:
        r += 0.2
    elif "バカ" in text:
        r -= 0.3
    else:
        r *= 0.99
    return max(-1, min(1, r))

# ------------------------
# 欲求（restなし）
# ------------------------
def update_drive(drive, energy, emotion):
    drive["explore"] += energy * 0.1 + random.uniform(-0.05, 0.05)
    drive["social"] += emotion * 0.1 + random.uniform(-0.05, 0.05)

    for k in drive:
        drive[k] = max(0.0, min(1.0, drive[k]))

    return drive

def decide_action(drive):
    return max(drive, key=drive.get)

# ------------------------
# 言語生成
# ------------------------
def generate_response(x, prev_x, emotion, energy, drive, personality):

    valence, _, novelty = analyze_state(x, prev_x)

    parts = []

    if valence > 0.2:
        parts.append("楽しい")
    elif valence < -0.2:
        parts.append("違和感ある")

    if energy > 0.6:
        parts.append("動きたい")
    elif energy < 0.3:
        parts.append("少し落ち着いてる")

    if novelty > 0.1:
        parts.append("新しい感じ")

    if not parts:
        parts.append("よくわからない")

    base = "、".join(parts[:2])

    # 行動反映
    action = decide_action(drive)

    if action == "explore":
        base += "、何か試したい"
    elif action == "social":
        base += "、もっと話したい"

    # 性格
    tone = {
        "friendly": "だね！",
        "cool": "だな",
        "dark": "…そうだな"
    }[personality]

    return base + tone, base

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前（ID）")
user_input = st.text_input("話しかけてみて")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "relation": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "lang_memory": []
        }

    user_data = st.session_state.users[user_id]

    if user_input:
        st.session_state.prev_x = st.session_state.x[:]

        st.session_state.x = update_state(
            st.session_state.x,
            st.session_state.S,
            user_input
        )

        user_data["emotion"], st.session_state.energy = update_internal(
            user_data["emotion"],
            st.session_state.energy,
            user_input
        )

        user_data["relation"] = update_relation(
            user_data["relation"],
            user_input
        )

        user_data["drive"] = update_drive(
            user_data["drive"],
            st.session_state.energy,
            user_data["emotion"]
        )

        response, base = generate_response(
            st.session_state.x,
            st.session_state.prev_x,
            user_data["emotion"],
            st.session_state.energy,
            user_data["drive"],
            st.session_state.personality
        )

        # 言語記憶（可視化しやすく）
        user_data["lang_memory"].append(base)
        user_data["lang_memory"] = user_data["lang_memory"][-10:]

        st.write("🤖 AI:", response)

    # ------------------------
    # 可視化
    # ------------------------
    st.subheader("あなたとの関係")
    st.write("感情:", round(user_data["emotion"], 3))
    st.write("関係:", round(user_data["relation"], 3))

    st.subheader("欲求")
    st.write(user_data["drive"])

    st.subheader("言語記憶")
    st.write(user_data["lang_memory"])

# ------------------------
# 内部状態
# ------------------------
st.subheader("AIの内部状態")

U_now = compute_U(st.session_state.x)
valence, _, novelty = analyze_state(
    st.session_state.x,
    st.session_state.prev_x
)

st.write("安定度 U:", round(U_now, 3))
st.write("valence:", round(valence, 3))
st.write("energy:", round(st.session_state.energy, 3))
st.write("novelty:", round(novelty, 3))
st.write("性格:", st.session_state.personality)
