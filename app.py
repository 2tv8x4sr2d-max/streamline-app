import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（可視化強化版）")

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
# 記憶
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

def trim_memory(u):
    u["memory"] = sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:80]

# ------------------------
# 記憶サンプリング
# ------------------------
def sample_memories(u):
    if not u["memory"]:
        return []

    sorted_mem = sorted(u["memory"], key=lambda x: x["weight"], reverse=True)

    strong = sorted_mem[0]
    weak = random.choice(sorted_mem[1:]) if len(sorted_mem) > 1 else strong

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
# 思考
# ------------------------
def generate_thought(u):
    thoughts = []

    if u["memory"]:
        thoughts.append("記憶が混ざっている")

    if u["drive"]["explore"] > 0.6:
        thoughts.append("試したい欲求がある")

    return thoughts

# ------------------------
# 発話（理由付き）
# ------------------------
def generate_response(u):
    mems = sample_memories(u)
    e = u["emotion"]

    if not mems:
        return "まだ不明", "記憶なし"

    texts = [m["text"] for m in mems]

    patterns = [
        "{}が残っている",
        "{}が混ざっている",
        "{}について考えている",
        "{}が気になる"
    ]

    combined = "と".join(texts)
    line = random.choice(patterns).format(combined)

    reason = f"記憶: {texts}"

    if e > 0.4:
        line += "（前向き）"
    elif e < -0.4:
        line += "（違和感）"

    return line, reason

# ------------------------
# 発話制御
# ------------------------
def decide_speech(u, user_input):
    now = time.time()

    if now - u["last_speak"] < 1.0:
        return None, None

    u["last_speak"] = now

    if user_input:
        return generate_response(u)

    if u["thought_buffer"]:
        return u["thought_buffer"].pop(), "思考出力"

    return None, None

# ------------------------
# UI
# ------------------------
user_id = st.text_input("あなたの名前")
user_input = st.text_input("話しかける")

if user_id:

    if user_id not in st.session_state.users:
        st.session_state.users[user_id] = {
            "emotion": 0.0,
            "drive": {"explore": 0.5, "social": 0.5},
            "memory": [],
            "thought_buffer": [],
            "speech_log": [],
            "thought_log": [],
            "decision_log": [],
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

        decay_memory(u)
        update_memory_type(u)

        thoughts = generate_thought(u)
        u["thought_buffer"].extend(thoughts)
        u["thought_log"].extend(thoughts)

    if user_input:
        store_memory(user_input, u)

    trim_memory(u)

    speech, reason = decide_speech(u, user_input)

    if speech:
        u["speech_log"].append(speech)
        u["decision_log"].append(reason)

    # ------------------------
    # UI表示
    # ------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 思考履歴")
        for t in u["thought_log"][-10:]:
            st.write("-", t)

    with col2:
        st.subheader("💬 発言履歴")
        for i, s in enumerate(reversed(u["speech_log"][-10:])):
            if i == 0:
                st.write("👉", s)
            else:
                st.write(s)

    st.subheader("⚙ 内部判断")
    for d in u["decision_log"][-5:]:
        st.write("-", d)

    st.subheader("📊 状態")
    st.write("emotion:", round(u["emotion"], 3))
    st.write("energy:", round(st.session_state.energy, 3))
    st.write("drive:", u["drive"])

    st.subheader("🧩 記憶")
    for m in u["memory"][:10]:
        st.write(m)

# ------------------------
# ループ
# ------------------------
time.sleep(0.3)
st.rerun()


