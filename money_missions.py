import streamlit as st
import pandas as pd
import random
import numpy as np
from datetime import date

st.set_page_config(page_title="Money Missions (Web Demo)", layout="wide")

# ============================================================
# Themes (Unlocked by rewards)
# ============================================================
THEMES = {
    "Mint": {
        "bg": "linear-gradient(135deg, #eafff5 0%, #fffbe6 55%, #eaf2ff 100%)",
        "card_border": "rgba(16,185,129,0.18)",
        "side_border": "rgba(234,179,8,0.25)",
        "pill_bg": "rgba(234,179,8,0.18)",
        "pill_border": "rgba(234,179,8,0.35)",
    },
    "Ocean": {
        "bg": "linear-gradient(135deg, #e8f7ff 0%, #eafff5 60%, #fffbe6 100%)",
        "card_border": "rgba(59,130,246,0.18)",
        "side_border": "rgba(234,179,8,0.25)",
        "pill_bg": "rgba(59,130,246,0.12)",
        "pill_border": "rgba(59,130,246,0.25)",
    },
    "Sunset": {
        "bg": "linear-gradient(135deg, #fff1f2 0%, #fffbe6 55%, #eaf2ff 100%)",
        "card_border": "rgba(244,63,94,0.16)",
        "side_border": "rgba(234,179,8,0.25)",
        "pill_bg": "rgba(244,63,94,0.10)",
        "pill_border": "rgba(244,63,94,0.22)",
    },
}

# ============================================================
# Spend Options (Progressively more realistic by level)
# ============================================================
SPEND_OPTIONS_BY_LEVEL = {
    1: {
        "I buy nothing (0)": 0,
        "A small snack (2)": 2,
        "A sweet treat (3)": 3,
        "A small toy sticker (4)": 4,
    },
    2: {
        "I buy nothing (0)": 0,
        "A small snack (3)": 3,
        "A sweet treat (5)": 5,
        "A mini game item (6)": 6,
        "School supplies (4)": 4,
    },
    3: {
        "I buy nothing (0)": 0,
        "Candy (5) [want]": 5,
        "Game item (8) [want]": 8,
        "School supplies (6) [need]": 6,
        "Bus fare / ride (6) [need]": 6,
        "Healthy snack (4) [need]": 4,
    },
    4: {
        "I buy nothing (0)": 0,
        "Snack (4)": 4,
        "Movie night (10)": 10,
        "School supplies (7)": 7,
        "Gift (8)": 8,
    },
    5: {
        "I buy nothing (0)": 0,
        "Snack (4)": 4,
        "Game item (10)": 10,
        "Movie night (12)": 12,
        "School supplies (8)": 8,
    },
    6: {
        "I buy nothing (0)": 0,
        "Snack (4)": 4,
        "Game item (10)": 10,
        "Movie night (12)": 12,
        "School supplies (8)": 8,
    },
}

SHOP_ITEMS = [
    ("Sticker Pack 1", 5),
    ("Sticker Pack 2", 8),
    ("Theme Badge", 10),
    ("Super Saver Trophy", 15),
]

# ============================================================
# Learning Path
# ============================================================
LEVELS = {
    1: {
        "name": "Money Basics",
        "grade_band": "1",
        "concept": "Money is limited. When you spend, it goes down. When you save, it grows.",
        "mission_goal_text": "Save at least 2 coins.",
        "mission_goal_fn": lambda saved, spent, allowance: saved >= 2,
        "quiz_pool": [
            {"q": "If you have 10 coins and spend 3, how many coins are left?",
             "choices": ["7", "13", "3"], "answer": "7",
             "tip": "Spending makes your coins go down."},
            {"q": "Saving means:",
             "choices": ["Keeping coins for later", "Spending everything now", "Losing coins"],
             "answer": "Keeping coins for later",
             "tip": "Saving is keeping coins for later."},
        ],
        "puzzle_pool": [
            {"q": "Pick the best choice for your piggy bank.",
             "choices": ["Save 2 coins first", "Spend everything first", "Never save"],
             "answer": "Save 2 coins first",
             "tip": "Saving first helps your piggy bank grow."},
            {"q": "Which makes your coins go down?",
             "choices": ["Saving", "Spending", "Keeping coins safe"],
             "answer": "Spending",
             "tip": "Spending removes coins from your wallet."},
        ],
    },
    2: {
        "name": "Saving Habit and Goals",
        "grade_band": "2",
        "concept": "Saving a little often builds a habit. Habits help you reach goals.",
        "mission_goal_text": "Save at least 4 coins.",
        "mission_goal_fn": lambda saved, spent, allowance: saved >= 4,
        "quiz_pool": [
            {"q": "Best time to save is:",
             "choices": ["First, before spending", "After spending everything", "Only once a year"],
             "answer": "First, before spending",
             "tip": "Save first, then spend."},
            {"q": "If you save 3 coins each mission, after 4 missions you save:",
             "choices": ["12", "7", "3"],
             "answer": "12",
             "tip": "Small habits add up."},
        ],
        "puzzle_pool": [
            {"q": "You want a goal. What is the best plan?",
             "choices": ["Save a little each time", "Wait and hope", "Spend now, save later"],
             "answer": "Save a little each time",
             "tip": "Saving a little often is powerful."},
            {"q": "Your goal costs 30 coins. Saving 5 coins each mission takes:",
             "choices": ["6 missions", "3 missions", "30 missions"],
             "answer": "6 missions",
             "tip": "30 ÷ 5 = 6."},
        ],
    },
    3: {
        "name": "Needs vs. Wants",
        "grade_band": "3",
        "concept": "Needs help life run. Wants are fun. Balance both.",
        "mission_goal_text": "Save at least 5 coins and spend 6 or less.",
        "mission_goal_fn": lambda saved, spent, allowance: (saved >= 5) and (spent <= 6),
        "quiz_pool": [
            {"q": "Which one is usually a need?",
             "choices": ["School supplies", "Game item", "Candy"],
             "answer": "School supplies",
             "tip": "Needs help you learn and live."},
            {"q": "Which one is usually a want?",
             "choices": ["Candy", "Water", "Winter jacket (in winter)"],
             "answer": "Candy",
             "tip": "Wants are fun, but optional."},
        ],
        "puzzle_pool": [
            {"q": "Choose the best order:",
             "choices": ["Needs first, then wants", "Wants first, then needs", "Only wants"],
             "answer": "Needs first, then wants",
             "tip": "Needs first keeps life running."},
            {"q": "You only have 6 coins. Which is the best choice?",
             "choices": ["Bus fare (need)", "Candy (want)", "Game item (want)"],
             "answer": "Bus fare (need)",
             "tip": "Needs come first when coins are low."},
        ],
    },
    4: {
        "name": "Simple Budgeting (Jars)",
        "grade_band": "4",
        "concept": "A budget is a simple plan for coins (save, spend, share).",
        "mission_goal_text": "Create a budget and save at least 6 coins.",
        "mission_goal_fn": lambda saved, spent, allowance: saved >= 6,
        "quiz_pool": [
            {"q": "A budget is:",
             "choices": ["A plan for coins", "A way to get free coins", "A toy"],
             "answer": "A plan for coins",
             "tip": "A budget helps you choose on purpose."},
            {"q": "You have 12 coins. A balanced plan could be:",
             "choices": ["Save 6, spend 5, share 1", "Spend 12, save 0, share 0", "Save 0, spend 0, share 12"],
             "answer": "Save 6, spend 5, share 1",
             "tip": "A plan often includes saving and sharing too."},
        ],
        "puzzle_pool": [
            {"q": "If you set a spending limit, what happens?",
             "choices": ["You control treats better", "You lose all coins", "You forget your goal"],
             "answer": "You control treats better",
             "tip": "Limits protect your goal."},
        ],
    },
    5: {
        "name": "Repeats and Subscriptions",
        "grade_band": "5",
        "concept": "Small repeating costs add up. Always check what repeats.",
        "mission_goal_text": "Save at least 6 coins and keep repeat costs low.",
        "mission_goal_fn": lambda saved, spent, allowance: saved >= 6,
        "quiz_pool": [
            {"q": "A subscription is:",
             "choices": ["A repeating payment", "A free gift", "A one-time payment"],
             "answer": "A repeating payment",
             "tip": "Repeat costs can sneak up."},
            {"q": "If a subscription costs 2 coins each mission, after 5 missions it costs:",
             "choices": ["10", "2", "7"],
             "answer": "10",
             "tip": "2 coins × 5 missions = 10."},
        ],
        "puzzle_pool": [
            {"q": "Small costs that repeat can:",
             "choices": ["Add up a lot", "Never matter", "Make goals faster"],
             "answer": "Add up a lot",
             "tip": "Repeating costs can slow goals."},
            {"q": "Best choice before keeping a subscription is:",
             "choices": ["Check if you still use it", "Keep all subscriptions forever", "Never cancel anything"],
             "answer": "Check if you still use it",
             "tip": "Pay only for what you use."},
        ],
    },
    6: {
        "name": "Risk and Growth (Idea)",
        "grade_band": "5+",
        "concept": "Money can grow over time, but there is risk. Do not risk money you need soon.",
        "mission_goal_text": "Save at least 7 coins and try the growth test once.",
        "mission_goal_fn": lambda saved, spent, allowance: saved >= 7,
        "quiz_pool": [
            {"q": "Investing can:",
             "choices": ["Go up or down", "Only go up", "Never change"],
             "answer": "Go up or down",
             "tip": "Risk means it can go both ways."},
        ],
        "puzzle_pool": [
            {"q": "Best coins to risk are:",
             "choices": ["Extra coins you can wait with", "Lunch money", "Emergency coins"],
             "answer": "Extra coins you can wait with",
             "tip": "Do not risk money you need soon."},
        ],
    },
}

