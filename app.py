import streamlit as st
import random
import math

st.title("🧠 成長するAI（内面駆動版）")

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    N = 20
    st.session_state.x = [random.uniform(-0.5, 0.5) for _ in range(N)]
    st.session_state.prev_x = st.session_state.x[:]
    st.session_state.S = [random.random() for _ in range(N)]
    st.session_state.personality = random.choice(["friendly", "cool", "dark"])
    st.session_state.users = {}

    # 🔥 内面状態
    st.session_state.energy = random.uniform(0.3, 0.7)

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

def analyze_state(x, prev_x, U):
    mean = sum(x)/len(x)
    var = sum((xi - mean)**2 for xi in x)/len(x)
    diff = sum(abs(x[i]-prev_x[i]) for i in range(len(x))) / len(x)
    return mean, var, U, diff

# ------------------------
# 🔥 内面更新（超重要）
# ------------------------
def update_internal(e, energy, text):

    # 外部影響
    if "好き" in text or "いい" in text:
        e += 0.2
    elif "嫌い" in text or "うざ" in text:
        e -= 0.3

    # 🔥 内発ノイズ
    e += random.uniform(-0.05, 0.05)

    # 🔥 エネルギー連動
    e += (energy - 0.5) * 0.1

    # 減衰
    e *= 0.98

    # baseline（停止防止）
    if abs(e) < 0.03:
        e += random.uniform(-0.1, 0.1)

    # ------------------------
    # エネルギー更新
    # ------------------------
    energy += random.uniform(-0.05, 0.05)

    # 感情と連動
    energy += e * 0.05

    # 制限
    energy = max(0.0, min(1.0, energy))

    return max(-1, min(1, e)), energy

# ------------------------
# 言語生成
# ------------------------
def generate_response(x, prev_x, U, emotion, energy, personality):

    valence, _, _, novelty = analyze_state(x, prev_x, U)

    parts = []

    if valence > 0.2:
        parts.append("楽しい")
    elif valence < -0.2:
        parts.append("違和感ある")

    if energy > 0.6:
        parts.append("動きたい")
    elif energy < 0.3:
        parts.append("少しだるい")

    if novelty > 0.1:
        parts.append("新しい感じ")

    if not parts:
        parts.append("よくわからない")

    base = "、".join(parts[:2])

    # 性格
    tone = {
        "friendly": "だね！",
        "cool": "だな",
        "dark": "…そうだな"
    }[personality]

    # 感情反映
    if emotion > 0.5:
        base += "、ちょっと嬉しい"
    elif emotion < -0.5:
        base += "、少し嫌だ"

    return base + tone

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前（ID）")
user_input = st.text_input("話しかけてみて")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0
        }

    user_data = st.session_state.users[user_id]

    if user_input:
        st.session_state.prev_x = st.session_state.x[:]

        st.session_state.x = update_state(
            st.session_state.x,
            st.session_state.S,
            user_input
        )

        U = compute_U(st.session_state.x)

        # 🔥 内面更新
        user_data["emotion"], st.session_state.energy = update_internal(
            user_data["emotion"],
            st.session_state.energy,
            user_input
        )

        response = generate_response(
            st.session_state.x,
            st.session_state.prev_x,
            U,
            user_data["emotion"],
            st.session_state.energy,
            st.session_state.personality
        )

        st.write("🤖 AI:", response)

    st.subheader("あなたとの関係")
    st.write("感情:", round(user_data["emotion"], 3))

# ------------------------
# 内部状態
# ------------------------
st.subheader("AIの内部状態")

U_now = compute_U(st.session_state.x)
valence, _, _, novelty = analyze_state(
    st.session_state.x,
    st.session_state.prev_x,
    U_now
)

st.write("安定度 U:", round(U_now, 3))
st.write("valence:", round(valence, 3))
st.write("energy:", round(st.session_state.energy, 3))
st.write("novelty:", round(novelty, 3))
st.write("性格:", st.session_state.personality)
