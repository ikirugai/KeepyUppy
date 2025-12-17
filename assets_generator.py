"""
Asset Generator
Generates Bluey-inspired cartoon graphics programmatically.
"""

import pygame
import math
from typing import Tuple


# Bluey-inspired color palette
class Palette:
    # Blues
    SKY_BLUE = (108, 172, 228)
    DEEP_BLUE = (59, 108, 180)
    PALE_BLUE = (168, 216, 240)
    NAVY = (45, 80, 140)

    # Warm colors
    ORANGE = (245, 132, 38)
    CORAL = (255, 140, 148)
    WARM_YELLOW = (255, 218, 107)
    SUNSET_ORANGE = (255, 180, 100)

    # Environment
    GRASS_GREEN = (122, 182, 72)
    LIGHT_GREEN = (166, 214, 126)
    DARK_GREEN = (80, 140, 50)
    SKY_TOP = (135, 206, 250)
    SKY_BOTTOM = (200, 235, 255)

    # Balloon colors
    BALLOON_RED = (255, 100, 100)
    BALLOON_PINK = (255, 180, 200)
    BALLOON_HIGHLIGHT = (255, 255, 255)

    # UI
    WHITE = (255, 255, 255)
    BLACK = (40, 40, 50)
    CREAM = (255, 250, 240)


