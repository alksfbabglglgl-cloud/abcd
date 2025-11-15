import streamlit as st
import random

# -----------------------------
# 초기 설정
# -----------------------------
def init_game():
    st.session_state.player = {
        "name": "영웅",
        "level": 1,
        "exp": 0,
        "max_exp": 30,
        "hp": 100,
        "max_hp": 100,
        "atk": 10,
        "def": 5,
        "gold": 50,
        "inventory": [],
        "equip": {"weapon": None, "armor": None},
        "materials": {},
        "status_points": 0,
        "magic": None,
        "skills": []
    }
    st.session_state.page = "town"
    st.session_state.dungeon = None
    st.session_state.monster = None
    st.session_state.log = ["게임 시작!"]
    st.session_state.dungeons_cleared = []
    
if "player" not in st.session_state:
    init_game()

player = st.session_state.player

# -----------------------------
# 아이템 / 장비 / 재료
# -----------------------------
items = [
    {"name":"공격력 +1", "type":"equip", "stat":"atk", "value":1},
    {"name":"방어력 +1", "type":"equip", "stat":"def", "value":1},
    {"name":"회복포션", "type":"consumable", "stat":"hp", "value":40},
    {"name":"전설검", "type":"equip", "stat":"atk", "value":10},
    {"name":"마법방패", "type":"equip", "stat":"def", "value":8},
]

materials_list = ["나무", "철", "마력석", "화염석", "얼음정수"]

# -----------------------------
# 던전 / 몬스터
# -----------------------------
monsters = [
    {"name": "슬라임", "hp": 30, "atk": 5, "def": 1, "exp": 5, "gold": 5, "drops":[("회복포션",0.6), ("나무",0.5)]},
    {"name": "고블린", "hp": 50, "atk": 8, "def": 2, "exp": 12, "gold": 15, "drops":[("방어력 +1",0.35), ("철",0.4)]},
    {"name": "오크 전사", "hp": 80, "atk": 14, "def": 5, "exp": 20, "gold": 25, "drops":[("전설검",0.05), ("화염석",0.2)]},
    {"name": "해골 기사", "hp": 100, "atk": 18, "def": 6, "exp": 30, "gold": 40, "drops":[("마법방패",0.1), ("얼음정수",0.2)]},
]

dungeons = [
    {"name":"초원 던전","monsters":["슬라임","고블린"],"min_level":1,"boss":"오크 전사"},
    {"name":"숲 던전","monsters":["고블린","슬라임"],"min_level":3,"boss":"해골 기사"},
    {"name":"동굴 던전","monsters":["슬라임","오크 전사"],"min_level":5,"boss":"해골 기사"},
    {"name":"화산 던전","monsters":["오크 전사","해골 기사"],"min_level":7,"boss":"해골 기사"},
    {"name":"얼음 동굴","monsters":["슬라임","해골 기사"],"min_level":10,"boss":"오크 전사"},
]

# -----------------------------
# 로그 출력
# -----------------------------
def add_log(msg):
    st.session_state.log.append(msg)

# -----------------------------
# 몬스터 생성
# -----------------------------
def spawn_monster(dungeon):
    m_name = random.choice(dungeon["monsters"])
    monster = next((m.copy() for m in monsters if m["name"]==m_name), None)
    st.session_state.monster = monster
    add_log(f"{m_name} 출현!")

# -----------------------------
# 전투
# -----------------------------
def attack_monster():
    monster = st.session_state.monster
    if not monster:
        return
    dmg = max(1, player["atk"] - monster["def"])
    monster["hp"] -= dmg
    add_log(f"🗡️ {monster['name']}에게 {dmg} 피해!")
    
    if monster["hp"] <=0:
        add_log(f"💀 {monster['name']} 처치! {monster['gold']}골드, {monster['exp']}EXP 획득")
        player["gold"] += monster["gold"]
        player["exp"] += monster["exp"]
        for item_name, prob in monster["drops"]:
            if random.random() < prob:
                if item_name in materials_list:
                    player["materials"][item_name] = player["materials"].get(item_name,0)+1
                else:
                    player["inventory"].append(item_name)
                add_log(f"🎁 {item_name} 획득!")
        st.session_state.monster = None
        if player["exp"] >= player["max_exp"]:
            level_up()
        return

    dmg_taken = max(1, monster["atk"] - player["def"])
    player["hp"] -= dmg_taken
    add_log(f"⚔️ {monster['name']}가 {dmg_taken} 피해!")

    if player["hp"]<=0:
        add_log("💥 쓰러졌습니다. 게임 재시작")
        init_game()

# -----------------------------
# 레벨업 및 스테이터스 선택
# -----------------------------
def level_up():
    player["level"] +=1
    player["max_hp"] +=20
    player["hp"] = player["max_hp"]
    player["status_points"] +=3
    player["exp"] = 0
    player["max_exp"] += 20
    add_log(f"🎉 레벨 {player['level']} 달성! 스테이터스 포인트 3점 획득!")

