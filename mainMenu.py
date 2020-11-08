import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
import os

BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GRAY = (105,105,105)
BLACK = (0, 0, 0)

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()

class GameState(Enum):
    QUIT = -1
    TITLE = 0
    STARTGAME = 1


class UIElement(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
        """
        self.mouse_over = False  # indicates if the mouse is over the element

        # create the default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        # calls the init method of the parent sprite class
        super().__init__()
        self.action = action

    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        """ Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked.
        """
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)

def title_screen(screen):
    boostButton = UIElement(
        center_position=(400, 200),
        font_size=50,
        bg_rgb=GRAY,
        text_rgb=WHITE,
        text="B O O S T !",
        action=GameState.QUIT,
    )

    quit_btn = UIElement(
        center_position=(400, 500),
        font_size=30,
        bg_rgb=GRAY,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    testDriveButton = UIElement(
        center_position=(400, 100),
        font_size=25,
        bg_rgb=GRAY,
        text_rgb=WHITE,
        text="Test Drive",
        action=GameState.QUIT,
    )

    mapButton = UIElement(
        center_position=(400, 300),
        font_size=25,
        bg_rgb=GRAY,
        text_rgb=WHITE,
        text="Map Editor",
        action=GameState.QUIT,
    )

    chadTitleScreen = UIElement(
        center_position=(400, 400),
        font_size=15,
        bg_rgb=GRAY,
        text_rgb=WHITE,
        text="Created by Jack Lowry, Michael Dasaro, and Cyrus Majd",
    )


    # main loop
    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
        screen.fill(GRAY)

        chadTitleScreen.update(pygame.mouse.get_pos(), mouse_up)
        chadTitleScreen.draw(screen)

        TST_DRIVE_MAN = testDriveButton.update(pygame.mouse.get_pos(), mouse_up)
        if TST_DRIVE_MAN is not None:
            print("Loading test drive...")
            os.system('python racertest.py 1')
            # pygame.quit()
            # return
        testDriveButton.draw(screen)

        MAP_MAN_POG = mapButton.update(pygame.mouse.get_pos(), mouse_up)
        if MAP_MAN_POG is not None:
            print("opening map editor")
            os.system('python racertest.py 2')
            # pygame.quit()
            # return
        mapButton.draw(screen)

        BOOST_MODE_KAPPA = boostButton.update(pygame.mouse.get_pos(), mouse_up)
        if BOOST_MODE_KAPPA is not None:
            print("LOL POG")
            os.system('python racertest.py')
            # pygame.quit()
            # return
        boostButton.draw(screen)

        LOSER_MODE_IDIOT = quit_btn.update(pygame.mouse.get_pos(), mouse_up)
        if LOSER_MODE_IDIOT is not None:
            print("aiight THOT")
            pygame.quit()
            # return
        quit_btn.draw(screen)
        pygame.display.flip()

def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    game_state = GameState.TITLE

    while True:
        if game_state == GameState.TITLE:
            game_state = title_screen(screen)

        if game_state == GameState.NEWGAME:
            game_state = play_level(screen)

        if game_state == GameState.QUIT:
            pygame.quit()
            return


# call main when the script is run
if __name__ == "__main__":
    main()