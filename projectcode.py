import pygame
from pygame.locals import *
import random

# Initialize pygame and its mixer for audio
pygame.init()
pygame.mixer.init()

# Load Background Music and Crash Sound
pygame.mixer.music.load('sounds/background.mp3')  # Replace with your background music file
crash_sound = pygame.mixer.Sound('sounds/crash.mp3')  # Replace with your crash sound effect

# Screen settings
width, height = 500, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Car Game')

# Colors
gray, green, red, white, yellow, black = (100, 100, 100), (76, 208, 56), (200, 0, 0), (255, 255, 255), (255, 232, 0), (0, 0, 0)

# Road settings
road_width, marker_width, marker_height = 300, 10, 50
left_lane, center_lane, right_lane = 150, 250, 350
lanes = [left_lane, center_lane, right_lane]

# Game settings
player_x, player_y = 250, 400
fps = 120
clock = pygame.time.Clock()
speed, score = 2, 0
gameover = False
difficulty = 'medium'  # Default difficulty
shield_active = False  # Shield state
shield_chances = 2  # Shield chances

# Fonts
menu_font = pygame.font.Font(pygame.font.get_default_font(), 32)
game_font = pygame.font.Font(pygame.font.get_default_font(), 16)
# Load wallpaper image
wallpaper = pygame.image.load('images/wallpaper.jpg')  # Replace with your wallpaper file path
wallpaper = pygame.transform.scale(wallpaper, (width, height))  # Scale to fit the screen


# Classes for vehicles
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 45 / image.get_rect().width
        new_width = int(image.get_rect().width * image_scale)
        new_height = int(image.get_rect().height * image_scale)
        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)


# Sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# Create player vehicle
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# Load vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = [pygame.image.load(f'images/{filename}') for filename in image_filenames]

# Load crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()


def display_text(text, font, color, center):
    """Utility function to display text on the screen."""
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=center)
    screen.blit(rendered_text, text_rect)


