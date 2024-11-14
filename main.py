import pygame
import math
import random

pygame.init()

# Constants
WINDOW_WIDTH = 7000
WINDOW_HEIGHT = 3000
SCALE = 0.2
DISPLAY_WIDTH = int(WINDOW_WIDTH * SCALE)
DISPLAY_HEIGHT = int(WINDOW_HEIGHT * SCALE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

class Lander:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0  
        self.angle = 0  
        self.thrust = 3
        self.fuel = 1000
        self.width = 40
        self.height = 40
        self.gravity = 3.711  # Mars gravity

    def update(self):
        angle_rad = math.radians(self.angle)
        ax = -self.thrust * math.sin(angle_rad)
        ay = self.thrust * math.cos(angle_rad) - self.gravity
        self.vx += ax
        self.vy -= ay  # Changed from -= to +=
        self.x = max(0, min(self.x + self.vx, WINDOW_WIDTH))
        self.y = max(0, min(self.y + self.vy, WINDOW_HEIGHT))
        if self.thrust > 0 and self.fuel > 0:
            self.fuel -= self.thrust

    def draw(self, screen, scale):
        scaled_x, scaled_y = int(self.x * scale), int(self.y * scale)  # Removed * 2
        angle_rad = math.radians(self.angle)
        points = [
            (scaled_x + math.cos(angle_rad) * 20 * scale, scaled_y - math.sin(angle_rad) * 20 * scale),
            (scaled_x - math.cos(angle_rad + math.pi/6) * 20 * scale, scaled_y + math.sin(angle_rad + math.pi/6) * 20 * scale),
            (scaled_x - math.cos(angle_rad - math.pi/6) * 20 * scale, scaled_y + math.sin(angle_rad - math.pi/6) * 20 * scale)
        ]
        pygame.draw.polygon(screen, WHITE, points)
        if self.thrust > 0:
            thrust_point = (scaled_x - math.cos(angle_rad) * 30 * scale, scaled_y + math.sin(angle_rad) * 30 * scale)
            pygame.draw.line(screen, RED, (scaled_x, scaled_y), thrust_point, 3)

class Terrain:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.points = self.generate_terrain()
        self.landing_pad = self.generate_landing_pad()

    def generate_terrain(self):
        points = [(0, self.height - 200)]
        for i in range(1, 20):
            x = int((i * self.width) / 19)
            y = random.randint(int(self.height * 0.3), int(self.height * 0.8))
            points.append((x, y))
        points.append((self.width, self.height - 200))
        return points

    def generate_landing_pad(self):
        pad_start = random.randint(5, len(self.points) - 3)
        pad_width = 500
        x1, y = self.points[pad_start]
        x2 = x1 + pad_width
        new_points = self.points[:pad_start] + [(x1, y), (x2, y)] + self.points[pad_start + 2:]
        self.points = new_points
        return (x1, x2, y)

    def draw(self, screen, scale):
        scaled_points = [(int(x * scale), int(y * scale)) for x, y in self.points]
        pygame.draw.lines(screen, WHITE, False, scaled_points, 2)
        pad_x1, pad_x2, pad_y = [int(v * scale) for v in self.landing_pad]
        pygame.draw.line(screen, BLUE, (pad_x1, pad_y), (pad_x2, pad_y), 3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Mars Lander")
        self.clock = pygame.time.Clock()
        self.terrain = Terrain(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.lander = Lander(WINDOW_WIDTH/2, WINDOW_HEIGHT/4)
        self.font = pygame.font.Font(None, 36)
        self.game_over = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.lander.angle = min(90, self.lander.angle + 1)
        if keys[pygame.K_RIGHT]:
            self.lander.angle = max(-90, self.lander.angle - 1)
        if keys[pygame.K_UP] and self.lander.fuel > 0:
            self.lander.thrust = min(4, self.lander.thrust + 0.1)
        elif keys[pygame.K_DOWN]:
            self.lander.thrust = max(0, self.lander.thrust - 0.1)

    def check_collision(self):
        lander_points = [
            (self.lander.x, self.lander.y),
            (self.lander.x - self.lander.width/2, self.lander.y + self.lander.height/2),
            (self.lander.x + self.lander.width/2, self.lander.y + self.lander.height/2)
        ]
        pad_x1, pad_x2, pad_y = self.terrain.landing_pad
        if pad_x1 <= self.lander.x <= pad_x2 and abs(self.lander.y + self.lander.height/2 - pad_y) < 5:
            if abs(self.lander.vy) < 40 and abs(self.lander.vx) < 20 and abs(self.lander.angle) < 15:
                return "landed"
            return "crashed"
        for i in range(len(self.terrain.points) - 1):
            x1, y1 = self.terrain.points[i]
            x2, y2 = self.terrain.points[i + 1]
            if x1 <= self.lander.x <= x2:
                terrain_y = y1 + (y2 - y1) * (self.lander.x - x1) / (x2 - x1)
                if self.lander.y + self.lander.height/2 >= terrain_y:
                    return "crashed"
        return None

    def draw_hud(self):
        texts = [
            f"Fuel: {int(self.lander.fuel)}",
            f"Altitude: {int(WINDOW_HEIGHT - self.lander.y)}",
            f"Vertical Speed: {int(self.lander.vy)}",
            f"Horizontal Speed: {int(self.lander.vx)}",
            f"Angle: {int(self.lander.angle)}°"
        ]
        for i, text in enumerate(texts):
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (10, 10 + i * 30))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if not self.game_over:
                self.handle_input()
                self.lander.update()
                collision_result = self.check_collision()
                if collision_result:
                    self.game_over = True
                    print("Successful landing!" if collision_result == "landed" else "Crashed!")
            self.screen.fill(BLACK)
            self.terrain.draw(self.screen, SCALE)
            self.lander.draw(self.screen, SCALE)
            self.draw_hud()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()



















# import pygame
# import math
# import random

# # Initialize Pygame
# pygame.init()

# # Constants
# WINDOW_WIDTH = 7000
# WINDOW_HEIGHT = 3000
# # SCALE = 0.2  # Scale factor to fit on most screens
# SCALE = 0.2
# DISPLAY_WIDTH = int(WINDOW_WIDTH * SCALE)
# DISPLAY_HEIGHT = int(WINDOW_HEIGHT * SCALE)

# # Colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# RED = (255, 0, 0)
# BLUE = (0, 0, 255)
# GRAY = (128, 128, 128)

# class Lander:
#     def __init__(self, x, y):
#         self.x, self.y = x, y
#         self.vx, self.vy = 0, 0  
#         self.angle = 0  
#         self.thrust = 0
#         self.fuel = 1000
#         self.width = 40
#         self.height = 40
#         self.gravity = 3.711  # Mars gravity

#     def update(self):
#        angle_rad = math.radians(self.angle)
#        ax = -self.thrust * math.sin(angle_rad)
#        ay = self.thrust * math.cos(angle_rad) - self.gravity
#        self.vx += ax
#        self.vy -= ay
#     #    self.vy += ay
#        self.x = max(0, min(self.x + self.vx, WINDOW_WIDTH))
#        self.y = max(0, min(self.y + self.vy, WINDOW_HEIGHT))
#        if self.thrust > 0 and self.fuel > 0:
#            self.fuel -= self.thrust

#     def draw(self, screen, scale):
#        scaled_x, scaled_y = int(self.x * scale), int(self.y * scale)
#        angle_rad = math.radians(self.angle)
#        points = [
#            (scaled_x + math.cos(angle_rad) * 20 * scale, scaled_y + math.sin(angle_rad) * 20 * scale),
#            (scaled_x - math.cos(angle_rad + math.pi/6) * 20 * scale, scaled_y - math.sin(angle_rad + math.pi/6) * 20 * scale),
#            (scaled_x - math.cos(angle_rad - math.pi/6) * 20 * scale, scaled_y - math.sin(angle_rad - math.pi/6) * 20 * scale)
#        ]
#        pygame.draw.polygon(screen, WHITE, points)
#        if self.thrust > 0:
#            thrust_point = (scaled_x - math.cos(angle_rad) * 30 * scale, scaled_y - math.sin(angle_rad) * 30 * scale)
#            pygame.draw.line(screen, RED, (scaled_x, scaled_y), thrust_point, 3)

# class Terrain:
#    def __init__(self, width, height):
#        self.width, self.height = width, height
#        self.points = self.generate_terrain()
#        self.landing_pad = self.generate_landing_pad()

#    def generate_terrain(self):
#        points = [(0, self.height - 200)]
#        for i in range(1, 20):
#            x = int((i * self.width) / 19)
#            y = random.randint(int(self.height * 0.3), int(self.height * 0.8))
#            points.append((x, y))
#        points.append((self.width, self.height - 200))
#        return points

#    def generate_landing_pad(self):
#        pad_start = random.randint(5, len(self.points) - 3)
#        pad_width = 500
#        x1, y = self.points[pad_start]
#        x2 = x1 + pad_width
#        new_points = self.points[:pad_start] + [(x1, y), (x2, y)] + self.points[pad_start + 2:]
#        self.points = new_points
#        return (x1, x2, y)

#    def draw(self, screen, scale):
#        scaled_points = [(int(x * scale), int(y * scale)) for x, y in self.points]
#        pygame.draw.lines(screen, WHITE, False, scaled_points, 2)
#        pad_x1, pad_x2, pad_y = [int(v * scale) for v in self.landing_pad]
#        pygame.draw.line(screen, BLUE, (pad_x1, pad_y), (pad_x2, pad_y), 3)

# class Game:
#    def __init__(self):
#        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
#        pygame.display.set_caption("Mars Lander")
#        self.clock = pygame.time.Clock()
#        self.terrain = Terrain(WINDOW_WIDTH, WINDOW_HEIGHT)
#        self.lander = Lander(2000, 3000)
#             #    self.lander = Lander(WINDOW_WIDTH/2, WINDOW_HEIGHT/4)
#        self.font = pygame.font.Font(None, 36)
#        self.game_over = False

#    def handle_input(self):
#        keys = pygame.key.get_pressed()
#        if keys[pygame.K_LEFT]:
#            self.lander.angle = min(90, self.lander.angle + 1)
#        if keys[pygame.K_RIGHT]:
#            self.lander.angle = max(-90, self.lander.angle - 1)
#        if keys[pygame.K_UP] and self.lander.fuel > 0:
#            self.lander.thrust = min(4, self.lander.thrust + 1)
#        elif keys[pygame.K_DOWN]:
#            self.lander.thrust = max(0, self.lander.thrust - 1)

#    def check_collision(self):
#        lander_points = [
#            (self.lander.x, self.lander.y),
#            (self.lander.x - self.lander.width/2, self.lander.y + self.lander.height/2),
#            (self.lander.x + self.lander.width/2, self.lander.y + self.lander.height/2)
#        ]
#        pad_x1, pad_x2, pad_y = self.terrain.landing_pad
#        if pad_x1 <= self.lander.x <= pad_x2 and abs(self.lander.y + self.lander.height/2 - pad_y) < 5:
#            if abs(self.lander.vy) < 40 and abs(self.lander.vx) < 20:
#                return "landed"
#            return "crashed"
#        for i in range(len(self.terrain.points) - 1):
#            x1, y1 = self.terrain.points[i]
#            x2, y2 = self.terrain.points[i + 1]
#            if self.lander.x >= x1 and self.lander.x <= x2 and self.lander.y + self.lander.height/2 >= min(y1, y2):
#                return "crashed"
#        return None

#    def draw_hud(self):
#        texts = [
#            f"Fuel: {int(self.lander.fuel)}",
#            f"Altitude: {int(WINDOW_HEIGHT - self.lander.y)}",
#            f"Vertical Speed: {int(self.lander.vy)}",
#            f"Horizontal Speed: {int(self.lander.vx)}",
#            f"Angle: {int(self.lander.angle)}°"
#        ]
#        for i, text in enumerate(texts):
#            surface = self.font.render(text, True, WHITE)
#            self.screen.blit(surface, (10, 10 + i * 30))

#    def run(self):
#        running = True
#        while running:
#            for event in pygame.event.get():
#                if event.type == pygame.QUIT:
#                    running = False
#            if not self.game_over:
#                self.handle_input()
#                self.lander.update()
#                collision_result = self.check_collision()
#                if collision_result:
#                    self.game_over = True
#                    print("Successful landing!" if collision_result == "landed" else "Crashed!")
#            self.screen.fill(BLACK)
#            self.terrain.draw(self.screen, SCALE)
#            self.lander.draw(self.screen, SCALE)
#            self.draw_hud()
#            pygame.display.flip()
#            self.clock.tick(60)
#        pygame.quit()

# if __name__ == "__main__":
#    game = Game()
#    game.run()