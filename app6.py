import streamlit as st
import random

# -------------------------------
# 초기 데이터 설정
# -------------------------------
if 'player' not in st.session_state:
    st.session_state.player = {
        'name': '모험가',
        'level': 1,
        'exp': 0,
        'hp': 100,
        'max_hp': 100,
        'atk': 10,
        'defense': 5,
        'gold': 100,
        'inventory': [],
        'equipment': {'weapon': None, 'armor': None},
        'status_points': 0,
        'magic': None,
        'skills': []
    }

if 'log' not in st.session_state:
    st.session_state.log = []

if 'dungeon' not in st.session_state:
    st.session_state.dungeon = None

if 'materials' not in st.session_state:
    st.session_state.materials = {'풀':0, '나무':0, '돌':0, '화염석':0, '얼음정수':0}

# -------------------------------
# 몬스터 데이터
# -------------------------------
MONSTERS = {
    '초원': [{'name':'슬라임', 'hp':20, 'atk':5, 'drop':{'풀':0.5, '희귀검':0.05}}],
    '숲': [{'name':'늑대', 'hp':35, 'atk':10, 'drop':{'나무':0.6, '희귀방패':0.05}}],
    '동굴': [{'name':'고블린', 'hp':50, 'atk':15, 'drop':{'돌':0.5, '희귀투구':0.03}}],
    '화산': [{'name':'화염마', 'hp':70, 'atk':25, 'drop':{'화염석':0.5, '전설검':0.01}}],
    '얼음동굴': [{'name':'얼음정령', 'hp':60, 'atk':20, 'drop':{'얼음정수':0.5, '전설방어구':0.01}}]
}

# -------------------------------
# 던전 최소 레벨
# -------------------------------
DUNGEON_LEVEL_REQ = {
    '초원': 1,
    '숲': 3,
    '동굴': 5,
    '화산': 8,
    '얼음동굴': 10
}

# -------------------------------
# 상점 데이터
# -------------------------------
SHOP_ITEMS = {
    '초급': [{'name':'작은 포션','price':10,'type':'potion','value':50}],
    '중급': [{'name':'중간 포션','price':30,'type':'potion','value':100}],
    '상급': [{'name':'큰 포션','price':100,'type':'potion','value':250}]
}

# -------------------------------
# 탐험 맵 레벨 제한
# -------------------------------
EXPLORATION_MAPS = {
    '초원': {'level_req':1, 'materials':['풀','나무']},
    '숲': {'level_req':3, 'materials':['나무','돌']},
    '동굴': {'level_req':5, 'materials':['돌','화염석']},
    '화산': {'level_req':8, 'materials':['화염석','전설재료']},
    '얼음동굴': {'level_req':10, 'materials':['얼음정수','전설재료']}
}

# -------------------------------
# 유틸리티 함수
# -------------------------------
def log(msg):
    st.session_state.log.append(msg)
    if len(st.session_state.log) > 10:
        st.session_state.log.pop(0)

def level_up():
    player = st.session_state.player
    while player['exp'] >= player['level']*50:
        player['exp'] -= player['level']*50
        player['level'] += 1
        player['status_points'] += 5
        player['max_hp'] += 10
        player['hp'] = player['max_hp']
        log(f"레벨업! 현재 레벨 {player['level']}. 스테이터스 포인트 5 획득.")

def equip(item):
    player = st.session_state.player
    if item['type'] in ['weapon','armor']:
        player['equipment'][item['type']] = item
        log(f"{item['name']} 장착 완료!")

def unequip(slot):
    player = st.session_state.player
    if player['equipment'][slot]:
        log(f"{player['equipment'][slot]['name']} 해제!")
        player['equipment'][slot] = None

# -------------------------------
# UI 시작
# -------------------------------
st.title("🗡️ Streamlit RPG 모험 게임")

tab = st.sidebar.radio("메뉴", ['마을','던전','탐험','제작','상태창'])

player = st.session_state.player

