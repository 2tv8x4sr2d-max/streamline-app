import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（記憶進化版）")

# ------------------------
# 初期知識
# ------------------------
knowledge = {
    "嬉しい": {"emotion": 0.6},
    "楽しい": {"emotion": 0.7},
    "悲しい": {"emotion": -0.7},
    "辛い": {"emotion": -0.6},
    "怒り": {"emotion": -0.8},
    "好き": {"social": 0.5},
    "嫌い": {"social": -0.5},
    "怖い": {"emotion": -0.6},
    "安心": {"emotion": 0.5},
    "不安": {"emotion": -0.5},
    "試す": {"explore": 0.4},
    "新しい": {"explore": 0.5},
    "話す": {"social": 0.4},
    "助けて": {"social": 0.6},
}

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    st.session_state.users = {}
    st.session_state.energy = 0.5
    st.session_state.last_time = time.time()
    st.session_state.initialized = True

# ------------------------
# 記憶統合（超重要）
# ------------------------
def store_memory(text, u):

    for m in u["memory"]:
        if text in m["text"] or m["text"] in text:
            m["weight"] += 0.7
            m["count"] += 1
            return

    u["memory"].append({
        "text": text,
        "weight": 1.0,
        "count": 1
    })

# ------------------------
# 忘却
# ------------------------
def decay_memory(u):
    for m in u["memory"]:
        m["weight"] *= 0.995

# ------------------------
# 上位保持（容量管理）
# ------------------------
def trim_memory(u, max_mem=50):
    u["memory"] = sorted(
        u["memory"], key=lambda x: x["weight"], reverse=True
    )[:max_mem]

# ------------------------
# 学習
# ------------------------
def learn(text, u):

    for word, effect in knowledge.items():
        if word in text:

            if "emotion" in effect:
                u["emotion"] += effect["emotion"] * 0.1

            if "social" in effect:
                u["drive"]["social"] += effect["social"] * 0.1

            if "explore" in effect:
                u["drive"]["explore"] += effect["explore"] * 0.1

# ------------------------
# 内部更新
# ------------------------
def update_internal(e, energy):
    e += random.uniform(-0.02, 0.02)
    e += (energy - 0.5) * 0.1
    e *= 0.99

    energy += random.uniform(-0.02, 0.02)
    energy += e * 0.05

    return max(-1, min(1, e)), max(0, min(1, energy))

# ------------------------
# 欲求
# ------------------------
def update_drive(drive, energy, emotion):

    drive["explore"] += 0.01 + energy * 0.05
    drive["social"] += 0.01 + emotion * 0.05

    drive["explore"] -= drive["social"] * 0.02
    drive["social"] -= drive["explore"] * 0.02

    for k in drive:
        drive[k] *= 0.995
        drive[k] = max(0, min(1, drive[k]))

    drive["explore"] = max(0.25, drive["explore"])

    return drive

# ------------------------
# 思考生成（記憶影響）
# ------------------------
def generate_thought(u):

    thoughts = []

    if u["memory"]:
        strong = max(u["memory"], key=lambda x: x["weight"])
        thoughts.append(f"最近よく考える: {strong['text']}")

    if u["drive"]["explore"] > 0.6:
        thoughts.append("何か試したい")

    if u["drive"]["social"] > 0.6:
        thoughts.append("誰かと話したい")

    return thoughts

# ------------------------
# 応答生成
# ------------------------
def generate_response(u):

    e = u["emotion"]

    if e > 0.5:
        return "少し嬉しいかもしれない"

    if e < -0.5:
        return "少し不安定かもしれない"

    if u["memory"]:
        return "さっきのことが少し残ってる"

    return "まだはっきりしない"

# ------------------------
# 発話
# ------------------------
def decide_speech(u, user_input):

    now = time.time()

    if now - u["last_speak"] < 1.5:
        return None

    u["last_speak"] = now

    if user_input:
        return generate_response(u)

    if u["thought_buffer"]:
        return u["thought_buffer"].pop()

    return None

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前")
user_input = st.text_input("マザーに話しかける")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "thought_buffer": [],
            "memory": [],
            "last_speak": 0
        }

    u = st.session_state.users[user_id]

    # 時間進行
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.last_time = now

    for _ in range(int(dt * 10)):

        u["emotion"], st.session_state.energy = update_internal(
            u["emotion"], st.session_state.energy
        )

        u["drive"] = update_drive(
            u["drive"], st.session_state.energy, u["emotion"]
        )

        decay_memory(u)

        u["thought_buffer"].extend(generate_thought(u))

    # 入力処理
    if user_input:

        learn(user_input, u)
        store_memory(user_input, u)

    trim_memory(u, 50)

    # 発話
    speech = decide_speech(u, user_input)

    # ------------------------
    # 表示
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 思考")
        for t in u["thought_buffer"][-5:]:
            st.write("-", t)

    with col2:
        st.subheader("💬 マザー")
        if speech:
            st.write("🤖", speech)
        else:
            st.write("…")

    st.subheader("📊 状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("drive:", u["drive"])

    # 🔥 記憶可視化（強化）
    st.subheader("🧩 記憶（詳細）")

    total_weight = sum(m["weight"] for m in u["memory"])

    st.write("総記憶数:", len(u["memory"]))
    st.write("総重み:", round(total_weight, 3))

    for m in sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:10]:
        st.write({
            "text": m["text"],
            "weight": round(m["weight"], 3),
            "count": m["count"]
        })

# ループ
time.sleep(0.3)
st.rerun()
