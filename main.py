import pygame
import sys
import random
import sqlite3


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SCREEN_WIDTH, SCREEN_HEIGHT = 450, 692

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
JUMP_HEIGHT = 15
GRAVITY = 1

PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 10

'''
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.is_jumping = False
        self.jump_count = JUMP_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_count = JUMP_HEIGHT

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


class Platform:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
'''

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_jumping = False
        self.jump_count = 15
        self.score = 0

    def update_score(self):
        pass

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_count = JUMP_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)


class Platform:
    def __init__(self, existing_platforms):
        clear = False
        platform = None

        while not clear:
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = random.randint(100, SCREEN_HEIGHT - PLATFORM_HEIGHT)
            platform = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
            platform_aura = pygame.Rect(x - 20, y - 20, PLATFORM_WIDTH + 40, PLATFORM_HEIGHT + 40)

            clear = True
            for item in existing_platforms:
                if platform_aura.colliderect(item.rect):
                    clear = False
                    break

        self.rect = platform
        self.x = self.rect.x
        self.y = self.rect.y
        self.image = pygame.image.load('greenplatform.png').convert_alpha()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class MovingPlatform():
    pass


class CrashingPlatform(Platform):
    def __init__(self, existing_platforms):
        Platform.__init__(self, existing_platforms)
        self.existing_platforms = existing_platforms
        self.image = pygame.image.load('brownplatform.png').convert_alpha()
        self.crashed = False
        self.crash_animation_complete = False
        self.ySpeed = 12

    def crash(self):
        self.image = pygame.image.load('brownplatformbr.png').convert_alpha()
        self.crashed = True

    def move(self):
        if self.crashed and not self.crash_animation_complete:
            self.rect.y += self.ySpeed
            if self.rect.y >= SCREEN_HEIGHT:
                self.crash_animation_complete = True
                self.renew()

    def renew(self):
        self.image = pygame.image.load('brownplatform.png').convert_alpha()
        self.crashed = False
        self.crash_animation_complete = False

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.background_image = pygame.image.load("background.png")
        self.start_button_image = pygame.image.load("start.png")
        self.start_button_rect = self.start_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130))
        self.rating_button_image = pygame.image.load("rat.png")
        self.rating_button_rect = self.rating_button_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button_rect.collidepoint(event.pos):
                    return "game_active"
                elif self.rating_button_rect.collidepoint(event.pos):
                    return "rating_screen"
        return "start_screen"

    def update(self):
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.start_button_image, self.start_button_rect)
        self.screen.blit(self.rating_button_image, self.rating_button_rect)
        pygame.display.flip()


class GameScreen:
    def __init__(self, screen, db_instance):
        self.screen = screen
        self.db_instance = db_instance
        self.background_image = pygame.image.load("background.png")
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 20)
        #self.platforms = [
        #    Platform(random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH),
        #             random.randint(100, SCREEN_HEIGHT - PLATFORM_HEIGHT))
        #    if random.randint(0, 3) else CrashingPlatform(random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH),
        #                                           random.randint(100, SCREEN_HEIGHT - PLATFORM_HEIGHT)) for _ in range(10)]
        #self.platforms = [Platform(random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH),
        #             random.randint(100, SCREEN_HEIGHT - PLATFORM_HEIGHT)) for _ in range(10)]
        self.platforms = []
        for _ in range(10):
            if random.randint(0, 3):
                self.platforms.append(Platform(self.platforms))
            else:
                self.platforms.append(CrashingPlatform(self.platforms))
        self.font = pygame.font.Font(None, 36)
        self.score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        self.score_rect = self.score_text.get_rect(topleft=(10, 10))
        self.clock = pygame.time.Clock()
        self.in_game = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_LEFT] and self.player.rect.x > 0:
            self.player.move(-10, 0)
        if keys_pressed[pygame.K_RIGHT] and self.player.rect.x < SCREEN_WIDTH - PLAYER_WIDTH:
            self.player.move(10, 0)
        if self.player.rect.y > SCREEN_HEIGHT - PLAYER_HEIGHT and self.in_game:
            self.db_instance.insert_rating("Player1", self.player.score)
            return "game_over"
        self.player.jump()

    def update(self):
        self.screen.blit(self.background_image, (0, 0))
        if self.player.is_jumping:
            self.player.rect.y -= self.player.jump_count
            self.player.jump_count -= GRAVITY

        if self.player.rect.y <= SCREEN_HEIGHT // 2:
            for platform in self.platforms:
                platform.rect.y += 15
            self.player.rect.y += 15

        if not self.in_game and self.player.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT:
            self.player.is_jumping = False

        for platform in self.platforms:
            if platform.rect.y > SCREEN_HEIGHT:
                platform.rect.y = 0
                platform.rect.x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)

        for platform in self.platforms:
            if (self.player.rect.colliderect(platform.rect) and
                    self.player.rect.top <= platform.rect.top):
                if isinstance(platform, CrashingPlatform):
                    platform.crash()
                    self.player.is_jumping = True
                else:
                    self.player.is_jumping = False
                    self.player.rect.y = platform.rect.y - PLAYER_HEIGHT
                self.in_game = True

        for platform in self.platforms:
            if isinstance(platform, CrashingPlatform) and not platform.crash_animation_complete:
                platform.move()

        self.player.update_score()

        for platform in self.platforms:
            platform.draw(self.screen)
        self.player.draw(self.screen)
        self.screen.blit(self.score_text, self.score_rect)
        pygame.display.flip()
        self.clock.tick(30)


class FinalScreen:
    def __init__(self, screen):
        self.screen = screen
        self.background_image = pygame.image.load("background.png")
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render("Game Over. Click to restart.", True, (77, 156, 34))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return "start_screen"
        return "game_over"

    def update(self):
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 50))
        pygame.display.flip()


class RatingScreen:
    def __init__(self, screen, db_instance):
        self.screen = screen
        self.db_instance = db_instance
        self.font = pygame.font.Font(None, 36)
        self.ranking_data = sorted(self.fetch_ranking_data(), key=lambda x: x[1])
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
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button_rect.collidepoint(event.pos):
                    return "start_screen"
        return "rating_screen"

    def update(self):
        self.ranking_data = sorted(self.fetch_ranking_data(), key=lambda x: x[1])
        self.screen.fill(BLACK)
        text_y = 100

        image_width, image_height = self.back_image.get_size()

        x_position = (SCREEN_WIDTH - image_width) // 2 + 20
        y_position = (SCREEN_HEIGHT - image_height) // 2 - 20
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.back_image, (x_position, y_position))

        for rank, (username, score) in enumerate(self.ranking_data[:10], start=1):
            text = self.font.render(f"{rank}. {username}: {score}", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, text_y))
            self.screen.blit(text, text_rect)
            text_y += 40

        self.screen.blit(self.back_button_image, self.back_button_rect)
        pygame.display.flip()


class DBSample:
    def __init__(self):
        try:
            self.connection = sqlite3.connect("rating.db")
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
    final_screen = FinalScreen(screen)

    current_screen = start_screen

    rating_screen = RatingScreen(screen, db_instance)

    while True:
        current_screen.update()
        next_screen = current_screen.handle_events()
        if next_screen == "game_active":
            game_screen = GameScreen(screen, db_instance)
            current_screen = game_screen
        elif next_screen == "game_over":
            current_screen = final_screen
        elif next_screen == "start_screen":
            current_screen = start_screen
        elif next_screen == "rating_screen":
            current_screen = rating_screen


if __name__ == "__main__":
    main()