GOALS_BY_LEVEL = {
    1: [("Small toy", 30), ("Book", 35), ("Sticker mega pack", 40)],
    2: [("Bigger toy", 50), ("Art set", 55), ("Puzzle box", 60)],
    3: [("New game", 70), ("Sports gear", 80), ("Board game", 85)],
    4: [("Headphones", 100), ("School bag", 90), ("Cool hoodie", 110)],
    5: [("Bike fund", 160), ("Tablet fund", 180), ("Camera fund", 200)],
    6: [("Laptop fund", 240), ("Big goal", 300), ("Dream goal", 360)],
}

SURPRISE_EVENTS = [
    ("Your pencil broke. You need a new one.", -2),
    ("You lost an eraser. Replace it.", -1),
    ("You forgot a notebook. Buy a cheap one.", -3),
    ("Your friend’s birthday. You buy a small card.", -2),
]

SUBSCRIPTIONS = {
    "Music app (2 coins/mission)": 2,
    "Game pass (3 coins/mission)": 3,
    "Video app (2 coins/mission)": 2,
}

PARENT_REFLECTION = [
    "Spending too much",
    "Forgetting the goal",
    "Mixing up needs and wants",
    "Not saving first",
    "Doing great (keep going)",
]

# ============================================================
# Helpers
# ============================================================
def clamp(n, lo, hi):
    return max(lo, min(hi, n))

def default_level_for_grade(child_grade: int) -> int:
    return clamp(child_grade, 1, 6)

def level_unlock_rule(level: int, stars: int) -> bool:
    needed = {1: 0, 2: 10, 3: 25, 4: 45, 5: 70, 6: 100}
    return stars >= needed.get(level, 9999)

def compute_progress(bank_coins, goal_amount):
    if goal_amount <= 0:
        return 0.0
    return clamp(bank_coins / goal_amount, 0.0, 1.0)

def ai_coach_tip(save_hist, spend_hist, streak, level):
    if not save_hist:
        return "Try saving 2 coins first. Small steps are easiest."
    avg_save = float(np.mean(save_hist))
    avg_spend = float(np.mean(spend_hist)) if spend_hist else 0.0
    if streak == 0:
        return "Try an easy win: save first, then pick a tiny treat only if coins are left."
    if avg_spend > avg_save + 2:
        return "They spend more than they save. Try picking “I buy nothing” once this week."
    if avg_save >= avg_spend:
        if level <= 2:
            return "Nice habit. Keep saving first each mission."
        if level <= 4:
            return "Good balance. Next step: set a spending limit before treats."
        return "Strong choices. Keep extra coins for long-term goals."
    return "Try increasing saving by 1 coin next time. You will feel the difference."

def pick_from_pool(pool):
    return random.choice(pool)

def reset_daily_content_for_level(level: int):
    st.session_state.quiz_done_today = False
    st.session_state.puzzle_done_today = False
    st.session_state.quiz_feedback = None
    st.session_state.puzzle_feedback = None
    st.session_state.quiz_current = pick_from_pool(LEVELS[level]["quiz_pool"])
    st.session_state.puzzle_current = pick_from_pool(LEVELS[level]["puzzle_pool"])
    st.session_state.last_level_for_daily = level

    st.session_state.quiz_tries = 0
    st.session_state.quiz_star_awarded = False
    st.session_state.puzzle_tries = 0
    st.session_state.puzzle_star_awarded = False

def ensure_daily_rotation():
    today_str = date.today().isoformat()
    lvl = int(st.session_state.level)

    if st.session_state.last_day != today_str:
        st.session_state.last_day = today_str
        reset_daily_content_for_level(lvl)
        return

    if int(st.session_state.last_level_for_daily) != lvl:
        reset_daily_content_for_level(lvl)

