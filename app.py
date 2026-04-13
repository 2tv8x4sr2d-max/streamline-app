import streamlit as st
import random
import math

st.title("🧠 成長するAI（言語収束版）")

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
    st.session_state.initialized = True

# ------------------------
# 基本関数
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
# 言語処理
# ------------------------
def compress_language(parts):
    return "、".join(parts[:2])

def clean_text(text):
    words = text.split("、")
    unique = []
    for w in words:
        if w not in unique:
            unique.append(w)
    return "、".join(unique)

# ------------------------
# 🔥 優先度付き検索
# ------------------------
def find_similar(x, lang_memory):
    best = None
    best_score = 999
    best_index = -1

    for i, (past_x, text, weight) in enumerate(lang_memory):
        diff = sum(abs(x[j]-past_x[j]) for j in range(len(x)))

        score = diff / (weight + 0.1)

        if score < best_score:
            best_score = score
            best = text
            best_index = i

    return best, best_index

# ------------------------
# 言語生成
# ------------------------
def generate_response(x, prev_x, U, emotion, relation, personality, user_input, lang_memory):
    valence, energy, stability, novelty = analyze_state(x, prev_x, U)

    parts = []

    if valence > 0.2:
        parts.append("楽しい")
    elif valence < -0.2:
        parts.append("違和感ある")

    if energy > 0.2:
        parts.append("ざわつく")

    if stability < 0.5:
        parts.append("まとまらない")

    if novelty > 0.1:
        parts.append("新しい感じ")

    if not parts:
        parts.append("よくわからない")

    base = compress_language(parts)
    base = clean_text(base)

    # 🔥 過去参照（1つだけ）
    past, index = find_similar(x, lang_memory)

    if past:
        base = f"{past}っぽい"

        # 🔥 使用強化
        px, pt, pw = lang_memory[index]
        lang_memory[index] = (px, pt, pw + 1.0)

    # 性格
    tone = {
        "friendly": "だね！",
        "cool": "だな",
        "dark": "…そうだな"
    }[personality]

    # 感情
    if emotion > 0.5:
        base += "、嬉しい"
    elif emotion < -0.5:
        base += "、少し嫌だ"

    # 関係
    if relation > 0.5:
        prefix = "君と話すと"
    elif relation < -0.5:
        prefix = "正直言うと"
    else:
        prefix = ""

    return f"{prefix}{base}{tone}", base

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
            "lang_memory": []
        }

    user_data = st.session_state.users[user_id]

    if user_input:
        st.session_state.prev_x = st.session_state.x[:]

        st.session_state.x = update_state(st.session_state.x, st.session_state.S, user_input)
        U = compute_U(st.session_state.x)

        user_data["emotion"] = update_emotion(user_data["emotion"], user_input)
        user_data["relation"] = update_relation(user_data["relation"], user_input)

        response, base = generate_response(
            st.session_state.x,
            st.session_state.prev_x,
            U,
            user_data["emotion"],
            user_data["relation"],
            st.session_state.personality,
            user_input,
            user_data["lang_memory"]
        )

        # 🔥 新規追加（重複防止）
        if base not in [t for _, t, _ in user_data["lang_memory"]]:
            user_data["lang_memory"].append((st.session_state.x[:], base, 1.0))

        # 🔥 忘却処理
        new_memory = []
        for px, pt, pw in user_data["lang_memory"]:
            pw *= 0.995
            if pw > 0.1:  # 消滅条件
                new_memory.append((px, pt, pw))
        user_data["lang_memory"] = new_memory[-50:]  # 上限

        st.write("🤖 AI:", response)

    st.subheader("あなたとの関係")
    st.write("感情:", round(user_data["emotion"], 3))
    st.write("関係:", round(user_data["relation"], 3))
    st.write("言語記憶:", len(user_data["lang_memory"]))

# ------------------------
# AI状態
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
