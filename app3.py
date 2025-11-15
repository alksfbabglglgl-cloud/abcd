import streamlit as st
import random

# -----------------------------
# 초기 세션 상태 설정
# -----------------------------
def init_game():
    # 플레이어 기본 정보
    st.session_state.player = {
        "name": "영웅",
        "hp": 100,
        "max_hp": 100,
        "atk": 10,
        "def": 5,
        "gold": 50,
        "level": 1,
        "exp": 0,
        "max_exp": 30,
        "inventory": [],
        "equip": {"weapon": None, "armor": None},
    }
    st.session_state.page = "town"
    st.session_state.current_dungeon = None
    st.session_state.monster = None
    st.session_state.log = ["게임을 시작합니다!"]
    st.session_state.dungeons_cleared = []

if "player" not in st.session_state:
    init_game()

player = st.session_state.player

# -----------------------------
# 데이터 정의
# -----------------------------

# 아이템
items = [
    {"name":"공격력 +1", "type":"equip", "stat":"atk", "value":1},
    {"name":"방어력 +1", "type":"equip", "stat":"def", "value":1},
    {"name":"회복포션", "type":"consumable", "stat":"hp", "value":40},
    {"name":"전설검", "type":"equip", "stat":"atk", "value":10},
    {"name":"마법방패", "type":"equip", "stat":"def", "value":8},
]

# 몬스터
monsters = [
    {"name": "슬라임", "hp": 30, "atk": 5, "def": 1, "exp": 5, "gold": 5, 
     "drops":[("회복포션", 0.6), ("공격력 +1", 0.3), ("전설검", 0.1)]},
    {"name": "고블린", "hp": 50, "atk": 8, "def": 2, "exp": 12, "gold": 15, 
     "drops":[("회복포션", 0.5), ("방어력 +1", 0.35), ("마법방패", 0.15)]},
    {"name": "오크 전사", "hp": 80, "atk": 14, "def": 5, "exp": 20, "gold": 25, 
     "drops":[("회복포션",0.4), ("공격력 +1",0.4), ("전설검",0.2)]},
    {"name": "해골 기사", "hp": 100, "atk": 18, "def": 6, "exp": 30, "gold": 40,
     "drops":[("회복포션",0.3), ("마법방패",0.4), ("전설검",0.3)]},
]

# 던전
dungeons = [
    {"name":"초원 던전", "monsters":["슬라임","고블린"], "min_level":1},
    {"name":"숲 던전", "monsters":["고블린","해골 기사"], "min_level":2},
    {"name":"화산 던전", "monsters":["오크 전사","해골 기사"], "min_level":5},
]

# -----------------------------
# 유틸 함수
# -----------------------------
def add_log(msg):
    st.session_state.log.append(msg)

def get_monster_data(name):
    for m in monsters:
        if m["name"] == name:
            return m.copy()
    return None

def spawn_monster(dungeon):
    monster_name = random.choice(dungeon["monsters"])
    st.session_state.monster = get_monster_data(monster_name)
    add_log(f"🔥 몬스터 '{monster_name}' 출현!")

def drop_items(monster):
    drops = []
    for item_name, prob in monster["drops"]:
        if random.random() < prob:
            drops.append(item_name)
            player["inventory"].append(item_name)
    return drops

def level_up():
    player["level"] += 1
    player["max_hp"] += 20
    player["atk"] += 5
    player["def"] += 3
    player["hp"] = player["max_hp"]
    player["exp"] = 0
    player["max_exp"] += 20
    add_log(f"🎉 레벨 {player['level']} 달성! 능력치 상승!")