# -------------------------------
# 마을 탭
# -------------------------------
if tab=='마을':
    st.subheader("🏘️ 마을")
    if player['level']<5:
        town_level = '초급'
    elif player['level']<10:
        town_level = '중급'
    else:
        town_level = '상급'
    st.write(f"현재 마을: {town_level}")

    if st.button("회복"):
        player['hp'] = player['max_hp']
        log("HP 전부 회복!")

    if st.button("상점"):
        st.subheader("🛒 상점")
        items = SHOP_ITEMS[town_level]
        for i, item in enumerate(items):
            st.write(f"{item['name']} - 가격: {item['price']}골드")
            if st.button(f"{item['name']} 구매", key=f"buy{i}"):
                if player['gold']>=item['price']:
                    player['gold'] -= item['price']
                    player['inventory'].append(item)
                    log(f"{item['name']} 구매 완료!")
                else:
                    log("골드가 부족합니다!")

    if st.button("다음 던전으로 이동"):
        st.session_state.dungeon = None
        log("다음 던전으로 이동 준비 완료!")

# -------------------------------
# 던전 탭
# -------------------------------
elif tab=='던전':
    st.subheader("🗺️ 던전")
    for dun in MONSTERS.keys():
        req = DUNGEON_LEVEL_REQ[dun]
        if player['level']>=req:
            st.write(f"{dun} 던전 (최소 레벨 {req})")
            if st.button(f"{dun} 입장"):
                st.session_state.dungeon = dun
                log(f"{dun} 던전 입장!")
        else:
            st.write(f"{dun} 던전 (최소 레벨 {req}) - 레벨 부족")

    # 던전 전투
    if st.session_state.dungeon:
        monster = random.choice(MONSTERS[st.session_state.dungeon])
        st.write(f"🧟 몬스터 등장: {monster['name']} HP:{monster['hp']} ATK:{monster['atk']}")

        if st.button("공격"):
            damage = player['atk']
            monster['hp'] -= damage
            log(f"{monster['name']}에게 {damage} 피해!")
            if monster['hp']<=0:
                log(f"{monster['name']} 처치!")
                # 드랍
                for item, prob in monster['drop'].items():
                    if random.random()<prob:
                        if item in st.session_state.materials:
                            st.session_state.materials[item]+=1
                        else:
                            player['inventory'].append({'name':item})
                        log(f"{item} 획득!")
                player['exp'] += 20
                level_up()
        if st.button("도망"):
            log("도망쳤습니다!")

# -------------------------------
# 탐험 탭
# -------------------------------
elif tab=='탐험':
    st.subheader("🌲 탐험")
    # 탐험 가능 맵 표시
    available_maps = [m for m, info in EXPLORATION_MAPS.items() if player['level']>=info['level_req']]
    for emap in available_maps:
        if st.button(f"{emap} 탐험"):
            material = random.choice(EXPLORATION_MAPS[emap]['materials'])
            if material in st.session_state.materials:
                st.session_state.materials[material] +=1
            else:
                st.session_state.materials[material] =1
            log(f"{emap} 탐험: {material} 1개 획득!")

# -------------------------------
# 제작 탭
# -------------------------------
elif tab=='제작':
    st.subheader("⚒️ 제작")
    st.write("재료 현황:")
    st.write(st.session_state.materials)

    if st.button("포션 제작 (풀 2개)"):
        if st.session_state.materials.get('풀',0)>=2:
            st.session_state.materials['풀']-=2
            player['inventory'].append({'name':'포션','type':'potion','value':50})
            log("포션 제작 완료!")
        else:
            log("재료 부족!")

# -------------------------------
# 상태창 탭
# -------------------------------
elif tab=='상태창':
    st.subheader("📊 상태창")
    st.write(f"이름: {player['name']}")
    st.write(f"레벨: {player['level']} (EXP:{player['exp']})")
    st.write(f"HP: {player['hp']}/{player['max_hp']}")
    st.write(f"ATK: {player['atk']}, DEF: {player['defense']}")
    st.write(f"골드: {player['gold']}")
    st.write(f"장착: {player['equipment']}")
    st.write(f"인벤토리: {[i['name'] for i in player['inventory']]}")
    st.write(f"스킬: {player['skills']}")
    st.write(f"마법 속성: {player['magic']}")
    st.write(f"재료: {st.session_state.materials}")

# -------------------------------
# 로그 표시
# -------------------------------
st.subheader("📝 로그")
for msg in st.session_state.log:
    st.write(msg)
