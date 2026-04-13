import streamlit as st

st.title("初めてのアプリ")
st.write("ここから始まる")

import random
import math

st.title("🧠 成長するAIプロトタイプ")

 N = 20
# 初期化
if "x" not in st.session_state:
    st.session_state.x = [random.uniform(-0.5, 0.5) for _ in range(N)]
    st.session_state.S = [random.random() for _ in range(N)]
    st.session_state.memory = []
    st.session_state.emotion = 0.0
    st.session_state.relation = 0.0
    st.session_state.personality = random.choice(["friendly", "cool", "dark"])

# 関数
def update_state(x, S, user_input):
    influence = sum(ord(c) for c in user_input) % 100 / 100.0
    return [math.tanh(x[i] + influence * S[i] + random.uniform(-0.05, 0.05)) for i in range(len(x))]

def compute_U(x):
    mean = sum(x)/len(x)
    var = sum((xi - mean)**2 for xi in x)/len(x)
    return 1 / (1 + var)

def update_emotion(e, text):
    if "好き" in text or "いい" in text:
        e += 0.2
    elif "嫌い" in text or "うざ" in text:
        e -= 0.3
    else:
        e *= 0.95
    return max(-1, min(1, e))

def update_relation(r, text):
    if "ありがとう" in text:
        r += 0.2
    elif "バカ" in text:
        r -= 0.3
    return max(-1, min(1, r))

def generate_response(x, U, emotion, relation, personality, user_input):
    mood = sum(x)/len(x)

    if U < 0.4:
        base = "ちょっと混乱してる"
    elif mood > 0.2:
        base = "いい感じ"
    elif mood < -0.2:
        base = "少し違和感ある"
    else:
        base = "普通かな"

    if personality == "friendly":
        tone = "だね！"
    elif personality == "cool":
        tone = "だな"
    else:
        tone = "…そうだな"

    if emotion > 0.5:
        base += "、嬉しい"
    elif emotion < -0.5:
        base += "、ちょっと嫌だ"

    if relation > 0.5:
        prefix = "君と話すと"
    elif relation < -0.5:
        prefix = "正直言うと"
    else:
        prefix = ""

    return f"{prefix}{user_input}って言われて、{base}{tone}"

# UI
user_input = st.text_input("話しかけてみて")

if user_input:
    st.session_state.memory.append(user_input)

    st.session_state.x = update_state(st.session_state.x, st.session_state.S, user_input)
    U = compute_U(st.session_state.x)

    st.session_state.emotion = update_emotion(st.session_state.emotion, user_input)
    st.session_state.relation = update_relation(st.session_state.relation, user_input)

    response = generate_response(
        st.session_state.x,
        U,
        st.session_state.emotion,
        st.session_state.relation,
        st.session_state.personality,
        user_input
    )

    st.write("🤖 AI:", response)

# 可視化（超重要）
st.subheader("内部状態")

st.write("安定度 U:", round(compute_U(st.session_state.x), 3))
st.write("感情:", round(st.session_state.emotion, 3))
st.write("関係:", round(st.session_state.relation, 3))
st.write("性格:", st.session_state.personality)

st.subheader("記憶")
st.write(st.session_state.memory[-5:])