def has_reward(name: str) -> bool:
    return name in st.session_state.unlocked_rewards

def unlock_reward(name: str):
    st.session_state.unlocked_rewards.add(name)
    if name == "Theme Badge":
        st.session_state.unlocked_themes.update({"Ocean", "Sunset"})
        if st.session_state.theme_name not in st.session_state.unlocked_themes:
            st.session_state.theme_name = "Mint"
    if name == "Sticker Pack 1":
        st.session_state.sidebar_stickers.update({"⭐", "🌈", "🍀"})
    if name == "Sticker Pack 2":
        st.session_state.sidebar_stickers.update({"🚀", "🦄", "🍭"})
    if name == "Super Saver Trophy":
        st.session_state.has_trophy = True

def apply_subscriptions_charge_if_needed():
    lvl = int(st.session_state.level)
    if lvl < 5:
        return
    if st.session_state.subscriptions_charged_this_mission:
        return

    total = 0
    for name in st.session_state.active_subscriptions:
        total += int(SUBSCRIPTIONS.get(name, 0))

    if total > 0:
        if int(st.session_state.wallet) >= total:
            st.session_state.wallet -= total
        else:
            remainder = total - int(st.session_state.wallet)
            st.session_state.wallet = 0
            st.session_state.bank = max(0, int(st.session_state.bank) - remainder)

        st.session_state.history.append(
            {"mission": int(st.session_state.mission), "event": "subscription_charge", "amount": -total}
        )

    st.session_state.subscriptions_charged_this_mission = True

def apply_allowance_for_mission_if_needed():
    if st.session_state.mission_paid:
        return
    st.session_state.wallet += int(st.session_state.allowance)
    st.session_state.mission_paid = True
    st.session_state.mission_paid_amount = int(st.session_state.allowance)
    st.session_state.subscriptions_charged_this_mission = False
    st.session_state.history.append(
        {"mission": int(st.session_state.mission), "event": "allowance_paid", "amount": int(st.session_state.allowance)}
    )
    apply_subscriptions_charge_if_needed()

def sync_allowance_change_in_current_mission():
    if not st.session_state.mission_paid:
        return
    current_paid = int(st.session_state.mission_paid_amount)
    new_allowance = int(st.session_state.allowance)
    diff = new_allowance - current_paid
    if diff != 0:
        st.session_state.wallet += diff
        st.session_state.mission_paid_amount = new_allowance
        st.session_state.history.append(
            {"mission": int(st.session_state.mission), "event": "allowance_adjust", "amount": diff}
        )

def spend_label_with_icons(choice: str) -> str:
    lower = choice.lower()
    if "[need]" in lower:
        return "need: " + choice
    if "[want]" in lower:
        return "want: " + choice
    return "buy: " + choice

def mission_summary_lines(saved, spent, allowance, lvl):
    lines = []
    if saved > 0:
        lines.append(f"you saved {saved} coins first. that builds a saving habit.")
    if spent == 0 and saved > 0:
        lines.append("you skipped buying this time. that protected your goal.")
    if lvl == 3:
        lines.append("remember: needs help life run. wants are fun. balance both.")
    if lvl >= 4:
        lines.append("a plan helps: set a limit before treats.")
    if allowance > 0:
        s_ratio = saved / allowance
        p_ratio = spent / allowance
        lines.append(f"your plan today: saved {int(round(s_ratio*100))}% and spent {int(round(p_ratio*100))}%.")
    return lines

# ============================================================
# Session State
# ============================================================
def init_state():
    st.session_state.mode = "Parents"
    st.session_state.view = "Welcome"

    st.session_state.child_grade = 1
    st.session_state.level = 1
    st.session_state.allowance = 10
    st.session_state.goal_name, st.session_state.goal_amount = GOALS_BY_LEVEL[1][0]

    st.session_state.mission = 1
    st.session_state.wallet = 0
    st.session_state.bank = 0
    st.session_state.stars = 0
    st.session_state.streak = 0

    st.session_state.mission_paid = False
    st.session_state.mission_paid_amount = 0
    st.session_state.subscriptions_charged_this_mission = False

    st.session_state.save_hist = []
    st.session_state.spend_hist = []
    st.session_state.history = []

    st.session_state.last_day = None
    st.session_state.last_level_for_daily = 1
    st.session_state.quiz_done_today = False
    st.session_state.puzzle_done_today = False
    st.session_state.quiz_current = None
    st.session_state.puzzle_current = None
    st.session_state.quiz_feedback = None
    st.session_state.puzzle_feedback = None

    st.session_state.quiz_tries = 0
    st.session_state.quiz_star_awarded = False
    st.session_state.puzzle_tries = 0
    st.session_state.puzzle_star_awarded = False

    st.session_state.unlocked_rewards = set()
    st.session_state.unlocked_themes = {"Mint"}
    st.session_state.theme_name = "Mint"
    st.session_state.sidebar_stickers = set()
    st.session_state.has_trophy = False

    st.session_state.parent_pin = "1234"
    st.session_state.parent_verified = False

    st.session_state.coach_draft_loaded = False
    st.session_state.active_subscriptions = set()

    st.session_state.play_step = "Mission"
    st.session_state.last_mission_summary = None

    st.session_state.parent_reflection_choice = "Doing great (keep going)"

if "mission" not in st.session_state:
    init_state()

ensure_daily_rotation()

# ============================================================
# Styling
# ============================================================
theme = THEMES.get(st.session_state.theme_name, THEMES["Mint"])

