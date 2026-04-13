import streamlit as st
import random
import math

st.title("🧠 成長するAI（個人依存版）")

# ------------------------
# 初期化
# ------------------------
if "x" not in st.session_state:
    N = 20
    st.session_state.x = [random.uniform(-0.5, 0.5) for _ in range(N)]
    st.session_state.prev_x = st.session_state.x[:]
    st.session_state.S = [random.random() for _ in range(N)]
    st.session_state.personality = random.choice(["friendly", "cool", "dark"])

    st.session_state.users = {}  # 🔥 ユーザー別管理

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

# ------------------------
# 状態分析
# ------------------------
def analyze_state(x, prev_x, U):
    mean = sum(x)/len(x)
    var = sum((xi - mean)**2 for xi in x)/len(x)
    diff = sum(abs(x[i]-prev_x[i]) for i in range(len(x))) / len(x)
    return mean, var, U, diff

# ------------------------
# 感情・関係
# ------------------------
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

# ------------------------
# 言語記憶
# ------------------------
def find_similar(x, lang_memory):
    best = None
    best_score = 999

    for past_x, text in lang_memory:
        diff = sum(abs(x[i]-past_x[i]) for i in range(len(x)))
        if diff < best_score:
            best_score = diff
            best = text

    return best, best_score

# ------------------------
# 言語生成
# ------------------------
def generate_response(x, prev_x, U, emotion, relation, personality, user_input, lang_memory):
    valence, energy, stability, novelty = analyze_state(x, prev_x, U)

    parts = []

    if valence > 0.2:
        parts.append("少し楽しい")
    elif valence < -0.2:
        parts.append("少し嫌な感じ")

    if energy > 0.2:
        parts.append("頭がざわついてる")

    if stability < 0.5:
        parts.append("うまくまとまらない")

    if novelty > 0.1:
        parts.append("新しい感じがする")

    if not parts:
        parts.append("まだよくわからない")

    base = "、".join(parts)

    # 🔥 個人ごとの言語記憶
    past, score = find_similar(x, lang_memory)
    if past and score < 5:
        base = f"{past}に近い感じがする"

    # 性格
    tone = {
        "friendly": "だね！",
        "cool": "だな",
        "dark": "…そうだな"
    }[personality]

    # 感情
    if emotion > 0.5:
        base += "、ちょっと嬉しい"
    elif emotion < -0.5:
        base += "、少し嫌だ"

    # 関係（ここが個人差）
    if relation > 0.5:
        prefix = "君と話してると"
    elif relation < -0.5:
        prefix = "正直言うと"
    else:
        prefix = ""

    return f"{prefix}{user_input}って言われて、{base}{tone}"

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
            "memory": [],
            "lang_memory": []
        }

    user_data = st.session_state.users[user_id]

    if user_input:
        st.session_state.prev_x = st.session_state.x[:]

        st.session_state.x = update_state(st.session_state.x, st.session_state.S, user_input)
        U = compute_U(st.session_state.x)

        user_data["emotion"] = update_emotion(user_data["emotion"], user_input)
        user_data["relation"] = update_relation(user_data["relation"], user_input)

        response = generate_response(
            st.session_state.x,
            st.session_state.prev_x,
            U,
            user_data["emotion"],
            user_data["relation"],
            st.session_state.personality,
            user_input,
            user_data["lang_memory"]
        )

        # 🔥 個人ごとに学習
        user_data["lang_memory"].append((st.session_state.x[:], response))
        user_data["memory"].append(user_input)

        st.write("🤖 AI:", response)

    # ------------------------
    # 可視化（個人別）
    # ------------------------
    st.subheader("あなたとの関係")

    st.write("感情:", round(user_data["emotion"], 3))
    st.write("関係:", round(user_data["relation"], 3))
    st.write("言語記憶数:", len(user_data["lang_memory"]))

# ------------------------
# 共通状態
# ------------------------
st.subheader("AIの内部状態")

U_now = compute_U(st.session_state.x)
valence, energy, stability, novelty = analyze_state(
    st.session_state.x,
    st.session_state.prev_x,
    U_now
)

st.write("安定度 U:", round(U_now, 3))
st.write("valence:", round(valence, 3))
st.write("energy:", round(energy, 3))
st.write("novelty:", round(novelty, 3))
st.write("性格:", st.session_state.personality)
