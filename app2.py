import streamlit as st
import random

# -----------------------------
# 초기 세션 상태 설정
# -----------------------------
def init_game():
    st.session_state.player = {
        "hp": 100,
        "max_hp": 100,
        "atk": 10,
        "def": 3,
        "gold": 20,
        "level": 1,
        "exp": 0,
        "max_exp": 30
    }

    st.session_state.monster = None
    st.session_state.page = "home"
    st.session_state.log = ["게임이 시작되었습니다!"]


if "player" not in st.session_state:
    init_game()

player = st.session_state.player


# -----------------------------
# 유틸 함수
# -----------------------------
def add_log(msg):
    st.session_state.log.append(msg)

def spawn_monster():
    monsters = [
        {"name": "슬라임", "hp": 30, "atk": 5, "def": 1, "reward": 10, "exp": 8},
        {"name": "고블린", "hp": 45, "atk": 8, "def": 2, "reward": 15, "exp": 12},
        {"name": "해골 병사", "hp": 60, "atk": 10, "def": 3, "reward": 18, "exp": 15},
        {"name": "오크 전사", "hp": 80, "atk": 14, "def": 5, "reward": 25, "exp": 20},
    ]
    st.session_state.monster = random.choice(monsters)
    add_log(f"🔥 몬스터 '{st.session_state.monster['name']}' 이(가) 나타났다!")


def level_up():
    player["level"] += 1
    player["max_hp"] += 20
    player["atk"] += 5
    player["def"] += 2
    player["hp"] = player["max_hp"]
    player["exp"] = 0
    player["max_exp"] += 15
    add_log(f"🎉 레벨 {player['level']} 달성! 능력치가 증가했습니다!")


# -----------------------------
# 전투 처리
# -----------------------------
def attack_monster():
    if st.session_state.monster is None:
        return

    monster = st.session_state.monster

    # 플레이어 공격
    dmg = max(1, player["atk"] - monster["def"])
    monster["hp"] -= dmg
    add_log(f"🗡️ 몬스터에게 {dmg}의 피해를 주었다!")

    if monster["hp"] <= 0:
        add_log(f"💀 {monster['name']} 처치! +{monster['reward']}골드, +{monster['exp']}EXP")
        player["gold"] += monster["reward"]
        player["exp"] += monster["exp"]
        st.session_state.monster = None

        # 레벨업 체크
        if player["exp"] >= player["max_exp"]:
            level_up()

        return

    # 몬스터 반격
    dmg_taken = max(1, monster["atk"] - player["def"])
    player["hp"] -= dmg_taken
    add_log(f"⚔️ 몬스터가 {dmg_taken}의 피해를 입혔다!")

    if player["hp"] <= 0:
        add_log("💥 당신은 쓰러졌습니다… 게임 오버")
        st.session_state.page = "home"
        init_game()


# -----------------------------
# 상점
# -----------------------------
def buy(item):
    if item == "포션(20G)" and player["gold"] >= 20:
        player["gold"] -= 20
        player["hp"] = min(player["max_hp"], player["hp"] + 40)
        add_log("🧪 체력이 40 회복되었습니다!")
    elif item == "공격력 +5 (40G)" and player["gold"] >= 40:
        player["gold"] -= 40
        player["atk"] += 5
        add_log("💪 공격력이 5 증가했습니다!")
    elif item == "방어력 +3 (40G)" and player["gold"] >= 40:
        player["gold"] -= 40
        player["def"] += 3
        add_log("🛡️ 방어력이 3 증가했습니다!")
    else:
        add_log("❌ 골드가 부족합니다!")


# -----------------------------
# UI - 사이드바 (플레이어 정보)
# -----------------------------
st.sidebar.title("🧙 플레이어 정보")
st.sidebar.write(f"HP: {player['hp']} / {player['max_hp']}")
st.sidebar.write(f"공격력: {player['atk']}")
st.sidebar.write(f"방어력: {player['def']}")
st.sidebar.write(f"골드: {player['gold']}")
st.sidebar.write(f"레벨: {player['level']}")
st.sidebar.write(f"EXP: {player['exp']} / {player['max_exp']}")


# -----------------------------
# 메인 페이지
# -----------------------------
st.title("⚔️ Streamlit RPG - 던전 탐험")

page = st.session_state.page

# ----------------- 홈 화면 -----------------
if page == "home":
    st.header("🏰 마을")
    if st.button("던전으로 출발"):
        st.session_state.page = "dungeon"

    st.write("---")
    st.subheader("🛒 상점")

    if st.button("포션(20G)"):
        buy("포션(20G)")
    if st.button("공격력 +5 (40G)"):
        buy("공격력 +5 (40G)")
    if st.button("방어력 +3 (40G)"):
        buy("방어력 +3 (40G)")

# ----------------- 던전 화면 -----------------
elif page == "dungeon":
    st.header("🌑 던전 탐험 중…")

    if st.session_state.monster is None:
        if st.button("❓ 몬스터와 조우하기"):
            spawn_monster()
    else:
        monster = st.session_state.monster
        st.subheader(f"⚠️ {monster['name']} 출현!")
        st.write(f"몬스터 HP: {monster['hp']}")

        if st.button("⚔️ 공격하기"):
            attack_monster()

        if st.button("🏃 도망가기"):
            st.session_state.monster = None
            add_log("🏃 도망쳤다!")

    if st.button("⬅️ 마을로 돌아가기"):
        st.session_state.page = "home"

# -----------------------------
# 로그 출력
# -----------------------------
st.write("---")
st.subheader("📜 로그")
for line in reversed(st.session_state.log[-10:]):
    st.write(line)