class AssetGenerator:
    """Generates game assets with a Bluey-inspired cartoon style."""

    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the asset generator."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.assets = {}

    def generate_all(self):
        """Generate all game assets."""
        self.assets['background'] = self._create_background()
        self.assets['balloon'] = self._create_balloon(100)
        self.assets['balloon_popped'] = self._create_popped_balloon(100)
        self.assets['cloud1'] = self._create_cloud(120, 60)
        self.assets['cloud2'] = self._create_cloud(100, 50)
        self.assets['sun'] = self._create_sun(80)
        self.assets['wind_arrow'] = self._create_wind_arrow(60)
        self.assets['grass_tuft'] = self._create_grass_tuft(40, 30)

        return self.assets

    def _create_background(self) -> pygame.Surface:
        """Create the game background with sky and ground."""
        surface = pygame.Surface((self.screen_width, self.screen_height))

        # Draw gradient sky
        for y in range(self.screen_height - 100):
            ratio = y / (self.screen_height - 100)
            r = int(Palette.SKY_TOP[0] + (Palette.SKY_BOTTOM[0] - Palette.SKY_TOP[0]) * ratio)
            g = int(Palette.SKY_TOP[1] + (Palette.SKY_BOTTOM[1] - Palette.SKY_TOP[1]) * ratio)
            b = int(Palette.SKY_TOP[2] + (Palette.SKY_BOTTOM[2] - Palette.SKY_TOP[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))

        # Draw ground
        ground_y = self.screen_height - 100
        pygame.draw.rect(surface, Palette.GRASS_GREEN,
                        (0, ground_y, self.screen_width, 100))

        # Draw grass details (lighter patches)
        for x in range(0, self.screen_width, 40):
            # Random-ish grass bumps
            offset = (x * 7) % 20 - 10
            self._draw_grass_bump(surface, x + offset, ground_y,
                                 Palette.LIGHT_GREEN)

        # Draw some decorative flowers/dots
        for x in range(30, self.screen_width - 30, 80):
            y_offset = ((x * 13) % 40) - 20
            color = Palette.WARM_YELLOW if (x // 80) % 2 == 0 else Palette.CORAL
            pygame.draw.circle(surface, color,
                              (x, ground_y + 30 + y_offset), 8)
            pygame.draw.circle(surface, Palette.WHITE,
                              (x - 2, ground_y + 28 + y_offset), 3)

        return surface

    def _draw_grass_bump(self, surface: pygame.Surface, x: int, y: int,
                        color: Tuple[int, int, int]):
        """Draw a small grass bump."""
        points = [
            (x - 15, y + 5),
            (x - 5, y - 10),
            (x, y - 15),
            (x + 5, y - 10),
            (x + 15, y + 5),
        ]
        pygame.draw.polygon(surface, color, points)

    def _create_balloon(self, size: int) -> pygame.Surface:
        """Create a cartoon balloon surface."""
        # Make surface larger to fit string
        surface = pygame.Surface((size, size + 60), pygame.SRCALPHA)

        center_x = size // 2
        center_y = size // 2
        radius = size // 2 - 4

        # Balloon shadow
        pygame.draw.ellipse(surface, (*Palette.BALLOON_RED[:3], 100),
                           (center_x - radius + 6, center_y - radius + 6,
                            radius * 2, radius * 2 + 10))

        # Main balloon body (slightly oval)
        pygame.draw.ellipse(surface, Palette.BALLOON_RED,
                           (center_x - radius, center_y - radius,
                            radius * 2, radius * 2 + 10))

        # Balloon outline
        pygame.draw.ellipse(surface, Palette.NAVY,
                           (center_x - radius, center_y - radius,
                            radius * 2, radius * 2 + 10), 4)

        # Highlight (shine effect)
        highlight_radius = radius // 3
        pygame.draw.ellipse(surface, Palette.BALLOON_PINK,
                           (center_x - radius // 2, center_y - radius // 2,
                            highlight_radius, highlight_radius * 2))

        # Small white shine
        pygame.draw.circle(surface, Palette.BALLOON_HIGHLIGHT,
                          (center_x - radius // 3, center_y - radius // 3),
                          radius // 6)

        # Balloon knot
        knot_y = center_y + radius + 5
        pygame.draw.polygon(surface, Palette.BALLOON_RED, [
            (center_x - 8, knot_y),
            (center_x + 8, knot_y),
            (center_x, knot_y + 12),
        ])
        pygame.draw.polygon(surface, Palette.NAVY, [
            (center_x - 8, knot_y),
            (center_x + 8, knot_y),
            (center_x, knot_y + 12),
        ], 2)

        # String (curvy)
        string_start = (center_x, knot_y + 12)
        for i in range(30):
            y = knot_y + 12 + i * 1.5
            x = center_x + math.sin(i * 0.3) * 5
            if i > 0:
                pygame.draw.line(surface, Palette.NAVY,
                               (prev_x, prev_y), (x, y), 2)
            prev_x, prev_y = x, y

        return surface

    def _create_popped_balloon(self, size: int) -> pygame.Surface:
        """Create a popped balloon effect."""
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        center = size

        # Draw scattered pieces
        pieces = [
            (center - 30, center - 20, 15),
            (center + 25, center - 15, 12),
            (center - 10, center + 20, 18),
            (center + 35, center + 10, 10),
            (center - 35, center + 5, 14),
            (center + 5, center - 35, 11),
        ]

        for px, py, ps in pieces:
            # Draw irregular balloon piece
            points = []
            for i in range(6):
                angle = i * math.pi / 3 + (px % 10) * 0.1
                r = ps * (0.7 + (py % 5) * 0.1)
                points.append((px + math.cos(angle) * r,
                              py + math.sin(angle) * r))
            pygame.draw.polygon(surface, Palette.BALLOON_RED, points)
            pygame.draw.polygon(surface, Palette.NAVY, points, 2)

        # "POP!" text effect
        font = pygame.font.Font(None, 48)
        text = font.render("POP!", True, Palette.ORANGE)
        text_rect = text.get_rect(center=(center, center))

        # Text outline
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            outline = font.render("POP!", True, Palette.NAVY)
            surface.blit(outline, (text_rect.x + dx, text_rect.y + dy))

        surface.blit(text, text_rect)

        return surface

    def _create_cloud(self, width: int, height: int) -> pygame.Surface:
        """Create a cartoon cloud."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw overlapping circles for fluffy cloud effect
        circles = [
            (width // 4, height // 2, height // 3),
            (width // 2, height // 3, height // 2.5),
            (width * 3 // 4, height // 2, height // 3),
            (width // 3, height // 2, height // 4),
            (width * 2 // 3, height // 2, height // 4),
        ]

        # Shadow
        for cx, cy, r in circles:
            pygame.draw.circle(surface, (200, 220, 240),
                              (int(cx) + 3, int(cy) + 3), int(r))

        # White cloud
        for cx, cy, r in circles:
            pygame.draw.circle(surface, Palette.WHITE,
                              (int(cx), int(cy)), int(r))

        return surface

    def _create_sun(self, size: int) -> pygame.Surface:
        """Create a cartoon sun."""
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        center = size

        # Sun rays
        ray_color = (255, 230, 150)
        for i in range(12):
            angle = i * math.pi / 6
            inner_r = size // 2 + 5
            outer_r = size - 5
            x1 = center + math.cos(angle) * inner_r
            y1 = center + math.sin(angle) * inner_r
            x2 = center + math.cos(angle) * outer_r
            y2 = center + math.sin(angle) * outer_r
            pygame.draw.line(surface, ray_color, (x1, y1), (x2, y2), 6)

        # Main sun circle
        pygame.draw.circle(surface, Palette.WARM_YELLOW, (center, center), size // 2)
        pygame.draw.circle(surface, Palette.ORANGE, (center, center), size // 2, 3)

        # Happy face
        eye_y = center - 5
        pygame.draw.circle(surface, Palette.BLACK, (center - 10, eye_y), 4)
        pygame.draw.circle(surface, Palette.BLACK, (center + 10, eye_y), 4)

        # Smile
        smile_rect = pygame.Rect(center - 12, center - 5, 24, 20)
        pygame.draw.arc(surface, Palette.BLACK, smile_rect,
                       math.pi + 0.3, 2 * math.pi - 0.3, 3)

        return surface

    def _create_wind_arrow(self, size: int) -> pygame.Surface:
        """Create a wind indicator arrow."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Arrow body
        arrow_points = [
            (5, size // 2 - 8),
            (size - 15, size // 2 - 8),
            (size - 15, size // 2 - 15),
            (size - 5, size // 2),
            (size - 15, size // 2 + 15),
            (size - 15, size // 2 + 8),
            (5, size // 2 + 8),
        ]

        pygame.draw.polygon(surface, Palette.PALE_BLUE, arrow_points)
        pygame.draw.polygon(surface, Palette.DEEP_BLUE, arrow_points, 3)

        # Wind swoosh lines
        for i, offset in enumerate([10, 0, -10]):
            start_x = 15 + i * 8
            pygame.draw.arc(surface, Palette.DEEP_BLUE,
                           (start_x, size // 2 + offset - 5, 12, 10),
                           0, math.pi, 2)

        return surface

    def _create_grass_tuft(self, width: int, height: int) -> pygame.Surface:
        """Create a grass tuft decoration."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw grass blades
        blades = [
            (width // 4, 0.8),
            (width // 2, 1.0),
            (width * 3 // 4, 0.85),
            (width // 3, 0.7),
            (width * 2 // 3, 0.75),
        ]

        for bx, height_factor in blades:
            blade_height = int(height * height_factor)
            points = [
                (bx - 3, height),
                (bx, height - blade_height),
                (bx + 3, height),
            ]
            pygame.draw.polygon(surface, Palette.GRASS_GREEN, points)

        return surface


def create_game_font(size: int) -> pygame.font.Font:
    """Create a font for game text (uses system font for compatibility)."""
    # Try to use a fun, rounded font if available
    try:
        return pygame.font.SysFont('Comic Sans MS', size)
    except:
        try:
            return pygame.font.SysFont('Arial Rounded MT Bold', size)
        except:
            return pygame.font.Font(None, size)
