import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（再構成発話モデル）")

# ------------------------
# 設定
# ------------------------
MIN_WEIGHT = 0.2
LONG_THRESHOLD = 2.5

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
    u["memory"] = sorted(
        u["memory"], key=lambda x: x["weight"], reverse=True
    )[:max_mem]

# ------------------------
# 🔥 記憶サンプリング（強＋弱）
# ------------------------
def sample_memories(u):

    if not u["memory"]:
        return []

    sorted_mem = sorted(u["memory"], key=lambda x: x["weight"], reverse=True)

    strong = sorted_mem[0]

    # 弱い記憶をランダム取得
    weak_candidates = sorted_mem[1:]
    weak = random.choice(weak_candidates) if weak_candidates else strong

    return [strong, weak]

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
        actions.append("対話")

    return actions

def apply_action(u):
    for a in act(u):
        if a == "探索":
            store_memory("探索:何か試した", u)
        if a == "対話":
            store_memory("対話:関係を求めた", u)

# ------------------------
# 思考
# ------------------------
def generate_thought(u):

    thoughts = []

    if u["memory"]:
        thoughts.append("いくつかの記憶が混ざっている感じがする")

    if u["drive"]["explore"] > 0.6:
        thoughts.append("試してみたい衝動がある")

    return thoughts

# ------------------------
# 🔥 発話（再構成）
# ------------------------
def generate_response(u):

    mems = sample_memories(u)
    e = u["emotion"]

    if not mems:
        return "まだはっきりしない"

    texts = [m["text"] for m in mems]

    # 🔥 テンプレ多様化
    patterns = [
        "{}がまだ頭にある",
        "{}が少し混ざってる感じがする",
        "{}についてうまく整理できてない",
        "{}が残ってる気がする",
        "{}が引っかかってる"
    ]

    combined = "と".join(texts)
    line = random.choice(patterns).format(combined)

    # 感情補正
    if e > 0.4:
        line += "（少し前向き）"
    elif e < -0.4:
        line += "（少し引っかかる）"

    # 揺らぎ
    r = random.random()
    if r < 0.3:
        line = "…うまく言えないけど、" + line
    elif r < 0.6:
        line += "かもしれない"

    return line

# ------------------------
# 発話制御
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

    st.subheader("🧩 記憶")
    
    for m in sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:10]:
        st.write({
            "text": m["text"],
            "weight": round(m["weight"], 3),
            "count": m["count"],
            "type": m["type"]
        })

    st.subheader("🧩 記憶（詳細）")

    for m in sorted(
        u["memory"], key=lambda x: x["weight"], reverse=True)[:10]:
    　　　st.write({
          text": m["text"],
            "weight": round(m["weight"], 3),
            "count": m["count"],
            "type": m["type"]
        })

# ループ
time.sleep(0.3)
st.rerun()



