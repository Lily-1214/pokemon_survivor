import pokemon_survivor_ingame  # ingame 파일 임포트
import json
import pygame
import sys
from tkinter import messagebox
from tkinter import Tk

SAVE_FILE = "save_slots.json"
BACKGROUND_IMAGE = pygame.image.load("assets/background.png")

# 세이브 데이터 저장 및 로드
def save_slots_to_file():
    """슬롯 데이터를 파일에 저장"""
    with open(SAVE_FILE, "w") as f:
        json.dump(slots, f)

def load_slots_from_file():
    """파일에서 슬롯 데이터를 불러오기"""
    global slots
    try:
        with open(SAVE_FILE, "r") as f:
            slots = json.load(f)
    except FileNotFoundError:
        slots = [None, None, None]  # 기본 슬롯 초기화

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Survivor")
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# 글꼴 설정
font = pygame.font.Font(None, 50)

# 세이브 슬롯 데이터
slots = [None, None, None]  # 세이브 슬롯 3개 (None이면 빈 슬롯)

# 버튼 생성 함수
def create_button(text, x, y, width, height, color, text_color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    label = font.render(text, True, text_color)
    screen.blit(label, (x + (width - label.get_width()) // 2, y + (height - label.get_height()) // 2))
    return pygame.Rect(x, y, width, height)

# 알림창 표시
def show_message(title, message):
    root = Tk()
    root.withdraw()  # Tkinter 창 숨기기
    return messagebox.askyesno(title, message)  # "예" 또는 "아니오" 반환

def show_info(title, message):
    """확인 버튼만 있는 알림창"""
    root = Tk()
    root.withdraw()  # Tkinter 창 숨기기
    messagebox.showinfo(title, message)  # 확인 버튼만 있는 메시지

# 세이브 슬롯 화면
def save_slots_screen():
    load_slots_from_file()  # 시작 시 세이브 데이터 로드
    running = True
    while running:
        screen.blit(pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT)), (0, 0))

        # 슬롯 버튼 생성
        slot_buttons = []
        for i in range(3):
            slot_text = f"Slot {i + 1}: {'Empty' if slots[i] is None else 'Saved'}"
            slot_buttons.append(create_button(slot_text, 400, 150 + i * 100, 480, 70, GRAY, BLACK))

        # 종료 버튼 생성
        exit_button = create_button("Exit", WIDTH // 2 - 100, HEIGHT - 100, 200, 50, RED, WHITE)

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_slots_to_file()  # 종료 전 데이터 저장
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for i, button in enumerate(slot_buttons):
                    if button.collidepoint(pos):
                        if slots[i] is None:
                            result = show_message("New Game", "새로 시작하시겠습니까?")
                            if result:
                                slots[i] = {"level": 1, "attack": 10, "health": 100, "defense": 5, "speed": 2.5}
                                save_slots_to_file()  # 데이터 저장
                                main_screen(i)
                        else:
                            result = show_message("Load Game", "저장된 데이터를 플레이 하시겠습니까?")
                            if result:
                                main_screen(i)

                if exit_button.collidepoint(pos):
                    result = show_message("Exit Game", "게임을 종료하시겠습니까?")
                    if result:
                        save_slots_to_file()  # 종료 전 데이터 저장
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()

# 메인 화면
def main_screen(slot_index):
    running = True
    while running:
        screen.blit(pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT)), (0, 0))

        # 버튼 생성
        start_button = create_button("Start", 500, 200, 280, 70, GRAY, BLACK)
        upgrade_button = create_button("Upgrade", 500, 300, 280, 70, GRAY, BLACK)
        save_button = create_button("Save", 500, 400, 280, 70, GRAY, BLACK)
        back_button = create_button("Exit to Slots", 500, 500, 280, 70, RED, WHITE)

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_slots_to_file()  # 종료 전 데이터 저장
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if start_button.collidepoint(pos):
                    start_game(slot_index)
                if upgrade_button.collidepoint(pos):
                    upgrade_screen(slot_index)
                if save_button.collidepoint(pos):
                    save_slots_to_file()  # 데이터 저장
                    show_message("Save", "데이터가 저장되었습니다!")
                if back_button.collidepoint(pos):
                    return  # 슬롯 화면으로 돌아감
        pygame.display.flip()

