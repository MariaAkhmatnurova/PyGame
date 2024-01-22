import pygame
import sys
import random
import sqlite3


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SCREEN_WIDTH, SCREEN_HEIGHT = 450, 692

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
JUMP_HEIGHT = 18
GRAVITY = 1

PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 10
PLATFORMS_DIST = sum(range(JUMP_HEIGHT)) - PLATFORM_HEIGHT - 10


class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_jumping = False
        self.is_falling = False
        self.jump_count = JUMP_HEIGHT
        self.score = 0
        self.max_height = 0
        #self.image = pygame.image.load('character.png').convert_alpha()

    def update_score(self):
        self.score = self.max_height

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def jump(self, jh = JUMP_HEIGHT):

        #else:
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_count = jh

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        #screen.blit(self.image, (self.rect.x, self.rect.y))


class Platform:
    def __init__(self, image):
        self.rect = None
        self.x = None
        self.y = None
        self.image = pygame.image.load(image).convert_alpha()

    def place(self, x, y):
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.x = self.rect.x
        self.y = self.rect.y

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class MovingPlatform():
    pass


class CrashingPlatform(Platform):
    def __init__(self, image, image2):
        Platform.__init__(self, image)
        #self.image = pygame.image.load('brownplatform.png').convert_alpha()
        self.im = image
        self.image2 = image2
        self.crashed = False
        self.crash_animation_complete = False
        self.ySpeed = 12

    def crash(self):
        self.image = pygame.image.load(self.image2).convert_alpha()
        self.crashed = True

    def move(self):
        if self.crashed and not self.crash_animation_complete:
            self.rect.y += self.ySpeed
            if self.rect.y >= SCREEN_HEIGHT:
                self.crash_animation_complete = True
                self.renew()

    def renew(self):
        self.image = pygame.image.load(self.im).convert_alpha()
        self.crashed = False
        self.crash_animation_complete = False


class Platforms:
    def __init__(self, norm_image, crash_image_1, crash_image_2):
        self.normal_platforms = []
        self.last_y = SCREEN_HEIGHT
        while self.last_y >= -SCREEN_HEIGHT:
            platform = Platform(norm_image)
            self.place_normal_platform(platform)
            self.normal_platforms.append(platform)

        self.crashing_platforms = []
        for i in range( 7 ):
            platform = CrashingPlatform(crash_image_1, crash_image_2)
            self.place_crashing_platform(platform)
            self.crashing_platforms.append(platform)

    def place_normal_platform(self, platform):
        y = random.randint(self.last_y - PLATFORMS_DIST,
                            self.last_y - PLATFORMS_DIST//2 )
        x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
        platform.place(x, y)
        self.last_y = y + PLATFORM_HEIGHT + 10

    def place_crashing_platform(self, platform, min_y=-SCREEN_HEIGHT,
                                            max_y=SCREEN_HEIGHT - PLATFORM_HEIGHT):
        clear = False
        x = 0
        y = 0
        while not clear:
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = random.randint(min_y, max_y)
            platform_aura = pygame.Rect(x - 20, y - 20, PLATFORM_WIDTH + 40, PLATFORM_HEIGHT + 40)

            clear = True
            for item in self.normal_platforms:
                if platform_aura.colliderect(item.rect):
                    clear = False
                    break
            for item in self.crashing_platforms:
                if platform_aura.colliderect(item.rect):
                    clear = False
                    break
        platform.place(x, y)
        platform.renew()


    def all_down(self, up_value):
        for el in self.normal_platforms:
            el.rect.y += up_value
        self.last_y += up_value
        for el in self.crashing_platforms:
            el.rect.y += up_value


    def update(self):
        for platform in self.normal_platforms:
            if platform.rect.y > SCREEN_HEIGHT:
                self.place_normal_platform(platform)
        for platform in self.crashing_platforms:
            if platform.rect.y > SCREEN_HEIGHT:
                self.place_crashing_platform(platform,
                -SCREEN_HEIGHT + self.last_y, -SCREEN_HEIGHT)

    def draw(self, screen):
        for platform in self.normal_platforms:
            platform.draw(screen)
        for platform in self.crashing_platforms:
            platform.draw(screen)


class Monster:
    def __init__(self, platforms):
        self.image = pygame.image.load("monster.png").convert_alpha()
        self.platforms = platforms
        self.speed = 6
        self.place_monster()

    def place_monster(self):
        clear = False
        x = 0
        y = 0

        while not clear:
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = random.randint(-SCREEN_HEIGHT, 0)
            monster_width, monster_height = self.image.get_size()
            platform_aura = pygame.Rect(x - monster_width // 2, y - monster_height // 2,
                                        monster_width, monster_height)
            clear = True
            for item in self.platforms.normal_platforms:
                if platform_aura.colliderect(item.rect):
                    clear = False
                    break
            for item in self.platforms.crashing_platforms:
                if platform_aura.colliderect(item.rect):
                    clear = False
                    break

        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = self.rect.x
        self.y = self.rect.y

    def move(self):
        self.rect.x += self.speed
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speed = -self.speed

    def update(self):
        if self.rect.y > SCREEN_HEIGHT:
            self.place_monster()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.background_image = pygame.image.load("background.png")
        self.start_button_image = pygame.image.load("start.png")
        self.start_button_rect = self.start_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130))
        self.rating_button_image = pygame.image.load("rat_main.png")
        self.rating_button_rect = self.rating_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button_rect.collidepoint(event.pos):
                    #return "game_active"
                    return "level_screen"
                elif self.rating_button_rect.collidepoint(event.pos):
                    return "rating_screen"
        return "start_screen"

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.start_button_image, self.start_button_rect)
        self.screen.blit(self.rating_button_image, self.rating_button_rect)
        pygame.display.flip()


