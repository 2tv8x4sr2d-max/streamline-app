import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（行動＋記憶進化版）")

# ------------------------
# 初期設定
# ------------------------
MIN_WEIGHT = 0.2
LONG_THRESHOLD = 2.5

knowledge = {
    "嬉しい": {"emotion": 0.6},
    "悲しい": {"emotion": -0.7},
    "楽しい": {"emotion": 0.7},
    "嫌い": {"social": -0.5},
    "好き": {"social": 0.5},
    "新しい": {"explore": 0.5},
    "試す": {"explore": 0.5},
    "話す": {"social": 0.4},
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
# 記憶管理
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
        "count": 1,
        "type": "short"
    })

def decay_memory(u):
    for m in u["memory"]:
        if m["type"] == "long":
            m["weight"] *= 0.998
        else:
            m["weight"] *= 0.995

        if m["weight"] < MIN_WEIGHT:
            m["weight"] = MIN_WEIGHT

def update_memory_type(u):
    for m in u["memory"]:
        if m["weight"] > LONG_THRESHOLD:
            m["type"] = "long"

def trim_memory(u, max_mem=80):
    u["memory"] = sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:max_mem]

# ------------------------
# 記憶サンプリング
# ------------------------
def sample_memory(u):
    if not u["memory"]:
        return None

    total = sum(m["weight"] for m in u["memory"])
    r = random.uniform(0, total)
    s = 0

    for m in u["memory"]:
        s += m["weight"]
        if r <= s:
            return m["text"]

# ------------------------
# 内部状態
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

    drive["explore"] += 0.02 + energy * 0.05
    drive["social"] += 0.01 + emotion * 0.05

    drive["explore"] -= drive["social"] * 0.02
    drive["social"] -= drive["explore"] * 0.02

    for k in drive:
        drive[k] *= 0.995
        drive[k] = max(0, min(1, drive[k]))

    drive["explore"] = max(0.3, drive["explore"])

    return drive

# ------------------------
# 行動
# ------------------------
def act(u):
    actions = []

    if u["drive"]["explore"] > 0.6:
        actions.append("探索")

    if u["drive"]["social"] > 0.6:
        actions.append("対話欲求")

    return actions

def apply_action(u):
    actions = act(u)

    for a in actions:
        if a == "探索":
            result = "試した"
            store_memory("探索:" + result, u)

        if a == "対話欲求":
            result = "関係を求めた"
            store_memory("対話:" + result, u)

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
# 思考
# ------------------------
def generate_thought(u):

    thoughts = []

    mem = sample_memory(u)
    if mem:
        thoughts.append("思い出している: " + mem)

    if u["drive"]["explore"] > 0.6:
        thoughts.append("実際に試してみたい")

    return thoughts

# ------------------------
# 応答
# ------------------------
def generate_response(u):

    if u["memory"]:
        return "少し記憶に引っ張られてる"

    return "まだよく分からない"

# ------------------------
# 発話
# ------------------------
def decide_speech(u, user_input):

    now = time.time()

    if now - u["last_speak"] < 1.2:
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

        apply_action(u)
        decay_memory(u)
        update_memory_type(u)

        u["thought_buffer"].extend(generate_thought(u))

    if user_input:
        learn(user_input, u)
        store_memory(user_input, u)

    trim_memory(u)

    speech = decide_speech(u, user_input)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 思考")
        for t in u["thought_buffer"][-5:]:
            st.write("-", t)

    with col2:
        st.subheader("💬 マザー")
        st.write(speech if speech else "…")

    st.subheader("📊 状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("drive:", u["drive"])

    st.subheader("🧩 記憶（詳細）")

    for m in sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:10]:
        st.write({
            "text": m["text"],
            "weight": round(m["weight"], 3),
            "count": m["count"],
            "type": m["type"]
        })

# ループ
time.sleep(0.3)
st.rerun()
