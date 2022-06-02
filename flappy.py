import os
import random

import pygame

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "pipe.png"))
)
CHAO_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "base.png"))
)
IMAGE_BACKGROUND = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bg.png"))
)
IMAGES_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png"))),
]

pygame.font.init()
SOURCE = pygame.font.SysFont("arial", 50)


class Bird:

    IMGS = IMAGES_BIRD

    MAXIMUM_ROTATION = 25
    SPEED_ROTATION = 20
    TIME_ANIMATION = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.height = self.y
        self.time = 0
        self.count_image = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.velocity = -10.5
        self.time = 0
        self.height = self.y

    def move(self):

        self.time += 1
        displacement = 1.5 * (self.time**2) + self.velocity * self.time

        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAXIMUM_ROTATION:
                self.angle = self.MAXIMUM_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.SPEED_ROTATION

    def draw(self, screen):
        self.count_image += 1

        if self.count_image < self.TIME_ANIMATION:
            self.image = self.IMGS[0]
        elif self.count_image < self.TIME_ANIMATION * 2:
            self.image = self.IMGS[1]
        elif self.count_image < self.TIME_ANIMATION * 3:
            self.image = self.IMGS[2]
        elif self.count_image < self.TIME_ANIMATION * 4:
            self.image = self.IMGS[1]
        elif self.count_image >= self.TIME_ANIMATION * 4 + 1:
            self.image = self.IMGS[0]
            self.count_image = 0

        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.count_image = self.TIME_ANIMATION * 2

        rotated_image = pygame.transform.rotate(self.image, self.angle)
        pos_centro_image = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_image.get_rect(center=pos_centro_image)
        screen.blit(rotated_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.post_top = 0
        self.post_base = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BASE = PIPE_IMAGE
        self.passed = False
        self.define_height()

    def define_height(self):
        self.height = random.randrange(50, 450)
        self.post_top = self.height - self.PIPE_TOP.get_height()
        self.post_base = self.height + self.DISTANCE

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.post_top))
        screen.blit(self.PIPE_BASE, (self.x, self.post_base))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)

        DISTANCE_top = (self.x - bird.x, self.post_top - round(bird.y))
        DISTANCE_base = (self.x - bird.x, self.post_base - round(bird.y))

        top_point = bird_mask.overlap(top_mask, DISTANCE_top)
        base_point = bird_mask.overlap(base_mask, DISTANCE_base)

        if base_point or top_point:
            return True
        else:
            return False


class Chao:
    VELOCITY = 5
    WIDTH = CHAO_IMAGE.get_width()
    IMAGE = CHAO_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))


def draw_screen(screen, birds, pipes, chao, points):
    screen.blit(IMAGE_BACKGROUND, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = SOURCE.render(f"Pontuação: {points}", 1, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    chao.draw(screen)
    pygame.display.update()


def main():
    birds = [Bird(230, 350)]
    chao = Chao(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    points = 0
    watch = pygame.time.Clock()

    rodando = True
    while rodando:
        watch.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        for bird in birds:
            bird.move()
        chao.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            points += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > chao.y or bird.y < 0:
                birds.pop(i)

        draw_screen(screen, birds, pipes, chao, points)


if __name__ == "__main__":
    main()