# -----------------------------
# 장착/해제
# -----------------------------
def equip_item(item_name):
    item = next((i for i in items if i["name"]==item_name), None)
    if not item:
        return
    slot = "weapon" if item["stat"]=="atk" else "armor"
    if player["equip"][slot]:
        unequip_item(slot)
    player["equip"][slot] = item
    player[item["stat"]] += item["value"]
    player["inventory"].remove(item_name)
    add_log(f"{item_name} 장착!")

def unequip_item(slot):
    item = player["equip"][slot]
    if item:
        player[item["stat"]] -= item["value"]
        player["inventory"].append(item["name"])
        add_log(f"{item['name']} 해제")
        player["equip"][slot] = None

# -----------------------------
# 아이템 제작
# -----------------------------
def craft_item(recipe):
    can_craft = all(player["materials"].get(mat,0)>=count for mat,count in recipe["materials"].items())
    if can_craft:
        for mat,count in recipe["materials"].items():
            player["materials"][mat]-=count
        player["inventory"].append(recipe["result"])
        add_log(f"🎨 {recipe['result']} 제작 성공!")
    else:
        add_log("❌ 재료 부족!")

# -----------------------------
# UI
# -----------------------------
st.sidebar.title("🧙 플레이어 정보")
st.sidebar.write(f"레벨: {player['level']}  EXP: {player['exp']}/{player['max_exp']}")
st.sidebar.progress(player['hp']/player['max_hp'])
st.sidebar.write(f"HP: {player['hp']}/{player['max_hp']}")
st.sidebar.write(f"ATK: {player['atk']}  DEF: {player['def']}")
st.sidebar.write(f"골드: {player['gold']}")
st.sidebar.write(f"장착 무기: {player['equip']['weapon']['name'] if player['equip']['weapon'] else '없음'}")
st.sidebar.write(f"장착 방어구: {player['equip']['armor']['name'] if player['equip']['armor'] else '없음'}")
with st.sidebar.expander("인벤토리"):
    for item in player["inventory"]:
        st.write(item)
        if st.button(f"{item} 장착/사용", key=item):
            it = next((i for i in items if i["name"]==item), None)
            if it:
                if it["type"]=="equip":
                    equip_item(item)
                elif it["type"]=="consumable":
                    player["hp"] = min(player["max_hp"], player["hp"]+it["value"])
                    player["inventory"].remove(item)
                    add_log(f"{item} 사용! 체력 {it['value']} 회복")

with st.sidebar.expander("재료"):
    for mat, cnt in player["materials"].items():
        st.write(f"{mat}: {cnt}")

# -----------------------------
# 메인 페이지
# -----------------------------
st.title("🏰 Streamlit RPG - 고급판")

if st.session_state.page=="town":
    st.header("🛖 마을")
    st.write("마을에서 회복, 상점, 던전 입장 가능")
    col1,col2 = st.columns(2)
    with col1:
        if st.button("💊 회복"):
            player["hp"]=player["max_hp"]
            add_log("체력 회복!")
    with col2:
        st.subheader("🛒 상점")
        # 마을 레벨별 상점
        town_items = ["회복포션","공격력 +1"] if player["level"]<5 else ["회복포션","공격력 +1","전설검","마법방패"]
        for it in town_items:
            cost = 20 if "포션" in it else 50
            if st.button(f"{it} ({cost}G)"):
                if player["gold"]>=cost:
                    player["gold"]-=cost
                    player["inventory"].append(it)
                    add_log(f"{it} 구매!")
                else:
                    add_log("골드 부족!")

    st.subheader("던전 입장")
    for d in dungeons:
        if player["level"]>=d["min_level"]:
            if st.button(f"{d['name']} (Lv {d['min_level']} 이상)"):
                st.session_state.dungeon = d
                st.session_state.page="dungeon"
        else:
            st.write(f"{d['name']} (Lv {d['min_level']} 필요)")

elif st.session_state.page=="dungeon":
    dungeon = st.session_state.dungeon
    st.header(f"🌑 {dungeon['name']} 탐험")
    monster = st.session_state.monster
    if not monster:
        spawn_monster(dungeon)
    else:
        st.subheader(f"⚔️ {monster['name']} 출현")
        st.progress(monster['hp']/monster['hp'])
        col1,col2 = st.columns(2)
        with col1:
            if st.button("공격"):
                attack_monster()
        with col2:
            if st.button("도망"):
                st.session_state.monster = None
                add_log("도망쳤다!")

    if st.button("⬅️ 마을로 돌아가기"):
        st.session_state.page="town"

# -----------------------------
# 로그 출력
# -----------------------------
st.write("---")
st.subheader("📜 로그")
for line in reversed(st.session_state.log[-10:]):
    st.write(line)
