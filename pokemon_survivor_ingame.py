import pygame
import random
import sys
import math
import time


# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Survivor")
clock = pygame.time.Clock()

# 글꼴 초기화
pygame.font.init()
font = pygame.font.Font(None, 36)  # 글꼴 크기를 36으로 설정

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
PLAYER_COLOR = (230, 40, 41)  # #E62829
ENEMY_COLOR = (235, 221, 204)  # #EBDDCC
ATTACK_COLOR = (239, 115, 116)  # #EF7374

# 이미지 로드
PLAYER_IMAGE = pygame.image.load("assets/player.png")
ENEMY_IMAGE = pygame.image.load("assets/enemy.png")
ATTACK_EFFECT_IMAGE = pygame.image.load("assets/attack_effect.png")
ATTACK_EFFECT2_IMAGE = pygame.image.load("assets/attack_effect2.png")
BACKGROUND_IMAGE = pygame.image.load("assets/background.png")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(PLAYER_IMAGE, (45, 45))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 2.5
        self.health = 10
        self.attack_damage = 50
        self.attack_range = 150
        self.attack_angle = 30
        self.last_attack_time = time.time()
        self.target_angle = 0
        self.show_attack_time = 0
        self.facing_right = False
        self.secondary_attack_enabled = False
        self.secondary_attack_last_time = time.time()
        self.projectiles = pygame.sprite.Group()

         # 강화 관련 초기화
        self.primary_attack_level = 1
        self.secondary_attack_level = 0
        self.projectile_count_level = 0
        self.attack_level = 0
        self.health_level = 0
        self.speed_level = 0
        self.attack_range_level = 0
        self.health_regen_level = 0

        # 체력 재생 관련
        self.max_health = 10
        self.current_health = 10
        self.health_regen_rate = 0
        self.last_health_regen_time = time.time()

        # 레벨 및 경험치
        self.level = 1
        self.current_exp = 0
        self.required_exp = self.calculate_required_exp()

    def calculate_required_exp(self):
        if self.level <= 10:
            return (self.level * 5) + 10
        elif self.level <= 20:
            return (self.level * 5) + 25
        else:
            return (self.level * 5) + 50

    def regenerate_health(self):
        if self.current_health < self.max_health:
            if time.time() - self.last_health_regen_time >= 5:
                self.current_health += 1 + self.health_regen_level
                self.current_health = min(self.current_health, self.max_health)
                self.last_health_regen_time = time.time()

    def enable_secondary_attack(self):
        self.secondary_attack_enabled = True

    def secondary_attack(self, enemies):
        if not self.secondary_attack_enabled:
            return

        if time.time() - self.secondary_attack_last_time < 5:
            return

        closest_enemies = self.find_closest_enemies(enemies, self.projectile_count_level + 1)
        for enemy in closest_enemies:
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)
            self.create_projectile(self.rect.centerx, self.rect.centery, angle)

        self.secondary_attack_last_time = time.time()

    def create_projectile(self, x, y, angle):
        base_size = 50
        size = int(base_size * (1.2 ** (self.secondary_attack_level // 2)))

        image = pygame.transform.scale(ATTACK_EFFECT2_IMAGE, (size, size))
        rect = image.get_rect(center=(x, y))
        speed = 4
        damage = 50 * (1.2 ** ((self.secondary_attack_level + 1) // 2))

        projectile = pygame.sprite.Sprite()
        projectile.image = image
        projectile.rect = rect
        projectile.angle = angle
        projectile.speed = speed
        projectile.damage = damage
        projectile.hit_enemies = set()  # 타격한 적을 기록할 집합

        self.projectiles.add(projectile)


    def update_projectiles(self, enemies):
        for projectile in list(self.projectiles):
            # 화염구 이동
            projectile.rect.x += math.cos(projectile.angle) * projectile.speed
            projectile.rect.y += math.sin(projectile.angle) * projectile.speed

            # 화면 밖으로 나가면 제거
            if (
                projectile.rect.right < 0
                or projectile.rect.left > WIDTH
                or projectile.rect.bottom < 0
                or projectile.rect.top > HEIGHT
            ):
                self.projectiles.remove(projectile)

            # 적과의 충돌 감지
            for enemy in enemies:
                if (
                    projectile.rect.colliderect(enemy.rect) and
                    enemy not in projectile.hit_enemies  # 이미 타격한 적은 제외
                ):
                    enemy.health -= projectile.damage
                    projectile.hit_enemies.add(enemy)  # 적을 타격한 적 목록에 추가

    def find_closest_enemies(self, enemies, count):
        distances = [
            (enemy, math.sqrt((self.rect.centerx - enemy.rect.centerx) ** 2 +
                              (self.rect.centery - enemy.rect.centery) ** 2))
            for enemy in enemies
        ]
        distances.sort(key=lambda x: x[1])
        return [enemy for enemy, _ in distances[:count]]

    def attack(self, enemies):
        if time.time() - self.last_attack_time < 1:
            return

        closest_enemies = self.find_closest_enemies(enemies, 1)
        if closest_enemies:
            closest_enemy = closest_enemies[0]
            dx = closest_enemy.rect.centerx - self.rect.centerx
            dy = closest_enemy.rect.centery - self.rect.centery
            self.target_angle = math.degrees(math.atan2(dy, dx))

            for enemy in enemies:
                dx = enemy.rect.centerx - self.rect.centerx
                dy = enemy.rect.centery - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                if distance <= self.attack_range:
                    angle = math.degrees(math.atan2(dy, dx)) - self.target_angle
                    angle = abs((angle + 180) % 360 - 180)
                    if angle <= self.attack_angle:
                        enemy.health -= self.attack_damage

            self.last_attack_time = time.time()
            self.show_attack_time = time.time()

    def update(self, keys, enemies=None):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.facing_right = True

        self.update_image_orientation()
        if enemies:
            self.update_projectiles(enemies)

    def update_image_orientation(self):
        if self.facing_right:
            self.image = pygame.transform.flip(
                pygame.transform.scale(PLAYER_IMAGE, (45, 45)), True, False
            )
        else:
            self.image = pygame.transform.scale(PLAYER_IMAGE, (45, 45))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        for projectile in self.projectiles:
            screen.blit(projectile.image, projectile.rect.topleft)

    def draw_health_bar(self, screen):
        bar_width = 60
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - (bar_height + 5)

        health_ratio = self.health / 10
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

        exp_ratio = self.current_exp / self.required_exp if self.required_exp > 0 else 0
        exp_bar_y = bar_y - (bar_height + 5)
        pygame.draw.rect(screen, (203, 152, 111), (bar_x, exp_bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 0), (bar_x, exp_bar_y, bar_width * exp_ratio, bar_height))

        level_text = font.render(f"Lv {self.level}", True, BLACK)
        screen.blit(level_text, (bar_x + bar_width // 2 - level_text.get_width() // 2, exp_bar_y - 20))

    def draw_attack_effect(self, screen):
        if time.time() - self.show_attack_time <= 0.2:
            rotated_effect = pygame.transform.rotate(ATTACK_EFFECT_IMAGE, -(self.target_angle + 90))
            rotated_rect = rotated_effect.get_rect()
            rotated_rect.center = (
                self.rect.centerx + math.cos(math.radians(self.target_angle)) * (rotated_rect.width // 2),
                self.rect.centery + math.sin(math.radians(self.target_angle)) * (rotated_rect.height // 2),
            )
            screen.blit(rotated_effect, rotated_rect.topleft)
    def add_exp(self, amount, screen, captured_screen):
        self.current_exp += amount
        while self.current_exp >= self.required_exp and self.level < 30:
            self.current_exp -= self.required_exp
            self.level += 1
            self.required_exp = self.calculate_required_exp()
            print(f"레벨 업! 현재 레벨: {self.level}")

            # 레벨 업 시 선택지 화면 호출
            handle_level_up(self, screen, captured_screen)

def draw_attack_effect2(screen, projectiles):
    for projectile in projectiles:
        # 화염구 이미지를 projectile.rect 위치에 그리기
        screen.blit(projectile.image, projectile.rect.topleft)

#적 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self, health, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (30, 30))  # 적 이미지
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([0, WIDTH - self.rect.width])
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.health = 50
        self.speed = 1  # 적 이동 속도
        self.damage = 5  # 적 데미지

    def update(self, player_pos):
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # 방향 벡터 정규화
            dx /= distance
            dy /= distance

            # 총 속도가 1을 넘지 않도록 제한
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            
#레벨업
def handle_level_up(player, screen, captured_screen):
    running = True
    selected = None
    start_time = time.time()

    # 선택지 랜덤화
    options = ["Attack increase", "Health increase", "Speed increase", "Attack range increase",
               "Health regeneration increase", "Projectile_increase", "Ember", "Fireball"]
    chosen_options = random.sample(options, 3)

    selected_upgrades = {}  # 선택한 업그레이드를 저장

    while running:
        blend_with_white(screen, captured_screen)  # 혼합 배경 표시

        # 선택지 표시
        for i, option in enumerate(chosen_options):
            create_button(option, WIDTH // 2 - 200, 200 + i * 100, 400, 70, GRAY, BLACK)

        # 남은 시간 표시
        elapsed_time = time.time() - start_time
        remaining_time = max(30 - elapsed_time, 0)
        time_bar_width = int((remaining_time / 30) * 400)
        pygame.draw.rect(screen, (255, 255, 0), (WIDTH // 2 - 200, 150, time_bar_width, 20))

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for i, option in enumerate(chosen_options):
                    if pygame.Rect(WIDTH // 2 - 200, 200 + i * 100, 400, 70).collidepoint(pos):
                        selected = option
                        selected_upgrades[option] = selected_upgrades.get(option, 0) + 1
                        running = False

        # 자동 선택 (30초 초과 시)
        if remaining_time <= 0:
            selected = chosen_options[0]
            selected_upgrades[selected] = selected_upgrades.get(selected, 0) + 1
            running = False

        pygame.display.flip()

    # 선택한 옵션 적용
    apply_level_up_choice(player, selected)

    # 선택한 업그레이드 정보 전달
    draw_selected_upgrades(screen, player)

#강화 선택지
def apply_level_up_choice(player, choice):
    """선택한 옵션에 따라 플레이어 능력치 변경"""
    if choice == "Ember":
        if player.primary_attack_level < 6:
            player.primary_attack_level += 1
            player.attack_damage *= 1.2 if player.primary_attack_level % 2 == 0 else 1
            player.attack_range *= 1.2 if player.primary_attack_level % 2 == 1 else 1
    elif choice == "Attack increase":
        if player.attack_level < 6:
            player.attack_damage += 5
            player.attack_level += 1
    elif choice == "Health increase":
        if player.health_level < 6:
            player.max_health += 5
            player.health_level += 1
    elif choice == "Speed increase":
        if player.speed_level < 6:
            player.speed += 0.1
            player.speed_level += 1
    elif choice == "Attack range increase":
        if player.attack_range_level < 6:
            player.attack_range += 20
            player.attack_range_level += 1
    elif choice == "Health regeneration increase":
        pass  # 체력 재생 로직은 이미 자동으로 적용됨
    elif choice == "Projectile_increase":
        if player.projectile_count_level < 3:
            player.projectile_count_level += 1
    elif choice == "Fireball":
        if not player.secondary_attack_enabled:
            player.enable_secondary_attack()  # 두 번째 공격 활성화
            player.secondary_attack_level += 1
        elif player.secondary_attack_level < 6:
            player.secondary_attack_level += 1

#강화 상태
def draw_selected_upgrades(screen, player):
    """
    게임 화면 좌측 하단에 플레이어의 능력치와 레벨을 표시합니다.

    Parameters:
        screen: Pygame 화면 객체
        player: Player 객체 (능력치 정보를 포함)
    """
    ICON_SIZE = 40  # 정사각형 아이콘 크기
    PADDING = 10    # 아이콘 간 간격
    START_X = 10    # 좌측 시작 X 좌표
    START_Y = HEIGHT - (ICON_SIZE + 10)  # 하단 시작 Y 좌표

    # 작은 폰트 정의
    small_font = pygame.font.Font(None, 16)

    # 플레이어 속성과 매핑된 업그레이드 데이터 정의
    upgrades = {
        "A": player.attack_level,
        "H": player.health_level,
        "S": player.speed_level,
        "R": player.attack_range_level,
        "HR": player.health_regen_level,
        "P": player.projectile_count_level,
        "F": player.secondary_attack_level,
        "E": player.primary_attack_level,
    }

    # 아이콘 이미지 매핑
    icons = {
        "E": ATTACK_EFFECT_IMAGE,    # 불꽃세례 이미지
        "F": ATTACK_EFFECT2_IMAGE    # 화염구 이미지
    }

     # 아이콘과 레벨 표시
    for index, (key, level) in enumerate(upgrades.items()):
        x = START_X + index * (ICON_SIZE + PADDING)

        # 아이콘 배경 그리기
        pygame.draw.rect(screen, (200, 200, 200), (x, START_Y, ICON_SIZE, ICON_SIZE))

        # 아이콘 표시
        if key in icons:  # 이미지로 표시
            icon_image = pygame.transform.scale(icons[key], (ICON_SIZE, ICON_SIZE))
            screen.blit(icon_image, (x, START_Y))
        else:  # 텍스트로 표시
            icon_text = font.render(key, True, BLACK)
            text_rect = icon_text.get_rect(center=(x + ICON_SIZE // 2, START_Y + ICON_SIZE // 2))
            screen.blit(icon_text, text_rect)

        # 레벨 표시 (작은 폰트 사용)
        level_text = small_font.render(str(level), True, BLACK)
        # 오른쪽 아래 끝으로 위치 설정
        level_rect = level_text.get_rect(bottomright=(x + ICON_SIZE - 2, START_Y + ICON_SIZE - 2))
        screen.blit(level_text, level_rect)
        screen.blit(level_text, level_rect)

def fade_out(screen):
    """페이드 아웃 효과"""
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    for alpha in range(0, 255, 5):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)

def fade_in(screen, new_background):
    """페이드 인 효과"""
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    for alpha in range(255, 0, -5):
        fade.set_alpha(alpha)
        screen.blit(new_background, (0, 0))
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)

#게임 오버 화면
def show_game_over_screen(final_score, survival_time, earned_gold):
    """게임 결과 화면 표시"""
    screen.fill(WHITE)

    # 결과 텍스트 표시
    game_over_text = font.render("Game Over!", True, BLACK)
    final_score_text = font.render(f"Final Score: {final_score}", True, BLACK)
    survival_time_text = font.render(f"Survival Time: {survival_time:.2f} seconds", True, BLACK)
    earned_gold_text = font.render(f"Gold Earned: {earned_gold}", True, BLACK)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(survival_time_text, (WIDTH // 2 - survival_time_text.get_width() // 2, HEIGHT // 2 + 50))
    screen.blit(earned_gold_text, (WIDTH // 2 - earned_gold_text.get_width() // 2, HEIGHT // 2 + 100))

    pygame.display.flip()

    # 대기 후 결과 화면 종료
    pygame.time.wait(3000)  # 3초 대기

#게임 클리어 화면
def show_clear_screen(screen, captured_screen, score, elapsed_time):
    """게임 클리어 화면을 표시합니다."""
    blend_with_white(screen, captured_screen)  # 혼합 배경 표시

    clear_text = font.render("Game Clear!", True, BLACK)
    score_text = font.render(f"Final Score: {score}", True, BLACK)
    time_text = font.render(f"Total Time: {int(elapsed_time // 60):02}:{int(elapsed_time % 60):02}", True, BLACK)

    screen.blit(clear_text, (WIDTH // 2 - clear_text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.flip()
    pygame.time.wait(5000)  # 5초간 대기

def capture_game_screen(screen):
    return screen.copy()

def blend_with_white(screen, captured_screen):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 128))  # 흰색, 반투명 (alpha=128)

    # 캡처된 화면과 흰색 오버레이를 혼합
    screen.blit(captured_screen, (0, 0))
    screen.blit(overlay, (0, 0))


# 버튼 생성 함수
def create_button(text, x, y, width, height, color, text_color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    label = font.render(text, True, text_color)
    screen.blit(label, (x + (width - label.get_width()) // 2, y + (height - label.get_height()) // 2))
    return pygame.Rect(x, y, width, height)

# 스프라이트 그룹 설정
player = Player()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(player)

# 점수 관련 변수
score = 0
score_increment = 100  # 초당 증가량
start_time = time.time()
last_score_update_time = start_time  # 마지막 점수 갱신 시간

# 게임 시작 시간 초기화
game_start_time = time.time()  # 게임 시작 시 기준 시간

# 골드 관련 변수 추가
gold_earned = 0  # 게임 중 획득한 골드

def run_game(slot_data):
    """게임 실행 함수"""
    global running
    running = True

    # 게임 초기화 변수
    start_time = time.time()
    last_score_update_time = start_time
    score = 0

    # 스프라이트 그룹 설정
    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)
    player.draw_health_bar(screen)

    # 시간 체크 변수
    enemy_health = 50  # 초기 적 체력
    enemy_image = ENEMY_IMAGE  # 초기 적 이미지
    background_image = BACKGROUND_IMAGE  # 초기 배경 이미지
    background_changed = False  # 배경 변경 여부 플래그

    captured_screen = capture_game_screen(screen)
    
    while running:
        elapsed_time = time.time() - start_time

        # 체력 변화
        if elapsed_time >= 30 and elapsed_time < 60:
            enemy_health = 75
        elif elapsed_time >= 60 and elapsed_time < 90:
            enemy_health = 100
        elif elapsed_time >= 120 and elapsed_time < 150:
            enemy_health = 150
        elif elapsed_time >= 150 and elapsed_time < 180:
            enemy_health = 200

        # 1분 30초에 배경 및 적 이미지 변경
        if elapsed_time >= 90 and not background_changed:
            fade_out(screen)  # 페이드 아웃
            background_image = pygame.image.load("assets/background2.png")  # 배경 변경
            enemy_image = pygame.image.load("assets/enemy2.png")  # 적 이미지 변경
            enemy_health = 125  # 적 체력 변경
            fade_in(screen, background_image)  # 페이드 인
            background_changed = True  # 변경 완료 플래그

        # 3분이 되면 게임 종료
        if elapsed_time >= 180:
            running = False
            show_clear_screen(screen, captured_screen, score, elapsed_time)  # 클리어 화면 표시
            break

        # 배경 그리기
        screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))
        # 적 처치 및 점수 처리
        for enemy in list(enemies):
            if enemy.health <= 0:
                score += 50  # 점수 추가
                captured_screen = capture_game_screen(screen)
                player.add_exp(5, screen, captured_screen)  # 경험치 추가
                enemies.remove(enemy)  # 적 제거
                all_sprites.remove(enemy)  # 모든 스프라이트에서도 제거

                
        # 생존 시간 계산 및 표시
        elapsed_time = time.time() - start_time
        minutes_passed = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        survival_time_str = f"{minutes_passed:02}:{seconds:02}"
        time_text = font.render(survival_time_str, True, BLACK)
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 10))

        # 초당 점수 증가량 업데이트
        score_increment = 100 + minutes_passed * 10

        # 1초마다 점수 갱신
        current_time = time.time()
        if current_time - last_score_update_time >= 1:
            score += score_increment
            last_score_update_time = current_time

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # 적 추가
        if random.random() < 0.03:
            enemy = Enemy(enemy_health, enemy_image)
            enemies.add(enemy)
            all_sprites.add(enemy)
            
        # 적 업데이트
        for enemy in enemies:
            enemy.update(player.rect.center)
            
        # 플레이어 업데이트
        keys = pygame.key.get_pressed()
        player.update(keys)
        player.draw_health_bar(screen)
        
        # 좌측 하단에 능력치 표시
        draw_selected_upgrades(screen, player)

        # 공격 수행
        player.attack(enemies) # 기본 공격
        player.secondary_attack( enemies)  # 두 번째 공격

        # 공격 이펙트 그리기
        player.draw_attack_effect(screen)

        # 화염구 업데이트 및 그리기
        player.update_projectiles(enemies)  # 화염구 업데이트
        draw_attack_effect2(screen, player.projectiles)  # 화염구 그리기

        # 충돌 감지 및 처리
        collided_enemies = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in collided_enemies:
            player.health -= enemy.damage
            enemy.kill()
            if player.health <= 0:
                running = False

        # 모든 스프라이트 그리기
        all_sprites.draw(screen)
    
        # 점수 표시
        score_text = font.render(f"Score: {int(score)}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # 게임 종료 후 결과 화면 표시
    earned_gold = score // 10  # 점수의 10%를 골드로 계산
    show_game_over_screen(score, time.time() - start_time, earned_gold)

    # 게임 결과 반환
    return {"score": score, "elapsed_time": time.time() - start_time, "gold_earned": earned_gold}