# -----------------------------
# 전투 시스템
# -----------------------------
def attack_monster():
    monster = st.session_state.monster
    if not monster:
        return

    dmg = max(1, player["atk"] - monster["def"])
    monster["hp"] -= dmg
    add_log(f"🗡️ 몬스터에게 {dmg} 피해를 주었다!")

    if monster["hp"] <= 0:
        add_log(f"💀 {monster['name']} 처치! +{monster['gold']}골드, +{monster['exp']}EXP")
        player["gold"] += monster["gold"]
        player["exp"] += monster["exp"]
        drops = drop_items(monster)
        if drops:
            add_log(f"🎁 드랍 아이템: {', '.join(drops)}")
        st.session_state.monster = None
        if player["exp"] >= player["max_exp"]:
            level_up()
        return

    dmg_taken = max(1, monster["atk"] - player["def"])
    player["hp"] -= dmg_taken
    add_log(f"⚔️ 몬스터가 {dmg_taken} 피해를 입혔다!")

    if player["hp"] <= 0:
        add_log("💥 당신은 쓰러졌습니다… 게임 오버")
        init_game()

# -----------------------------
# 상점 / 강화 / 소비 아이템
# -----------------------------
def use_item(item_name):
    for i, it in enumerate(player["inventory"]):
        if it == item_name:
            item = next((x for x in items if x["name"]==it), None)
            if not item:
                return
            if item["type"]=="consumable":
                if item["stat"]=="hp":
                    player["hp"] = min(player["max_hp"], player["hp"] + item["value"])
                    add_log(f"🧪 {item_name} 사용! 체력 {item['value']} 회복")
                player["inventory"].pop(i)
            elif item["type"]=="equip":
                if item["stat"]=="atk":
                    player["atk"] += item["value"]
                elif item["stat"]=="def":
                    player["def"] += item["value"]
                player["equip"][item_name] = item
                add_log(f"⚔️ {item_name} 장착! {item['stat']} +{item['value']}")
                player["inventory"].pop(i)
            break

# -----------------------------
# UI
# -----------------------------
st.sidebar.title("🧙 플레이어 정보")
st.sidebar.write(f"레벨: {player['level']}  EXP: {player['exp']}/{player['max_exp']}")
st.sidebar.progress(player['hp']/player['max_hp'])
st.sidebar.write(f"HP: {player['hp']}/{player['max_hp']}")
st.sidebar.write(f"ATK: {player['atk']}  DEF: {player['def']}")
st.sidebar.write(f"골드: {player['gold']}")
with st.sidebar.expander("인벤토리"):
    for item in player["inventory"]:
        st.write(item)
        if st.button(f"{item} 사용", key=item):
            use_item(item)

# -----------------------------
# 메인 페이지
# -----------------------------
st.title("🏰 Streamlit RPG 업그레이드판")

if st.session_state.page=="town":
    st.header("🛖 마을")
    st.write("마을에서 회복하거나 상점을 이용하고, 던전을 탐험할 수 있습니다.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💊 회복", key="heal"):
            player["hp"] = player["max_hp"]
            add_log("🧪 체력 완전 회복!")

    with col2:
        st.subheader("🛒 상점")
        for it in ["공격력 +1", "방어력 +1", "회복포션"]:
            cost = 20
            if st.button(f"{it} ({cost}G)"):
                if player["gold"] >= cost:
                    player["gold"] -= cost
                    player["inventory"].append(it)
                    add_log(f"{it} 구매 완료!")
                else:
                    add_log("❌ 골드 부족!")

    st.write("---")
    st.subheader("던전 입장")
    for d in dungeons:
        if player["level"]>=d["min_level"]:
            if st.button(f"{d['name']} (Lv {d['min_level']} 이상)"):
                st.session_state.current_dungeon = d
                st.session_state.page="dungeon"

elif st.session_state.page=="dungeon":
    dungeon = st.session_state.current_dungeon
    st.header(f"🌑 {dungeon['name']} 탐험 중")
    monster = st.session_state.monster

    if not monster:
        if st.button("❓ 몬스터와 조우"):
            spawn_monster(dungeon)
    else:
        st.subheader(f"⚔️ {monster['name']} 출현!")
        st.progress(monster['hp']/100)
        st.write(f"HP: {monster['hp']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("공격"):
                attack_monster()
        with col2:
            if st.button("도망가기"):
                st.session_state.monster = None
                add_log("🏃 도망쳤다!")

    if st.button("⬅️ 마을로 돌아가기"):
        st.session_state.page="town"

st.write("---")
st.subheader("📜 로그")
for line in reversed(st.session_state.log[-10:]):
    st.write(line)