class LevelScreen:
    def __init__(self, screen):
        pygame.init()
        self.screen = screen

        self.background_image = pygame.image.load("background.png")
        self.font = pygame.font.Font(None, 36)

        self.normal_button = pygame.Rect(50, 50, 300, 50)

        self.normal_button_image = pygame.image.load("normal.png")
        self.gaser_button_image = pygame.image.load("gayser.png")

        self.normal_button_rect = self.normal_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130))
        self.gaser_button_rect = self.gaser_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.normal_button_rect.collidepoint(event.pos):
                    return "normal"
                elif self.gaser_button_rect.collidepoint(event.pos):
                    return "geyser"
        return "level_screen"

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))

        self.screen.blit(self.normal_button_image, self.normal_button_rect)
        self.screen.blit(self.gaser_button_image, self.gaser_button_rect)

        pygame.display.flip()


class GameScreen:
    def __init__(self, screen, db_instance):
        self.up_value = 0
        self.down_value = 0
        self.screen = screen
        self.db_instance = db_instance

        self.background_image = pygame.image.load("background.png")
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 20)
        self.back_button_image = pygame.image.load("back_lit.png")
        self.back_button_rect = self.back_button_image.get_rect(topleft=(10, 30))
        self.platforms = Platforms("greenplatform.png",
                "brownplatform.png", "brownplatformbr.png")

        self.font = pygame.font.Font(None, 36)
        self.score_text = self.font.render(f"Score: {self.player.score}", True, (77, 156, 34))
        self.score_rect = self.score_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.in_game = False
        self.return_str = "normal"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button_rect.collidepoint(event.pos):
                    return "start_screen"

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_LEFT] and self.player.rect.x > 0:
            self.player.move(-10, 0)
        if keys_pressed[pygame.K_RIGHT] and self.player.rect.x < SCREEN_WIDTH - PLAYER_WIDTH:
            self.player.move(10, 0)

        if self.player.rect.y > SCREEN_HEIGHT - PLAYER_HEIGHT and self.in_game:
            self.db_instance.insert_rating("Player1", self.player.score)
            return "game_over", self.return_str
        self.player.jump()

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.platforms.draw(self.screen)
        self.player.draw(self.screen)
        self.screen.blit(self.back_button_image, self.back_button_rect)
        self.screen.blit(self.score_text, self.score_rect)
        pygame.display.flip()

    def all_down(self, add):
        self.platforms.all_down(add)
        self.player.rect.y += add
        self.player.max_height -= add

    def update(self):
        #self.player.jump()
        if self.player.is_jumping:
            self.player.rect.y -= self.player.jump_count
            self.player.jump_count -= GRAVITY

        if not self.in_game and self.player.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT:
            self.player.is_jumping = False

        for platform in self.platforms.normal_platforms:
            if (self.player.rect.colliderect(platform.rect) and\
                    self.player.rect.top <= platform.rect.top and\
                    0 > self.player.jump_count):
                self.player.is_jumping = False
                self.player.rect.y = platform.rect.y - PLAYER_HEIGHT
                if SCREEN_HEIGHT - self.player.rect.y > self.player.max_height:
                    self.player.score += SCREEN_HEIGHT - self.player.rect.y - self.player.max_height
                    self.player.max_height = SCREEN_HEIGHT - self.player.rect.y
                self.in_game = True

        for platform in self.platforms.crashing_platforms:
            if (self.player.rect.colliderect(platform.rect) and\
                    self.player.rect.top <= platform.rect.top and\
                    0 > self.player.jump_count):
                platform.crash()
                self.player.is_jumping = True
                self.in_game = True
            platform.move()

        self.score_text = self.font.render(f"Score: {self.player.score}", True, (77, 156, 34))

        if self.player.rect.y <= 0:  # опускаем быстро
            self.all_down(JUMP_HEIGHT)
        elif self.player.rect.y <= SCREEN_HEIGHT // 2 \
                and self.down_value == 0:  # опускаем  медленно
            self.down_value = JUMP_HEIGHT
        if self.down_value > 0:
            add = min(JUMP_HEIGHT // 2, self.down_value)
            self.all_down(add)
            self.down_value -= add

        self.platforms.update()


class GeyserGameScreen(GameScreen):
    def __init__(self, screen, db_instance):
        GameScreen.__init__(self, screen, db_instance)
        self.background_image = pygame.image.load("background2.png")
        self.platforms = Platforms("yellowplatform.png",
            "blackplatform.png", "blackplatformbr.png")
        self.return_str = "geyser"
        self.monster = None

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.platforms.draw(self.screen)
        self.player.draw(self.screen)
        if self.monster:
            self.monster.draw(self.screen)
        self.screen.blit(self.back_button_image, self.back_button_rect)
        self.screen.blit(self.score_text, self.score_rect)
        pygame.display.flip()

    def all_down(self, add):
        GameScreen.all_down(self, add)
        if self.monster:
            self.monster.rect.y += add

    def update(self):
        #self.player.jump()
        if self.player.is_jumping:
            self.player.rect.y -= self.player.jump_count
            self.player.jump_count -= GRAVITY

        if not self.in_game and self.player.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT:
            self.player.is_jumping = False

        for platform in self.platforms.normal_platforms:
            if (self.player.rect.colliderect(platform.rect) and\
                    self.player.rect.top <= platform.rect.top and\
                    0 > self.player.jump_count):
                if not self.player.is_falling:
                    self.player.is_jumping = False
                    self.player.rect.y = platform.rect.y - PLAYER_HEIGHT
                    if SCREEN_HEIGHT - self.player.rect.y > self.player.max_height:
                        self.player.score += SCREEN_HEIGHT - self.player.rect.y - self.player.max_height
                        self.player.max_height = SCREEN_HEIGHT - self.player.rect.y
                    self.in_game = True

        for platform in self.platforms.crashing_platforms:
            if (self.player.rect.colliderect(platform.rect) and\
                    self.player.rect.top <= platform.rect.top and\
                    0 > self.player.jump_count):
                if not self.player.is_falling:
                    platform.crash()
                    self.player.is_jumping = True
                    self.in_game = True
            platform.move()

        if self.player.score > 1500 and not self.monster:
            self.monster = Monster(self.platforms)

        if self.monster:
            self.monster.move()
            if self.player.rect.colliderect(self.monster.rect):
                self.player.is_falling = True

        self.score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)

        if self.player.rect.y <= 0:  # опускаем быстро
            self.all_down(JUMP_HEIGHT)
        elif self.player.rect.y <= SCREEN_HEIGHT // 2 \
                and self.down_value == 0:  # опускаем  медленно
            self.down_value = JUMP_HEIGHT
        if self.down_value > 0:
            add = min(JUMP_HEIGHT // 2, self.down_value)
            self.all_down(add)
            self.down_value -= add

        self.platforms.update()
        if self.monster:
            self.monster.update()


class FinalScreen:
    def __init__(self, screen, last_screen="normal"):
        self.screen = screen
        self.last_screen = last_screen
        self.background_image = pygame.image.load("background.png")
        self.home_button_image = pygame.image.load("home.png")
        self.home_button_rect = self.home_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
        self.font = pygame.font.SysFont("Comic Sans", 44)
        self.text = self.font.render("Game Over!", True, (77, 156, 34))
        self.text2 = self.font.render("Click to restart.", True, (77, 156, 34))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.home_button_rect.collidepoint(event.pos):
                    return "start_screen"
                return self.last_screen

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 120))
        self.screen.blit(self.text2, (SCREEN_WIDTH // 2 - 155, SCREEN_HEIGHT // 2 - 70))
        self.screen.blit(self.home_button_image, self.home_button_rect)
        pygame.display.flip()


class RatingScreen:
    def __init__(self, screen, db_instance):
        self.screen = screen
        self.db_instance = db_instance
        self.font = pygame.font.SysFont("Comic Sans", 28)
        self.font2 = pygame.font.SysFont("Comic Sans", 38)
        self.ranking_data = sorted(self.fetch_ranking_data(), key=lambda x: x[1], reverse=True)
        self.background_image = pygame.image.load("background.png")
        self.back_image = pygame.image.load("rating.png").convert_alpha()
        self.back_image.set_alpha(220)
        self.back_button_image = pygame.image.load("back.png")
        self.back_button_rect = self.back_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

    def fetch_ranking_data(self):
        try:
            table_name = "рейтинг"
            self.db_instance.cursor.execute(f"SELECT * FROM {table_name} ORDER BY счет DESC")
            ranking_data = self.db_instance.cursor.fetchall()
            return ranking_data
        except sqlite3.Error as e:
            print("Error fetching ranking data:", e)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button_rect.collidepoint(event.pos):
                    return "start_screen"
        return "rating_screen"

    def update(self):
        pass

    def draw(self):
        self.screen.fill(BLACK)
        text_y = 150

        image_width, image_height = self.back_image.get_size()

        x_position = (SCREEN_WIDTH - image_width) // 2 + 20
        y_position = (SCREEN_HEIGHT - image_height) // 2 - 20
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.back_image, (x_position, y_position))

        text = self.font2.render("Rating", True, (77, 156, 34))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(text, text_rect)

        for rank, (username, score) in enumerate(self.ranking_data[:10], start=1):
            text = self.font.render(f"{rank}. {username}           {score}", True, (77, 156, 34))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, text_y))
            self.screen.blit(text, text_rect)
            text_y += 40

        self.screen.blit(self.back_button_image, self.back_button_rect)
        pygame.display.flip()