def main_menu():
    """Displays the main menu."""
    while True:
        screen.blit(wallpaper, (0, 0))

        display_text('Street Racer', menu_font, black, (width // 2, 100))
        display_text('1. Start Game', game_font, black, (width // 2, 200))
        display_text('2. Instructions', game_font, black, (width // 2, 250))
        display_text('3. Quit', game_font, black, (width // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_1:
                    difficulty_menu()  # Show difficulty options after clicking start
                elif event.key == K_2:
                    instructions()
                elif event.key == K_3:
                    pygame.quit()
                    exit()


def instructions():
    """Displays the instructions screen."""
    while True:
        screen.blit(wallpaper, (0, 0))

        display_text('Instructions', menu_font, black, (width // 2, 100))
        display_text('Use LEFT and RIGHT arrow keys to move.', game_font, black, (width // 2, 200))
        display_text('Avoid collisions with other vehicles.', game_font, black, (width // 2, 250))
        display_text('Press ESC to return to the menu.', game_font, black, (width // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return


def difficulty_menu():
    """Displays the difficulty level options."""
    global difficulty
    while True:
        screen.blit(wallpaper, (0, 0))

        display_text('Choose Difficulty', menu_font, black, (width // 2, 100))
        display_text('1. Easy', game_font, black, (width // 2, 200))
        display_text('2. Intermediate', game_font, black, (width // 2, 250))
        display_text('3. Hard', game_font, black, (width // 2, 300))
        display_text('Press ESC to go back', game_font, black, (width // 2, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_1:
                    difficulty = 'easy'
                    game_loop()
                    return
                elif event.key == K_2:
                    difficulty = 'medium'
                    game_loop()
                    return
                elif event.key == K_3:
                    difficulty = 'hard'
                    game_loop()
                    return
                elif event.key == K_ESCAPE:
                    return


def reset_game():
    """Resets the game to initial settings."""
    global gameover, score, speed, shield_active, shield_chances
    gameover = False
    score = 0
    vehicle_group.empty()
    player.rect.center = [player_x, player_y]
    shield_active = False
    shield_chances = 2

    # Adjust speed based on difficulty
    if difficulty == 'easy':
        speed = 2
    elif difficulty == 'medium':
        speed = 4
    elif difficulty == 'hard':
        speed = 6


def game_loop():
    """Main game loop."""
    global gameover, score, speed, shield_active, shield_chances

    lane_marker_move_y = 0
    running = True

    # Start the background music here
    pygame.mixer.music.play(-1)  # Play background music in a loop

    while running:
        clock.tick(fps)
        screen.fill(green)
        pygame.draw.rect(screen, gray, (100, 0, road_width, height))
        pygame.draw.rect(screen, yellow, (95, 0, marker_width, height))
        pygame.draw.rect(screen, yellow, (395, 0, marker_width, height))

        # Lane marker animation
        lane_marker_move_y += speed * 2
        if lane_marker_move_y >= marker_height * 2:
            lane_marker_move_y = 0
        
        # Draw lane markers on all lanes (left, center, right)
        for y in range(-marker_height * 2, height, marker_height * 2):
            # Left lane markers
            pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
            # Center lane markers
            pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
            # Right lane markers
            pygame.draw.rect(screen, white, (right_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

        # Draw vehicles
        vehicle_group.draw(screen)
        player_group.draw(screen)

        # Add new vehicles
        if len(vehicle_group) < 2:
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False
            if add_vehicle:
                lane = random.choice(lanes)
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, lane, height / -2)
                vehicle_group.add(vehicle)

        # Move vehicles
        for vehicle in vehicle_group:
            vehicle.rect.y += speed
            if vehicle.rect.top >= height:
                vehicle.kill()
                score += 1
                if score > 0 and score % 5 == 0:
                    speed += 1

        # Display score and shield chances
        display_text(f'Score: {score}', game_font, black, (50, 450))
        display_text(f'Shield Chances: {shield_chances}', game_font, black, (width - 150, 450))

        # Check for collisions
        collision = pygame.sprite.spritecollide(player, vehicle_group, True)
        if collision:
            if shield_chances > 0:
                shield_chances -= 1
                shield_active = True
            else:
                gameover = True
                pygame.mixer.music.stop()
                crash_sound.play()
                crash_rect.center = player.rect.center  # Align crash image with the player's car

        # Handle gameover
        if gameover:
            screen.blit(crash, crash_rect)  # Display crash effect at the collision location
            display_text('Game Over!', game_font, black, (width // 2, 200))
            display_text(f'Your Score: {score}', game_font, black, (width // 2, 250))
            display_text('Press Y to Retry or N to Quit.', game_font, black, (width // 2, 300))

            pygame.display.update()

            while gameover:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        exit()
                    if event.type == KEYDOWN:
                        if event.key == K_y:
                            reset_game()
                            pygame.mixer.music.play(-1)  # Restart background music after reset
                        elif event.key == K_n:
                            gameover = False
                            running = False

        pygame.display.update()

        # Handle user input for pausing the game
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT and player.rect.center[0] > left_lane:
                    player.rect.x -= 100
                elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                    player.rect.x += 100
                elif event.key == K_p:
                    pause_menu()  # Pause the game


def pause_menu():
    """Pause the game and provide options."""
    paused = True
    while paused:
        screen.blit(wallpaper, (0, 0))
        display_text('Game Paused', menu_font, black, (width // 2, 100))
        display_text('1. Resume', game_font, black, (width // 2, 200))
        display_text('2. Main Menu', game_font, black, (width // 2, 250))
        display_text('3. Difficulty Settings', game_font, black, (width // 2, 300))
        display_text('Press Q to Quit', game_font, black, (width // 2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_1:
                    paused = False  # Resume game
                elif event.key == K_2:
                    paused = False
                    return main_menu()  # Go to Main Menu
                elif event.key == K_3:
                    paused = False
                    return difficulty_menu()  # Go to Difficulty Settings
                elif event.key == K_q:
                    pygame.quit()
                    exit()


if __name__ == '__main__':
    main_menu()
