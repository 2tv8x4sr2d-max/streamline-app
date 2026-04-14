import streamlit as st
import random
import time

st.set_page_config(layout="wide")
st.title("🧠 成長するAI『マザー』（統合思考モデル）")

# ------------------------
# 初期化
# ------------------------
if "initialized" not in st.session_state:
    st.session_state.users = {}
    st.session_state.last_time = time.time()
    st.session_state.initialized = True

# ------------------------
# エージェント生成
# ------------------------
def create_agent():
    return {
        "memory": [],
        "word_memory": {},
        "uncertainty": 0.3,
        "emotion": {"joy": 0.0, "anger": 0.0, "sadness": 0.0, "fun": 0.0},
        "thought_buffer": [],
        "speech_log": []
    }

if "agents" not in st.session_state:
    st.session_state.agents = {
        "A": create_agent(),
        "B": create_agent()
    }

# ------------------------
# 記憶
# ------------------------
def store_memory(text, u):
    for m in u["memory"]:
        if text in m["text"]:
            m["weight"] += 0.5
            m["count"] += 1
            return

    u["memory"].append({
        "text": text,
        "weight": 1.0,
        "count": 1
    })

# ------------------------
# 言語学習
# ------------------------
def learn_words(text, u):
    words = text.replace("？", "").replace("?", "").split()
    for w in words:
        if len(w) < 2:
            continue
        u["word_memory"][w] = u["word_memory"].get(w, 0) + 1

# ------------------------
# 🔥 感情（改善版）
# ------------------------
def update_emotion(text, u):

    self_related = "自分" in text or "俺" in text
    other_related = "君" in text or "あなた" in text

    delta = {"joy":0,"anger":0,"sadness":0,"fun":0}

    if "嬉しい" in text:
        delta["joy"] += 0.3 if self_related else 0.1

    if "楽しい" in text:
        delta["fun"] += 0.3 if self_related else 0.1

    if "悲しい" in text:
        delta["sadness"] += 0.3

    if "嫌い" in text:
        delta["anger"] += 0.3

    # 記憶影響
    if any("嫌い" in m["text"] for m in u["memory"]):
        delta["anger"] += 0.05

    for k in u["emotion"]:
        u["emotion"][k] += delta[k]
        u["emotion"][k] *= 0.97
        u["emotion"][k] = max(0, min(1, u["emotion"][k]))

# ------------------------
# 記憶サンプル
# ------------------------
def sample_memories(u):
    return sorted(u["memory"], key=lambda x: x["weight"], reverse=True)[:2]

# ------------------------
# 解釈
# ------------------------
def interpret(text):
    intent = {"type": "statement", "uncertainty": 0.3}

    if "?" in text or "？" in text:
        intent["type"] = "question"
        intent["uncertainty"] += 0.2

    return intent

# ------------------------
# 深層思考
# ------------------------
def deep_think(u):
    thoughts = []

    if random.random() < 0.5:
        thoughts.append("何か試したい")

    if u["uncertainty"] > 0.6:
        thoughts.append("理解できていない")

    if u["memory"]:
        thoughts.append("記憶に引っ張られている")

    return thoughts

# ------------------------
# 🔥 思考統合（追加）
# ------------------------
def integrate_thoughts(a, b):

    combined = []

    combined += a

    for t in b:
        if "理解できていない" in t:
            combined.append("整理しようとしている")
        else:
            combined.append(t)

    return combined

# ------------------------
# 表層
# ------------------------
def surface_think(deep):
    out = []
    for t in deep:
        if "理解できていない" in t:
            out.append("整理できていない")
        elif "試したい" in t:
            out.append("行動したい")
        else:
            out.append(t)
    return out

# ------------------------
# 発話
# ------------------------
def verbalize(thoughts, intent, u):

    mems = sample_memories(u)
    words = list(u["word_memory"].keys())

    if words and random.random() < 0.7:
        combined = "と".join(random.sample(words, min(2, len(words))))
    elif mems:
        combined = "と".join([m["text"] for m in mems])
    else:
        combined = "何か"

    if intent["type"] == "question":
        line = combined + "について考えてる"
    else:
        line = combined + "が気になる"

    # 感情反映
    if u["emotion"]["anger"] > 0.5:
        line += "（少し苛立ち）"
    elif u["emotion"]["joy"] > 0.5:
        line += "（少しポジティブ）"
    elif u["emotion"]["sadness"] > 0.5:
        line += "（少し沈んでいる）"

    return line

# ------------------------
# UI
# ------------------------
user_input = st.text_input("話しかける")

A = st.session_state.agents["A"]
B = st.session_state.agents["B"]

if user_input:

    store_memory(user_input, A)
    learn_words(user_input, A)
    update_emotion(user_input, A)

    intent = interpret(user_input)

    # 🔥 2脳思考
    deep_A = deep_think(A)
    deep_B = deep_think(B)

    deep = integrate_thoughts(deep_A, deep_B)
    surface = surface_think(deep)

    speech = verbalize(surface, intent, A)

    A["speech_log"].append(speech)

# ------------------------
# 表示
# ------------------------
st.subheader("💬 マザー")
for s in A["speech_log"][-5:]:
    st.write(s)

st.subheader("🧠 思考")
for t in surface[-5:] if user_input else []:
    st.write("-", t)

st.subheader("📊 感情")
st.write(A["emotion"])

time.sleep(0.3)
st.rerun()