class DBSample:
    def __init__(self):
        try:
            self.connection = sqlite3.connect("rat.db")
            self.cursor = self.connection.cursor()
            # Создаем таблицы рейтинга, если ее нет
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS рейтинг (
                                                        имя TEXT,
                                                        счет INTEGER)''')
        except sqlite3.Error as e:
            print("Error creating table:", e)

        self.connection.commit()

    # Метод для добавления рейтинга в базу данных
    def insert_rating(self, username, value):
        try:
            table_name = "рейтинг"
            self.cursor.execute(f"INSERT INTO {table_name} (имя, счет) VALUES (?, ?)", (username, value))
            self.connection.commit()
        except sqlite3.Error as e:
            print("Error inserting rating:", e)

    # Закрытие базы данных при завершении работы приложения
    def close_database(self):
        if self.connection:
            self.connection.close()


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    db_instance = DBSample()

    start_screen = StartScreen(screen)
    game_screen = GameScreen(screen, db_instance)
    geyser_screen = GeyserGameScreen(screen, db_instance)
    final_screen = FinalScreen(screen)
    level_screen = LevelScreen(screen)

    current_screen = start_screen

    rating_screen = RatingScreen(screen, db_instance)

    clock = pygame.time.Clock()

    while True:
        next_screen = current_screen.handle_events()
        if next_screen:
            if "game_over" in next_screen:
                next_screen, last_screen = next_screen

        if next_screen == "normal":
            game_screen = GameScreen(screen, db_instance)
            current_screen = game_screen
        elif next_screen == "game_over":
            final_screen = FinalScreen(screen, last_screen)
            current_screen = final_screen
        elif next_screen == "start_screen":
            current_screen = start_screen
        elif next_screen == "rating_screen":
            current_screen = rating_screen
        elif next_screen == "level_screen":
            current_screen = level_screen
        elif next_screen == "geyser":
            geyser_screen = GeyserGameScreen(screen, db_instance)
            current_screen = geyser_screen
        elif next_screen == "quit":
            db_instance.close_database()
            pygame.quit()
            sys.exit()
            return

        current_screen.update()
        current_screen.draw()
        clock.tick(30)


if __name__ == "__main__":
    main()