# 능력 강화 화면
def upgrade_screen(slot_index):
    """강화 화면"""
    running = True

    while running:
        # 배경 이미지 출력
        screen.blit(pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT)), (0, 0))

        # 보유 골드 표시
        gold = slots[slot_index].get("gold", 0)
        gold_text = font.render(f"Gold: {gold}", True, BLACK)
        screen.blit(gold_text, (WIDTH // 2 - gold_text.get_width() // 2, 50))

        # 강화 레벨 및 비용 계산
        attack_level = slots[slot_index].get("attack_level", 0)
        health_level = slots[slot_index].get("health_level", 0)
        speed_level = slots[slot_index].get("speed_level", 0)

        attack_cost = 500 * (attack_level + 1) if attack_level < 6 else "MAX"
        health_cost = 500 * (health_level + 1) if health_level < 6 else "MAX"
        speed_cost = 500 * (speed_level + 1) if speed_level < 6 else "MAX"

        # 강화 버튼 및 레벨/비용 표시
        attack_button = create_button(f"Attack + (Lv {attack_level}) Cost: {attack_cost}", 400, 200, 480, 70, GRAY, BLACK)
        health_button = create_button(f"Health + (Lv {health_level}) Cost: {health_cost}", 400, 300, 480, 70, GRAY, BLACK)
        speed_button = create_button(f"Speed + (Lv {speed_level}) Cost: {speed_cost}", 400, 400, 480, 70, GRAY, BLACK)
        back_button = create_button("Back", 400, 500, 480, 70, RED, WHITE)

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_slots_to_file()  # 종료 전 데이터 저장
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                # 공격력 강화
                if attack_button.collidepoint(pos) and attack_level < 6:
                    if gold >= attack_cost:
                        result = show_message(
                            "Enhance Attack",
                            f"Upgrade Attack Level {attack_level} -> {attack_level + 1} for {attack_cost} Gold?"
                        )
                        if result:
                            slots[slot_index]["attack_level"] = attack_level + 1  # 레벨 증가
                            slots[slot_index]["gold"] -= attack_cost  # 골드 차감
                            slots[slot_index]["attack"] += 5  # 공격력 증가
                            save_slots_to_file()  # 슬롯 데이터 저장
                    else:
                        show_info("Error", "골드가 부족합니다!")

                # 체력 강화
                if health_button.collidepoint(pos) and health_level < 6:
                    if gold >= health_cost:
                        result = show_message(
                            "Enhance Health",
                            f"Upgrade Health Level {health_level} -> {health_level + 1} for {health_cost} Gold?"
                        )
                        if result:
                            slots[slot_index]["health_level"] = health_level + 1  # 레벨 증가
                            slots[slot_index]["gold"] -= health_cost  # 골드 차감
                            slots[slot_index]["health"] += 10  # 체력 증가
                            save_slots_to_file()  # 슬롯 데이터 저장
                    else:
                        show_info("Error", "골드가 부족합니다!")

                # 이동 속도 강화
                if speed_button.collidepoint(pos) and speed_level < 6:
                    if gold >= speed_cost:
                        result = show_message(
                            "Enhance Speed",
                            f"Upgrade Speed Level {speed_level} -> {speed_level + 1} for {speed_cost} Gold?"
                        )
                        if result:
                            slots[slot_index]["speed_level"] = speed_level + 1  # 레벨 증가
                            slots[slot_index]["gold"] -= speed_cost  # 골드 차감
                            slots[slot_index]["speed"] += 0.2  # 속도 증가
                            save_slots_to_file()  # 슬롯 데이터 저장
                    else:
                        show_info("Error", "골드가 부족합니다!")

                # 뒤로가기
                if back_button.collidepoint(pos):
                    return  # 메인 화면으로 복귀

        pygame.display.flip()



# 게임 실행
def start_game(slot_index):
    slot_data = slots[slot_index]
    result = pokemon_survivor_ingame.run_game(slot_data)

    # 게임 결과를 슬롯 데이터에 반영
    earned_gold = result.get("gold_earned", 0)
    slots[slot_index]["gold"] = slots[slot_index].get("gold", 0) + earned_gold
    save_slots_to_file()  # 저장

    main_screen(slot_index)


# 게임 시작
save_slots_screen()
