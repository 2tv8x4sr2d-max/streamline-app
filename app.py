import streamlit as st
import random
import math

st.title("🧠 成長するAI（自己＋他者＋主導）")

# ------------------------
# 意味辞書
# ------------------------
word_dict = {
    "楽しい": {"valence": 0.8},
    "嬉しい": {"valence": 0.9},
    "嫌い": {"valence": -0.8},
    "悲しい": {"valence": -0.7},
    "動きたい": {"energy": 0.8},
    "疲れた": {"energy": -0.5},
    "話そう": {"social": 0.7},
    "一緒": {"social": 0.5},
}

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    N = 20
    st.session_state.x = [random.uniform(-0.5, 0.5) for _ in range(N)]
    st.session_state.prev_x = st.session_state.x[:]
    st.session_state.energy = random.uniform(0.3, 0.7)

    st.session_state.self_name = "AI"
    st.session_state.users = {}
    st.session_state.initialized = True

# ------------------------
# 状態更新
# ------------------------
def update_state(x, text):
    influence = sum(ord(c) for c in text) % 100 / 100.0
    return [math.tanh(x[i] + influence + random.uniform(-0.05, 0.05)) for i in range(len(x))]

def analyze_state(x, prev_x):
    mean = sum(x)/len(x)
    diff = sum(abs(x[i]-prev_x[i]) for i in range(len(x))) / len(x)
    return mean, diff

# ------------------------
# 入力理解
# ------------------------
def interpret_input(text, emotion, energy, drive, user_model):

    for word, effect in word_dict.items():
        if word in text:
            if "valence" in effect:
                emotion += effect["valence"] * 0.1
                user_model["emotion"] += effect["valence"] * 0.2
            if "energy" in effect:
                energy += effect["energy"] * 0.1
            if "social" in effect:
                drive["social"] += effect["social"] * 0.1

    return emotion, energy, drive, user_model

# ------------------------
# 内面更新
# ------------------------
def update_internal(e, energy):
    e += random.uniform(-0.05, 0.05)
    e += (energy - 0.5) * 0.1
    e *= 0.98

    if abs(e) < 0.03:
        e += random.uniform(-0.1, 0.1)

    energy += random.uniform(-0.05, 0.05)
    energy += e * 0.05

    return max(-1, min(1, e)), max(0, min(1, energy))

# ------------------------
# 欲求
# ------------------------
def update_drive(drive, energy, emotion):
    drive["explore"] += energy * 0.1 + random.uniform(-0.05, 0.05)
    drive["social"] += emotion * 0.1 + random.uniform(-0.05, 0.05)

    for k in drive:
        drive[k] = max(0, min(1, drive[k]))

    return drive

def decide_action(drive):
    return max(drive, key=drive.get)

# ------------------------
# 名前理解
# ------------------------
def extract_name(text):
    if "名前は" in text:
        return text.split("名前は")[-1].strip()
    return None

# ------------------------
# 🔥 自己認識
# ------------------------
def self_reflection(emotion, energy):
    if emotion > 0.5:
        return "今ちょっといい気分"
    elif emotion < -0.5:
        return "少し不安定"
    elif energy > 0.6:
        return "動きたい状態"
    else:
        return "落ち着いてる"

# ------------------------
# 🔥 他者推定
# ------------------------
def infer_user_state(user_model):
    if user_model["emotion"] > 0.5:
        return "楽しそう"
    elif user_model["emotion"] < -0.5:
        return "少し嫌そう"
    else:
        return "まだよくわからない"

# ------------------------
# 🔥 会話生成（主導あり）
# ------------------------
def generate_response(x, prev_x, emotion, energy, drive, user_model):

    valence, novelty = analyze_state(x, prev_x)

    base = ""

    # 自己認識
    base += self_reflection(emotion, energy)

    # 他者認識
    base += "、君は" + infer_user_state(user_model)

    # 行動
    action = decide_action(drive)

    if action == "explore":
        base += "、何か試したい"
    elif action == "social":
        base += "、もっと話したい"

    # 🔥 主導（ランダム）
    if random.random() < 0.3:
        prompts = [
            "何してる？",
            "どう思う？",
            "今どんな気分？"
        ]
        base += "。" + random.choice(prompts)

    return base

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前（ID）")
user_input = st.text_input("話しかけてみて")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "memory": [],
            "user_model": {"emotion": 0.0}
        }

    user_data = st.session_state.users[user_id]

    if user_input:

        user_data["memory"].append(user_input)
        user_data["memory"] = user_data["memory"][-3:]

        name = extract_name(user_input)
        if name:
            st.session_state.self_name = name

        st.session_state.prev_x = st.session_state.x[:]
        st.session_state.x = update_state(st.session_state.x, user_input)

        user_data["emotion"], st.session_state.energy, user_data["drive"], user_data["user_model"] = interpret_input(
            user_input,
            user_data["emotion"],
            st.session_state.energy,
            user_data["drive"],
            user_data["user_model"]
        )

        user_data["emotion"], st.session_state.energy = update_internal(
            user_data["emotion"],
            st.session_state.energy
        )

        user_data["drive"] = update_drive(
            user_data["drive"],
            st.session_state.energy,
            user_data["emotion"]
        )

        response = generate_response(
            st.session_state.x,
            st.session_state.prev_x,
            user_data["emotion"],
            st.session_state.energy,
            user_data["drive"],
            user_data["user_model"]
        )

        st.write("🤖", st.session_state.self_name + ":", response)

    # 可視化
    st.subheader("自己状態")
    st.write("emotion:", round(user_data["emotion"], 3))
    st.write("energy:", round(st.session_state.energy, 3))

    st.subheader("他者推定")
    st.write(user_data["user_model"])

    st.subheader("欲求")
    st.write(user_data["drive"])

    st.subheader("文脈")
    st.write(user_data["memory"])
