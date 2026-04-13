import streamlit as st
import random
import math

st.title("🧠 成長するAI（価値観＋自己他者モデル）")

# ------------------------
# 意味辞書
# ------------------------
word_dict = {
    "楽しい": {"valence": 0.8},
    "嬉しい": {"valence": 0.9},
    "嫌い": {"valence": -0.8},
    "悲しい": {"valence": -0.7},
    "話そう": {"social": 0.7},
    "一緒": {"social": 0.5},
    "試す": {"explore": 0.7},
}

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    st.session_state.energy = random.uniform(0.3, 0.7)
    st.session_state.users = {}
    st.session_state.initialized = True

# ------------------------
# 他者推定（EMA）
# ------------------------
def update_user_model(user_model, text):

    target = 0.0

    for word, effect in word_dict.items():
        if word in text and "valence" in effect:
            target += effect["valence"]

    # 🔥 EMA更新（重要）
    user_model["emotion"] = 0.8 * user_model["emotion"] + 0.2 * target

    return user_model

# ------------------------
# 内面更新
# ------------------------
def update_internal(e, energy):

    e += random.uniform(-0.05, 0.05)
    e += (energy - 0.5) * 0.1
    e *= 0.98

    energy += random.uniform(-0.05, 0.05)
    energy += e * 0.05

    return max(-1, min(1, e)), max(0, min(1, energy))

# ------------------------
# 欲求（ベクトル）
# ------------------------
def update_drive(drive, energy, emotion):

    drive["explore"] += energy * 0.08
    drive["social"] += emotion * 0.08

    # 葛藤
    drive["explore"] -= drive["social"] * 0.05
    drive["social"] -= drive["explore"] * 0.05

    # 時間減衰
    for k in drive:
        drive[k] *= 0.99

    # 制限
    for k in drive:
        drive[k] = max(0, min(1, drive[k]))

    return drive

# ------------------------
# 🔥 価値観（追加）
# ------------------------
def update_values(values, user_model):

    # 他者がポジティブならsocial上昇
    values["social"] += user_model["emotion"] * 0.05

    # ランダム揺れ
    values["explore"] += random.uniform(-0.02, 0.02)
    values["social"] += random.uniform(-0.02, 0.02)

    # 正規化
    for k in values:
        values[k] = max(0.1, min(1.0, values[k]))

    return values

# ------------------------
# 🔥 行動決定（重要）
# ------------------------
def compute_action_vector(drive, values):

    action = {}

    for k in drive:
        action[k] = drive[k] * values[k]

    return action

# ------------------------
# 表現
# ------------------------
def express_action(action):

    parts = []

    if action["explore"] > 0.3:
        parts.append("何か試したい")

    if action["social"] > 0.3:
        parts.append("話したい")

    return parts

# ------------------------
# 他者理解
# ------------------------
def infer_user(user_model):
    if user_model["emotion"] > 0.3:
        return "楽しそう"
    elif user_model["emotion"] < -0.3:
        return "少し嫌そう"
    else:
        return "まだ読みきれない"

# ------------------------
# 応答生成
# ------------------------
def generate_response(emotion, energy, action, user_model):

    base = ""

    # 自己認識
    if emotion > 0.3:
        base += "今いい感じ"
    elif emotion < -0.3:
        base += "少し不安定"
    else:
        base += "落ち着いてる"

    # 他者
    base += "、君は" + infer_user(user_model)

    # 行動
    parts = express_action(action)
    if parts:
        base += "、" + "、".join(parts)

    # 主導
    if random.random() < 0.3:
        base += "。どう思う？"

    return base

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
            "values": {"explore": 0.6, "social": 0.6},
            "user_model": {"emotion": 0.0}
        }

    u = st.session_state.users[user_id]

    if user_input:

        # 他者推定
        u["user_model"] = update_user_model(u["user_model"], user_input)

        # 内面
        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"],
            st.session_state.energy
        )

        # 欲求
        u["drive"] = update_drive(
            u["drive"],
            st.session_state.energy,
            u["emotion"]
        )

        # 価値観
        u["values"] = update_values(
            u["values"],
            u["user_model"]
        )

        # 行動
        action = compute_action_vector(u["drive"], u["values"])

        # 応答
        res = generate_response(
            u["emotion"],
            st.session_state.energy,
            action,
            u["user_model"]
        )

        st.write("🤖 AI:", res)

    # 可視化
    st.subheader("内部状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("energy:", round(st.session_state.energy, 3))

    st.subheader("欲求")
    st.write(u["drive"])

    st.subheader("価値観")
    st.write(u["values"])

    st.subheader("他者モデル")
    st.write(u["user_model"])
