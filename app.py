import streamlit as st
import random

st.title("🧠 成長するAI（信念＋記憶＋価値観 完全版）")

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:

    st.session_state.energy = random.uniform(0.4, 0.6)

    st.session_state.users = {}

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
# 他者推定（安定化）
# ------------------------
def update_user_model(user_model, text):

    target = 0

    for w, v in word_dict.items():
        if w in text:
            target += v

    # EMA（重要）
    user_model["emotion"] = 0.8 * user_model["emotion"] + 0.2 * target

    return user_model

# ------------------------
# 内面
# ------------------------
def update_internal(e, energy):

    e += random.uniform(-0.04, 0.04)
    e += (energy - 0.5) * 0.1
    e *= 0.98

    energy += random.uniform(-0.04, 0.04)
    energy += e * 0.05

    return max(-1, min(1, e)), max(0, min(1, energy))

# ------------------------
# 欲求
# ------------------------
def update_drive(drive, energy, emotion):

    drive["explore"] += energy * 0.07
    drive["social"] += emotion * 0.07

    # 葛藤
    drive["explore"] -= drive["social"] * 0.05
    drive["social"] -= drive["explore"] * 0.05

    # 減衰
    for k in drive:
        drive[k] *= 0.99
        drive[k] = max(0, min(1, drive[k]))

    return drive

# ------------------------
# 価値観
# ------------------------
def update_values(values, user_model, priors):

    values["social"] += user_model["emotion"] * 0.04

    # priors影響
    values["explore"] += priors["curiosity"] * 0.02

    # 微揺れ
    values["explore"] += random.uniform(-0.01, 0.01)
    values["social"] += random.uniform(-0.01, 0.01)

    for k in values:
        values[k] = max(0.1, min(1.0, values[k]))

    return values

# ------------------------
# 信念
# ------------------------
def update_belief(belief, user_model):

    belief["trust"] += user_model["emotion"] * 0.05

    # 微揺れ
    belief["trust"] += random.uniform(-0.01, 0.01)

    belief["trust"] = max(0, min(1, belief["trust"]))

    return belief

# ------------------------
# 記憶
# ------------------------
def store_memory(memory, text, emotion):

    mem = {
        "text": text,
        "value": abs(emotion) + random.uniform(0, 0.2),
        "emotion": emotion
    }

    memory.append(mem)

    # 価値順に整理
    memory = sorted(memory, key=lambda x: x["value"], reverse=True)[:20]

    return memory

def memory_influence(memory):

    if not memory:
        return 0

    top = memory[:3]

    influence = sum(m["emotion"] * m["value"] for m in top)

    return influence * 0.1

# ------------------------
# 行動計算
# ------------------------
def compute_action(drive, values, belief, memory):

    mem_eff = memory_influence(memory)

    action = {}

    for k in drive:

        action[k] = drive[k] * values[k]

        # 信念
        if k == "social":
            action[k] *= belief["trust"]

        # 記憶
        action[k] += mem_eff

    return action

# ------------------------
# 表現
# ------------------------
def generate_response(e, energy, action, belief, user_model):

    base = ""

    # 自己
    if e > 0.3:
        base += "今いい感じ"
    elif e < -0.3:
        base += "少し不安定"
    else:
        base += "落ち着いてる"

    # 他者
    if user_model["emotion"] > 0.3:
        base += "、君は楽しそう"
    elif user_model["emotion"] < -0.3:
        base += "、少し警戒してる"
    else:
        base += "、まだ読みきれない"

    # 行動
    if action["explore"] > 0.3:
        base += "、試したい"
    if action["social"] > 0.3:
        base += "、話したい"

    # 信念
    if belief["trust"] > 0.7:
        base += "、人は信頼できる気がする"
    elif belief["trust"] < 0.3:
        base += "、少し疑ってる"

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
            "belief": {"trust": 0.5},
            "memory": [],
            "user_model": {"emotion": 0.0},
            "priors": {"curiosity": 0.6}
        }

    u = st.session_state.users[user_id]

    if user_input:

        # 他者
        u["user_model"] = update_user_model(u["user_model"], user_input)

        # 内面
        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"], st.session_state.energy
        )

        # 欲求
        u["drive"] = update_drive(
            u["drive"], st.session_state.energy, u["emotion"]
        )

        # 価値観
        u["values"] = update_values(
            u["values"], u["user_model"], u["priors"]
        )

        # 信念
        u["belief"] = update_belief(
            u["belief"], u["user_model"]
        )

        # 記憶
        u["memory"] = store_memory(
            u["memory"], user_input, u["emotion"]
        )

        # 行動
        action = compute_action(
            u["drive"], u["values"], u["belief"], u["memory"]
        )

        # 応答
        res = generate_response(
            u["emotion"], st.session_state.energy, action, u["belief"], u["user_model"]
        )

        st.write("🤖 AI:", res)

    # ------------------------
    # 可視化
    # ------------------------
    st.subheader("内部状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("energy:", round(st.session_state.energy, 3))

    st.subheader("欲求")
    st.write(u["drive"])

    st.subheader("価値観")
    st.write(u["values"])

    st.subheader("信念")
    st.write(u["belief"])

    st.subheader("記憶")
    st.write(u["memory"])

    st.subheader("他者モデル")
    st.write(u["user_model"])