st.markdown(
    f"""
<style>
.stApp {{
  background: {theme["bg"]};
}}
.block-container {{
  padding-top: 0.65rem;
  padding-bottom: 2rem;
}}
.kid-card {{
  background: rgba(255,255,255,0.94);
  border-radius: 18px;
  padding: 16px 18px;
  margin: 10px 0px;
  border: 2px solid {theme["card_border"]};
  box-shadow: 0 10px 26px rgba(0,0,0,0.06);
}}
.side-box {{
  background: rgba(255,255,255,0.94);
  border-radius: 18px;
  padding: 14px 14px;
  margin-bottom: 10px;
  border: 2px solid {theme["side_border"]};
  box-shadow: 0 10px 26px rgba(0,0,0,0.06);
}}
.big-num {{ font-size: 30px; font-weight: 900; margin: 2px 0px; }}
.pill {{
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: {theme["pill_bg"]};
  border: 1px solid {theme["pill_border"]};
  font-size: 12px;
  margin-top: 6px;
}}
.checklist {{
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.18);
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 14px;
  margin: 10px 0px 14px 0px;
}}
.stButton button {{
  border-radius: 14px !important;
  padding: 0.62rem 0.95rem !important;
}}
footer {{ visibility: hidden; }}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# Header
# ============================================================
st.markdown('<div class="kid-card">', unsafe_allow_html=True)
st.title("💰 Money Missions")
st.caption("Save, spend, and learn step by step.")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.session_state.mode = st.radio(
        "Mode",
        ["Kids", "Parents"],
        index=0 if st.session_state.mode == "Kids" else 1,
        horizontal=True,
        key="mode_switch_sidebar",
    )

    st.markdown('<div class="side-box">', unsafe_allow_html=True)
    st.markdown("🛡️ Safety")
    st.caption("No accounts. No names. No emails. No chat. No free text. No external links.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="side-box">', unsafe_allow_html=True)
    st.markdown("🐷 Piggy Bank")
    st.markdown(f'<div class="big-num">{int(st.session_state.bank)} coins</div>', unsafe_allow_html=True)
    st.caption("Saved coins stay here until you buy your goal.")
    st.progress(compute_progress(int(st.session_state.bank), int(st.session_state.goal_amount)))
    st.caption(f"Goal: {st.session_state.goal_name} ({int(st.session_state.goal_amount)} coins)")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="side-box">', unsafe_allow_html=True)
    st.markdown("🎯 Goal Preview")
    goals = GOALS_BY_LEVEL.get(int(st.session_state.level), GOALS_BY_LEVEL[1])
    st.caption("Coming up later")
    for gname, gamt in goals[:3]:
        if gname == st.session_state.goal_name:
            st.write(f"now: {gname} ({gamt})")
        else:
            st.write(f"later: {gname} ({gamt})")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="side-box">', unsafe_allow_html=True)
    st.markdown("👛 Wallet")
    st.markdown(f'<div class="big-num">{int(st.session_state.wallet)} coins</div>', unsafe_allow_html=True)
    st.caption("Spending comes from here.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="side-box">', unsafe_allow_html=True)
    st.markdown("⭐ Stars")
    st.markdown(f'<div class="big-num">{int(st.session_state.stars)}</div>', unsafe_allow_html=True)
    st.caption("Stars are rewards for learning and good choices.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 Reset Game", key="reset_game_btn"):
        init_state()
        st.success("Reset complete ✅")
        st.rerun()

# ============================================================
# Navigation
# ============================================================
def kids_nav():
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("Where do you want to go? 🧭")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("👋 Welcome", key="nav_welcome"):
            st.session_state.view = "Welcome"
            st.rerun()
    with c2:
        if st.button("🎮 Play", key="nav_play"):
            st.session_state.view = "Play"
            st.session_state.play_step = "Mission"
            st.rerun()
    with c3:
        if st.button("📈 Progress", key="nav_progress"):
            st.session_state.view = "Progress"
            st.rerun()
    with c4:
        if st.button("🎁 Rewards", key="nav_rewards"):
            st.session_state.view = "Rewards"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def parents_nav():
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("Parent Pages 👨‍👩‍👧‍👦")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Learn", key="nav_parent_learn"):
            st.session_state.view = "Parent: Learn"
            st.rerun()
    with c2:
        if st.button("Coach", key="nav_parent_coach"):
            st.session_state.view = "Parent: Coach"
            st.rerun()
    with c3:
        if st.button("Report", key="nav_parent_report"):
            st.session_state.view = "Parent: Report"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Kids Mode
# ============================================================
if st.session_state.mode == "Kids":
    kids_nav()

    st.markdown(
        """
        <div class="checklist">
        Quick start:
        1) Go to Play.
        2) Do one Mission (save + spend).
        3) Do Today’s Learning (quiz + puzzle).
        4) Spend stars in Rewards.
        </div>
        """,
        unsafe_allow_html=True,
    )

    lvl = int(st.session_state.level)
    level_info = LEVELS[lvl]

    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    cA, cB, cC = st.columns(3)
    with cA:
        st.write(f"Grade: {int(st.session_state.child_grade)} 🎒")
        st.write(f"level: {lvl} - {level_info['name']}")
    with cB:
        st.write(f"Wallet: {int(st.session_state.wallet)} coins 👛")
        st.write(f"Piggy Bank: {int(st.session_state.bank)} coins 🐷")
    with cC:
        st.write(f"Stars: {int(st.session_state.stars)} ⭐")
        st.write(f"Streak: {int(st.session_state.streak)} missions 🔥")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.view == "Welcome":
        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.subheader("Welcome 👋")
        st.write("This app teaches money through missions. each mission is one play session.")
        st.write("You earn coins, make choices, and grow your piggy bank.")
        st.caption("Tip: saving first makes your goal happen faster.")
        st.caption("Demo parent pin: 1234")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.view == "Play":
        apply_allowance_for_mission_if_needed()

        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.subheader(f"level {lvl}: {level_info['name']}")
        concept = level_info.get("concept","")
        if concept:
            st.caption(concept)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.subheader(f"mission {int(st.session_state.mission)}")
        st.write(f"you got {int(st.session_state.allowance)} coins for this mission.")
        st.markdown(f'<span class="pill">mission goal: {level_info["mission_goal_text"]}</span>', unsafe_allow_html=True)

        st.session_state.play_step = st.radio(
            "mission steps",
            ["Mission", "Today’s learning"],
            index=0 if st.session_state.play_step == "Mission" else 1,
            horizontal=True,
            key="play_step_toggle",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.play_step == "Mission":
        if lvl >= 5:
            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Repeat Costs (Subscriptions) 🔁")
            st.caption("These cost coins every mission until you turn them off.")
            current = set(st.session_state.active_subscriptions)

            for sub_name, sub_cost in SUBSCRIPTIONS.items():
                on = sub_name in current
                new_on = st.checkbox(
                    f"{sub_name} ({sub_cost} coins)",
                    value=on,
                    key=f"sub_{sub_name}_m{st.session_state.mission}",  # key changes each mission
                )
                if new_on:
                    st.session_state.active_subscriptions.add(sub_name)
                else:
                    st.session_state.active_subscriptions.discard(sub_name)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="kid-card">', unsafe_allow_html=True)

    # wrap all mission choices + finish button in a form so it must be re-submitted each mission
    with st.form(key=f"mission_form_{st.session_state.mission}", clear_on_submit=True):

        spend_amt = 0
        save_amt = 0
        do_growth_test = False

        spend_options = SPEND_OPTIONS_BY_LEVEL.get(lvl, SPEND_OPTIONS_BY_LEVEL[2])

        st.caption("Tiny plan: try to save first, then choose a buy that fits your wallet.")

        if lvl <= 2:
            st.subheader("Step 1: save first")
            save_amt = st.slider(
                "Move coins into your piggy bank",
                min_value=0,
                max_value=int(st.session_state.wallet),
                value=0,
            )

            remaining_wallet = int(st.session_state.wallet) - int(save_amt)

            st.subheader("Step 2: choose a buy (optional)")
            spend_choice = st.selectbox("Pick one", list(spend_options.keys()))
            spend_amt = int(spend_options[spend_choice])

            if spend_amt > remaining_wallet:
                st.warning("That buy is too expensive after saving. pick a smaller buy or save less.")

        elif lvl == 3:
            st.subheader("Step 1: save first")
            save_amt = st.slider(
                "Save coins before spending",
                min_value=0,
                max_value=int(st.session_state.wallet),
                value=0,
            )

            remaining_wallet = int(st.session_state.wallet) - int(save_amt)

            st.subheader("Step 2: need or want?")
            st.caption("Needs help life run. Wants are fun.")
            labeled = [spend_label_with_icons(k) for k in spend_options.keys()]
            mapping = dict(zip(labeled, list(spend_options.keys())))
            spend_pick_label = st.selectbox("Pick one", labeled)
            spend_choice = mapping[spend_pick_label]
            spend_amt = int(spend_options[spend_choice])

            if spend_amt > remaining_wallet:
                st.warning("That buy is too expensive after saving. pick a smaller buy or save less.")

        elif lvl == 4:
            st.subheader("Step 1: make a budget (jars)")
            st.caption("Plan your coins: save, spend, and share.")

            total = int(st.session_state.wallet)
            save_amt = st.slider("Save jar", 0, total, 0)
            remaining = total - int(save_amt)
            spend_amt_plan = st.slider("Spend jar", 0, remaining, 0)

            st.subheader("Step 2: choose a buy (Must fit your spend jar)")
            spend_choice = st.selectbox("Pick one", list(spend_options.keys()))
            spend_amt = int(spend_options[spend_choice])

            if spend_amt > int(spend_amt_plan):
                st.warning("That buy is bigger than your spend jar. Choose a smaller buy, or increase your spend jar.")

        else:
            st.subheader("Step 1: save first")
            save_amt = st.slider(
                "Save coins before spending",
                min_value=0,
                max_value=int(st.session_state.wallet),
                value=0,
            )

            remaining_wallet = int(st.session_state.wallet) - int(save_amt)

            st.subheader("Step 2: Choose a buy (optional)")
            spend_choice = st.selectbox("Pick one", list(spend_options.keys()))
            spend_amt = int(spend_options[spend_choice])

            if spend_amt > remaining_wallet:
                st.warning("That buy is too expensive after saving. pick a smaller buy or save less.")

            if lvl >= 6:
                st.subheader("Step 3: Growth test (risk)")
                do_growth_test = st.checkbox("use 5 coins for a growth test (can give back 4-7 coins)")
                st.caption("This teaches risk: it can go up or down. do not risk coins you need soon.")

        # IMPORTANT: use form_submit_button (not st.button)
        finish = st.form_submit_button("Finish this mission")

    st.markdown("</div>", unsafe_allow_html=True)

        spend_amt = 0
        save_amt = 0
        do_growth_test = False
    
        spend_options = SPEND_OPTIONS_BY_LEVEL.get(lvl, SPEND_OPTIONS_BY_LEVEL[2])
    
        st.caption("Tiny plan: try to save first, then choose a buy that fits your wallet.")

            if lvl <= 2:
                st.subheader("Step 1: save first")
                save_amt = st.slider(
                    "Move coins into your piggy bank",
                    min_value=0,
                    max_value=int(st.session_state.wallet),
                    value=min(4 if lvl == 2 else 2, int(st.session_state.wallet)),
                    key="save_slider_basic",
                )

                remaining_wallet = int(st.session_state.wallet) - int(save_amt)
                st.subheader("Step 2: choose a buy (optional)")
                spend_choice = st.selectbox("Pick one", list(spend_options.keys()), key="spend_choice_basic")
                spend_amt = int(spend_options[spend_choice])

                if spend_amt > remaining_wallet:
                    st.warning("That buy is too expensive after saving. pick a smaller buy or save less.")

            elif lvl == 3:
                st.subheader("Step 1: save first")
                save_amt = st.slider(
                    "Save coins before spending",
                    min_value=0,
                    max_value=int(st.session_state.wallet),
                    value=min(5, int(st.session_state.wallet)),
                    key="save_slider_nv",
                )

                remaining_wallet = int(st.session_state.wallet) - int(save_amt)
                st.subheader("Step 2: need or want?")
                st.caption("Seeds help life run. Wants are fun.")
                labeled = [spend_label_with_icons(k) for k in spend_options.keys()]
                mapping = dict(zip(labeled, list(spend_options.keys())))
                spend_pick_label = st.selectbox("Pick one", labeled, key="spend_choice_nv")
                spend_choice = mapping[spend_pick_label]
                spend_amt = int(spend_options[spend_choice])

                if spend_amt > remaining_wallet:
                    st.warning("That buy is too expensive after saving. pick a smaller buy or save less.")

            elif lvl == 4:
                st.subheader("Step 1: make a budget (jars)")
                st.caption("Plan your coins: save, spend, and share.")

                total = int(st.session_state.wallet)
                save_amt = st.slider("Save jar", 0, total, min(6, total), key="jar_save")
                remaining = total - int(save_amt)
                spend_amt_plan = st.slider("Spend jar", 0, remaining, min(5, remaining), key="jar_spend")

                st.subheader("Step 2: choose a buy (Must fit your spend jar)")
                spend_choice = st.selectbox("Pick one", list(spend_options.keys()), key="spend_choice_budget")
                spend_amt = int(spend_options[spend_choice])

                if spend_amt > int(spend_amt_plan):
                    st.warning("That buy is bigger than your spend jar. Choose a smaller buy, or increase your spend jar.")

            else:
                st.subheader("Step 1: save first")
                save_amt = st.slider(
                    "Save coins before spending",
                    min_value=0,
                    max_value=int(st.session_state.wallet),
                    value=min(6, int(st.session_state.wallet)),
                    key="save_slider_subs",
                )

                remaining_wallet = int(st.session_state.wallet) - int(save_amt)
                st.subheader("Step 2: Choose a buy (optional)")
                spend_choice = st.selectbox("Pick one", list(spend_options.keys()), key="spend_choice_subs")
                spend_amt = int(spend_options[spend_choice])

                if spend_amt > remaining_wallet:
                    st.warning("That buy is too expensive after saving. pick a smaller buy or save less.")

                if lvl >= 6:
                    st.subheader("Step 3: Growth test (risk)")
                    do_growth_test = st.checkbox("use 5 coins for a growth test (can give back 4-7 coins)", key="growth_test_chk")
                    st.caption("This teaches risk: it can go up or down. do not risk coins you need soon.")

            finish = st.button("Finish this mission", key="finish_mission_btn")
            st.markdown("</div>", unsafe_allow_html=True)

            if finish:
                if lvl == 4:
                    total = int(st.session_state.wallet)
                    planned_spend = int(st.session_state["jar_spend"])
                    planned_save = int(st.session_state["jar_save"])
                    if planned_save + planned_spend > total:
                        st.error("Your jars do not fit your wallet. try again.")
                        st.stop()
                    if spend_amt > planned_spend:
                        st.error("That buy is bigger than your spend jar. choose a smaller buy.")
                        st.stop()
                    save_amt = planned_save

                if int(save_amt) + int(spend_amt) > int(st.session_state.wallet):
                    st.error("You do not have enough coins in your wallet for that choice.")
                else:
                    st.session_state.wallet -= (int(save_amt) + int(spend_amt))
                    st.session_state.bank += int(save_amt)

                    st.session_state.save_hist.append(int(save_amt))
                    st.session_state.spend_hist.append(int(spend_amt))

                    stars_earned = 0

                    if int(save_amt) >= 2:
                        stars_earned += 2
                    if int(save_amt) >= 5:
                        stars_earned += 1

                    allowance = int(st.session_state.allowance)
                    if allowance > 0:
                        s_ratio = int(save_amt) / allowance
                        p_ratio = int(spend_amt) / allowance
                        if s_ratio >= 0.40 and p_ratio <= 0.40 and int(save_amt) > 0:
                            stars_earned += 2
                        if p_ratio <= 0.15 and s_ratio >= 0.50 and int(save_amt) > 0:
                            stars_earned += 1

                    if int(spend_amt) == 0 and int(save_amt) >= 4:
                        stars_earned += 1

                    if lvl >= 4 and int(save_amt) >= 6:
                        stars_earned += 1

                    growth_result = None
                    if lvl >= 6 and do_growth_test:
                        if int(st.session_state.wallet) >= 5:
                            st.session_state.wallet -= 5
                            growth_result = random.choice([4, 5, 6, 7])
                            st.session_state.wallet += growth_result
                        else:
                            st.warning("Not enough wallet coins for the growth test after your choices.")

                    surprise_text = None
                    if lvl >= 3 and random.random() < 0.22:
                        ev_name, ev_delta = random.choice(SURPRISE_EVENTS)
                        if int(st.session_state.wallet) + ev_delta >= 0:
                            st.session_state.wallet += ev_delta
                        else:
                            needed = abs(int(st.session_state.wallet) + ev_delta)
                            st.session_state.wallet = 0
                            st.session_state.bank = max(0, int(st.session_state.bank) - needed)
                        surprise_text = f"surprise: {ev_name} ({ev_delta} coins)"

                    met_goal = level_info["mission_goal_fn"](int(save_amt), int(spend_amt), int(st.session_state.allowance))
                    if met_goal:
                        stars_earned += 3
                        st.session_state.streak += 1
                        goal_text = "Mission goal reached"
                    else:
                        st.session_state.streak = 0
                        goal_text = "Mission goal not reached"

                    if stars_earned > 0:
                        st.session_state.stars += stars_earned

                    summary = {
                        "saved": int(save_amt),
                        "spent": int(spend_amt),
                        "stars_earned": int(stars_earned),
                        "goal_text": goal_text,
                        "growth_result": growth_result,
                        "surprise_text": surprise_text,
                        "lines": mission_summary_lines(int(save_amt), int(spend_amt), int(st.session_state.allowance), lvl),
                        "bank": int(st.session_state.bank),
                        "wallet": int(st.session_state.wallet),
                    }
                    st.session_state.last_mission_summary = summary

                    st.session_state.history.append(
                        {
                            "mission": int(st.session_state.mission),
                            "event": "mission_end",
                            "saved": int(save_amt),
                            "spent": int(spend_amt),
                            "bank": int(st.session_state.bank),
                            "wallet": int(st.session_state.wallet),
                            "stars": int(st.session_state.stars),
                            "streak": int(st.session_state.streak),
                            "level": int(st.session_state.level),
                            "allowance": int(st.session_state.allowance),
                        }
                    )

                    st.session_state.mission += 1
                    st.session_state.mission_paid = False
                    st.session_state.mission_paid_amount = 0
                    st.session_state.subscriptions_charged_this_mission = False

                    st.session_state.play_step = "Today’s learning"
                    st.balloons()
                    st.rerun()

            if st.session_state.last_mission_summary:
                s = st.session_state.last_mission_summary
                st.markdown('<div class="kid-card">', unsafe_allow_html=True)
                st.subheader("Mission Summary 🧾")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.write(f"saved: {s['saved']}")
                with c2:
                    st.write(f"spent: {s['spent']}")
                with c3:
                    st.write(f"stars earned: {s['stars_earned']}")
                with c4:
                    st.write(s["goal_text"])

                st.progress(compute_progress(int(st.session_state.bank), int(st.session_state.goal_amount)))
                st.caption(f"goal: {st.session_state.goal_name} ({int(st.session_state.goal_amount)} coins)")

                for line in s["lines"]:
                    st.write("- " + line)

                if s["growth_result"] is not None:
                    st.write(f"- growth test result: you got back {s['growth_result']} coins.")

                if s["surprise_text"]:
                    st.write("- " + s["surprise_text"])

                st.markdown("</div>", unsafe_allow_html=True)

            if int(st.session_state.bank) >= int(st.session_state.goal_amount):
                st.markdown('<div class="kid-card">', unsafe_allow_html=True)
                st.subheader("Buy My Goal 🎯")
                st.write(f"goal: {st.session_state.goal_name} ({int(st.session_state.goal_amount)} coins)")
                if st.button("Buy my goal now", key="buy_goal_btn"):
                    st.session_state.bank -= int(st.session_state.goal_amount)
                    st.session_state.stars += 8
                    st.session_state.last_mission_summary = None
                    st.success("You bought your goal. new goal unlocked.")

                    options = GOALS_BY_LEVEL.get(int(st.session_state.level), GOALS_BY_LEVEL[1])
                    candidates = [g for g in options if g[0] != st.session_state.goal_name]
                    if candidates:
                        st.session_state.goal_name, st.session_state.goal_amount = random.choice(candidates)
                    else:
                        st.session_state.goal_name, st.session_state.goal_amount = options[0]
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.play_step == "Today’s learning":
            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Today’s Learning 🧠")
            st.caption("You get 2 tries. stars only count the first time you get it correct.")

            st.write("Quiz (1 question) 📝")
            quiz = st.session_state.quiz_current
            st.write(quiz["q"])
            quiz_choice = st.radio("choose one", quiz["choices"], key="quiz_choice_kids")

            quiz_done = st.session_state.quiz_done_today
            if quiz_done:
                st.caption("Quiz is done for today. come back tomorrow for a new one.")
            else:
                if st.button("check quiz answer", key="check_quiz_btn"):
                    st.session_state.quiz_tries += 1
                    if quiz_choice == quiz["answer"]:
                        if not st.session_state.quiz_star_awarded:
                            st.session_state.stars += 2
                            st.session_state.quiz_star_awarded = True
                        st.session_state.quiz_feedback = {"type": "success", "text": "correct", "tip": ""}
                        st.session_state.quiz_done_today = True
                    else:
                        st.session_state.quiz_feedback = {"type": "warning", "text": "not quite", "tip": quiz["tip"]}
                        if st.session_state.quiz_tries >= 2:
                            st.session_state.quiz_done_today = True
                    st.rerun()

            if st.session_state.quiz_feedback:
                fb = st.session_state.quiz_feedback
                if fb["type"] == "success":
                    st.success(f"{fb['text']} (+2 stars if first correct)")
                else:
                    st.warning(fb["text"])
                    if fb.get("tip"):
                        st.info(fb["tip"])
                    remaining = max(0, 2 - int(st.session_state.quiz_tries))
                    if not st.session_state.quiz_done_today:
                        st.caption(f"tries left: {remaining}")

            st.markdown("---")

            st.write("Puzzle (1 question) 🧩")
            puzzle = st.session_state.puzzle_current
            st.write(puzzle["q"])
            puzzle_choice = st.radio("choose one", puzzle["choices"], key="puzzle_choice_kids")

            puzzle_done = st.session_state.puzzle_done_today
            if puzzle_done:
                st.caption("Puzzle is done for today. come back tomorrow for a new one.")
            else:
                if st.button("Check puzzle answer", key="check_puzzle_btn"):
                    st.session_state.puzzle_tries += 1
                    if puzzle_choice == puzzle["answer"]:
                        if not st.session_state.puzzle_star_awarded:
                            st.session_state.stars += 2
                            st.session_state.puzzle_star_awarded = True
                        st.session_state.puzzle_feedback = {"type": "success", "text": "nice", "tip": ""}
                        st.session_state.puzzle_done_today = True
                    else:
                        st.session_state.puzzle_feedback = {"type": "warning", "text": "almost", "tip": puzzle["tip"]}
                        if st.session_state.puzzle_tries >= 2:
                            st.session_state.puzzle_done_today = True
                    st.rerun()

            if st.session_state.puzzle_feedback:
                fb = st.session_state.puzzle_feedback
                if fb["type"] == "success":
                    st.success(f"{fb['text']} (+2 stars if first correct)")
                else:
                    st.warning(fb["text"])
                    if fb.get("tip"):
                        st.info(fb["tip"])
                    remaining = max(0, 2 - int(st.session_state.puzzle_tries))
                    if not st.session_state.puzzle_done_today:
                        st.caption(f"tries left: {remaining}")

            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.view == "Progress":
        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.subheader("My Progress 📈")
        st.write(f"Grade: {int(st.session_state.child_grade)} 🎒")
        st.write(f"level: {int(st.session_state.level)}")
        st.write(f"Streak: {int(st.session_state.streak)} missions 🔥")
        st.write(f"Stars: {int(st.session_state.stars)} ⭐")
        st.progress(compute_progress(int(st.session_state.bank), int(st.session_state.goal_amount)))
        st.caption(f"goal: {st.session_state.goal_name} ({int(st.session_state.goal_amount)} coins)")
        st.markdown("</div>", unsafe_allow_html=True)

        rows = [h for h in st.session_state.history if h.get("event") == "mission_end"]
        if rows:
            df = pd.DataFrame(rows).sort_values("mission")

            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("piggy bank over time")
            st.line_chart(df.set_index("mission")["bank"])
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("saved vs. spent each mission")
            st.line_chart(df.set_index("mission")[["saved", "spent"]])
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("play at least one mission to see charts.")

        next_level = clamp(int(st.session_state.level) + 1, 1, 6)
        if next_level != int(st.session_state.level) and level_unlock_rule(next_level, int(st.session_state.stars)):
            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Level Up Available 🚀")
            st.write(f"You unlocked level {next_level}. switch your level in parents mode.")
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.view == "Rewards":
        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.subheader("Rewards Shop 🎁")
        st.caption("Spend stars to unlock fun upgrades that change your app.")
        st.write(f"Your stars: {int(st.session_state.stars)}")
        st.markdown("</div>", unsafe_allow_html=True)

        if has_reward("Theme Badge"):
            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Choose Your Theme 🎨")
            theme_choices = sorted(list(st.session_state.unlocked_themes))
            new_theme = st.selectbox("theme", theme_choices, index=theme_choices.index(st.session_state.theme_name), key="theme_pick")
            if new_theme != st.session_state.theme_name:
                st.session_state.theme_name = new_theme
                st.success(f"theme applied: {new_theme}")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.subheader("Shop Items 🛍️")
        for item_name, cost in SHOP_ITEMS:
            owned = has_reward(item_name)
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.write(f"{item_name}")
            with c2:
                st.write(f"{cost} stars")
            with c3:
                if owned:
                    st.success("owned")
                else:
                    if st.button("buy", key=f"buy_{item_name}"):
                        if int(st.session_state.stars) >= int(cost):
                            st.session_state.stars -= int(cost)
                            unlock_reward(item_name)
                            st.success(f"you bought {item_name}")
                            st.rerun()
                        else:
                            st.error("not enough stars yet")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.subheader("My Rewards 🎉")
        if st.session_state.unlocked_rewards:
            st.write(", ".join(sorted(list(st.session_state.unlocked_rewards))))
        else:
            st.write("No rewards yet. Earn stars by playing and doing today’s learning.")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Parents Mode
# ============================================================
if st.session_state.mode == "Parents":
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("Parent Verification 🔒")
    st.caption("Demo pin starts as 1234. you can change it in coach.")

    pin = st.text_input("Enter parent pin", type="password", key="pin_entry")

    if st.button("Verify parent", key="verify_parent_btn"):
        st.session_state.parent_verified = (pin == st.session_state.parent_pin)

    if st.session_state.parent_verified:
        st.success("Parent verified ✅")
    else:
        st.warning("Not verified yet.")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.parent_verified:
        parents_nav()

        if st.session_state.view == "Parent: Learn":
            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("What Kids Learn (Grades 1–5) 📘")
            st.write("This is a learning path. each level adds one new money idea.")
            st.write("Kids practice with missions, then learn with a daily quiz and puzzle.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Level Path 🧭")
            for lv in range(1, 7):
                status = "unlocked" if level_unlock_rule(lv, int(st.session_state.stars)) else "locked"
                st.write(f"level {lv}: {LEVELS[lv]['name']} (grade {LEVELS[lv]['grade_band']}) - {status}")
                st.caption(LEVELS[lv]["concept"])
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.view == "Parent: Coach":
            if not st.session_state.coach_draft_loaded:
                st.session_state.draft_grade = int(st.session_state.child_grade)
                st.session_state.draft_level = int(st.session_state.level)
                st.session_state.draft_allowance = int(st.session_state.allowance)

                st.session_state.draft_goal_name = str(st.session_state.goal_name)
                st.session_state.draft_goal_amount = int(st.session_state.goal_amount)

                st.session_state.draft_goal_pick = "Suggested"
                st.session_state.coach_draft_loaded = True

            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Parent Setup ⚙️")
            st.caption("Change settings below, then press save settings")

            st.session_state.draft_grade = st.selectbox(
                "child grade",
                [1, 2, 3, 4, 5],
                index=[1, 2, 3, 4, 5].index(int(st.session_state.draft_grade)),
                key="coach_grade",
            )

            recommended = default_level_for_grade(int(st.session_state.draft_grade))
            st.caption(f"Recommended level: level {recommended}")

            max_level_by_grade = clamp(recommended + 1, 1, 6)
            selectable = []
            for lv in range(1, max_level_by_grade + 1):
                if lv <= recommended or level_unlock_rule(lv, int(st.session_state.stars)):
                    selectable.append(lv)
            if not selectable:
                selectable = [recommended]

            if int(st.session_state.draft_level) not in selectable:
                st.session_state.draft_level = selectable[0]

            st.session_state.draft_level = st.selectbox(
                "choose level",
                selectable,
                index=selectable.index(int(st.session_state.draft_level)),
                key="coach_level",
            )

            st.session_state.draft_allowance = st.number_input(
                "allowance per mission (coins)",
                min_value=1,
                max_value=999,
                value=int(st.session_state.draft_allowance),
                step=1,
                key="coach_allowance",
            )

            st.subheader("goal setup")
            goal_options = GOALS_BY_LEVEL.get(int(st.session_state.draft_level), GOALS_BY_LEVEL[1])
            goal_names = [g[0] for g in goal_options]
            goal_dict = dict(goal_options)

            st.session_state.draft_goal_pick = st.selectbox(
                "goal type",
                ["Suggested", "Custom goal..."],
                index=0 if st.session_state.draft_goal_pick == "Suggested" else 1,
                key="coach_goal_type",
            )

            if st.session_state.draft_goal_pick == "Suggested":
                default_idx = 0
                if st.session_state.draft_goal_name in goal_names:
                    default_idx = goal_names.index(st.session_state.draft_goal_name)

                st.session_state.draft_goal_name = st.selectbox(
                    "choose a goal",
                    goal_names,
                    index=default_idx,
                    key="coach_goal_pick",
                )
                st.session_state.draft_goal_amount = int(goal_dict[st.session_state.draft_goal_name])
                st.caption(f"Goal Cost: {int(st.session_state.draft_goal_amount)} coins")
            else:
                st.session_state.draft_goal_name = st.text_input(
                    "custom goal name",
                    value=st.session_state.draft_goal_name if st.session_state.draft_goal_name else "my goal",
                    key="coach_goal_custom_name",
                )
                st.session_state.draft_goal_amount = st.number_input(
                    "custom goal coins",
                    min_value=5,
                    max_value=9999,
                    value=int(st.session_state.draft_goal_amount) if int(st.session_state.draft_goal_amount) >= 5 else 50,
                    step=1,
                    key="coach_goal_custom_amount",
                )

            st.subheader("parent reflection (quick check)")
            st.session_state.parent_reflection_choice = st.selectbox(
                "what did your child struggle with most recently?",
                PARENT_REFLECTION,
                index=PARENT_REFLECTION.index(st.session_state.parent_reflection_choice) if st.session_state.parent_reflection_choice in PARENT_REFLECTION else 0,
                key="parent_reflection_pick",
            )
            reflection = st.session_state.parent_reflection_choice
            if reflection == "Spending too much":
                st.info("try: let’s choose a small treat and still save for the goal. what’s a fair limit?")
            elif reflection == "Forgetting the goal":
                st.info("try: let’s look at the goal bar. how many coins until we reach it?")
            elif reflection == "Mixing up needs and wants":
                st.info("try: is this a need for today, or a want for fun? can we do the need first?")
            elif reflection == "Not saving first":
                st.info("try: let’s save first every mission. even 2 coins counts.")
            else:
                st.info("try: nice work. what was your best choice today and why?")

            st.subheader("coach tip")
            st.info(ai_coach_tip(
                st.session_state.save_hist,
                st.session_state.spend_hist,
                int(st.session_state.streak),
                int(st.session_state.draft_level),
            ))

            if st.button("save settings", key="save_settings_btn"):
                st.session_state.child_grade = int(st.session_state.draft_grade)
                st.session_state.level = int(st.session_state.draft_level)

                st.session_state.allowance = int(st.session_state.draft_allowance)
                sync_allowance_change_in_current_mission()

                name = str(st.session_state.draft_goal_name).strip()
                st.session_state.goal_name = name if name else "goal"
                st.session_state.goal_amount = int(st.session_state.draft_goal_amount)

                ensure_daily_rotation()

                st.success("Settings saved ✅")
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Change Parent PIN 🔐")
            new_pin = st.text_input("new pin", type="password", key="new_pin_input")
            if st.button("update pin", key="update_pin_btn"):
                if new_pin and len(new_pin) >= 4:
                    st.session_state.parent_pin = new_pin
                    st.success("PIN updated ✅")
                else:
                    st.error("Pin must be at least 4 characters")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.view == "Parent: Report":
            st.markdown('<div class="kid-card">', unsafe_allow_html=True)
            st.subheader("Parent Report 🧾")
            st.write(f"child grade: {int(st.session_state.child_grade)}")
            st.write(f"current level: {int(st.session_state.level)}")
            st.write(f"allowance: {int(st.session_state.allowance)} coins per mission")
            st.write(f"goal: {st.session_state.goal_name} ({int(st.session_state.goal_amount)} coins)")
            if int(st.session_state.level) >= 5:
                if st.session_state.active_subscriptions:
                    st.write("active subscriptions: " + ", ".join(sorted(st.session_state.active_subscriptions)))
                else:
                    st.write("active subscriptions: none")
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.save_hist:
                avg_save = float(np.mean(st.session_state.save_hist))
                avg_spend = float(np.mean(st.session_state.spend_hist)) if st.session_state.spend_hist else 0.0
                st.markdown('<div class="kid-card">', unsafe_allow_html=True)
                st.subheader("Simple Insights 💡")
                st.write(f"average saved per mission: {avg_save:.1f} coins")
                st.write(f"average spent per mission: {avg_spend:.1f} coins")
                st.write(f"current streak: {int(st.session_state.streak)} missions")
                st.write(f"Stars: {int(st.session_state.stars)} ⭐")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("no data yet. play at least one mission to generate a report.")
