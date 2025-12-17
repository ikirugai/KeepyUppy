"""
Avatar Rendering System
Renders cartoon-style avatars for detected players in a Bluey-inspired style.
"""

import pygame
import math
from typing import Optional, Tuple, List
from player_detection import PlayerLandmarks


# Bluey-inspired color palette
class Colors:
    # Primary blues (Bluey family inspired)
    SKY_BLUE = (108, 172, 228)      # Light blue - main character color
    DEEP_BLUE = (59, 108, 180)      # Darker blue - shadows/outlines
    PALE_BLUE = (168, 216, 240)     # Very light blue - highlights

    # Warm colors (Bingo inspired)
    ORANGE = (245, 132, 38)         # Bingo's color
    CORAL = (255, 140, 148)         # Pink/coral accent
    WARM_YELLOW = (255, 218, 107)   # Sunny yellow

    # Environment
    GRASS_GREEN = (122, 182, 72)    # Grass
    LIGHT_GREEN = (166, 214, 126)   # Light grass
    SKY_GRADIENT_TOP = (135, 206, 250)  # Sky top
    SKY_GRADIENT_BOTTOM = (200, 230, 255)  # Sky bottom

    # UI
    WHITE = (255, 255, 255)
    BLACK = (40, 40, 50)
    SHADOW = (80, 100, 120, 100)    # Semi-transparent shadow

    # Avatar skin tones (cartoon style)
    SKIN_LIGHT = (255, 220, 185)
    SKIN_MEDIUM = (240, 195, 160)

    # Player colors (for multiple players)
    PLAYER_COLORS = [
        SKY_BLUE,      # Player 1 - Blue
        ORANGE,        # Player 2 - Orange
        CORAL,         # Player 3 - Pink
        WARM_YELLOW,   # Player 4 - Yellow
    ]


class AvatarRenderer:
    """Renders cartoon avatars for detected players."""

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize avatar renderer.

        Args:
            screen_width: Game screen width
            screen_height: Game screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Avatar style settings
        self.line_width = 4
        self.head_radius = 35
        self.hand_radius = 25
        self.body_width = 20

        # Smoothing for avatar positions (reduces jitter)
        self.smooth_factor = 0.3
        self.previous_positions = {}

    def render_player(self, surface: pygame.Surface, player: PlayerLandmarks,
                     player_index: int = 0):
        """
        Render a cartoon avatar for a player.

        Args:
            surface: Pygame surface to draw on
            player: Player landmark data
            player_index: Index for color selection
        """
        if not player.is_visible:
            return

        color = Colors.PLAYER_COLORS[player_index % len(Colors.PLAYER_COLORS)]
        outline_color = Colors.DEEP_BLUE

        # Draw body parts in order (back to front)
        self._draw_body(surface, player, color, outline_color)
        self._draw_limbs(surface, player, color, outline_color)
        self._draw_head(surface, player, color, outline_color, player_index)
        self._draw_hands(surface, player, color, outline_color)

    def _smooth_point(self, point: Optional[Tuple[float, float]],
                     key: str) -> Optional[Tuple[float, float]]:
        """Apply smoothing to reduce jitter in tracked positions."""
        if point is None:
            return self.previous_positions.get(key)

        if key in self.previous_positions and self.previous_positions[key]:
            prev = self.previous_positions[key]
            smoothed = (
                prev[0] + (point[0] - prev[0]) * self.smooth_factor,
                prev[1] + (point[1] - prev[1]) * self.smooth_factor
            )
            self.previous_positions[key] = smoothed
            return smoothed

        self.previous_positions[key] = point
        return point

    def _draw_head(self, surface: pygame.Surface, player: PlayerLandmarks,
                  color: Tuple[int, int, int], outline_color: Tuple[int, int, int],
                  player_index: int):
        """Draw the cartoon head with face."""
        nose = self._smooth_point(player.nose, 'nose')
        if not nose:
            return

        x, y = int(nose[0]), int(nose[1])
        radius = self.head_radius

        # Draw head shadow
        shadow_offset = 4
        pygame.draw.circle(surface, Colors.DEEP_BLUE,
                          (x + shadow_offset, y + shadow_offset), radius)

        # Draw head fill
        pygame.draw.circle(surface, color, (x, y), radius)

        # Draw head outline
        pygame.draw.circle(surface, outline_color, (x, y), radius, self.line_width)

        # Draw face features
        self._draw_face(surface, x, y, radius, player_index)

    def _draw_face(self, surface: pygame.Surface, x: int, y: int,
                  radius: int, player_index: int):
        """Draw cartoon face features."""
        # Eye settings
        eye_offset_x = radius // 3
        eye_offset_y = -radius // 6
        eye_radius = radius // 4
        pupil_radius = eye_radius // 2

        # Left eye
        left_eye_x = x - eye_offset_x
        eye_y = y + eye_offset_y

        # Eye whites
        pygame.draw.circle(surface, Colors.WHITE,
                          (left_eye_x, eye_y), eye_radius)
        pygame.draw.circle(surface, Colors.WHITE,
                          (x + eye_offset_x, eye_y), eye_radius)

        # Pupils
        pygame.draw.circle(surface, Colors.BLACK,
                          (left_eye_x, eye_y), pupil_radius)
        pygame.draw.circle(surface, Colors.BLACK,
                          (x + eye_offset_x, eye_y), pupil_radius)

        # Eye shine
        shine_offset = pupil_radius // 2
        shine_radius = pupil_radius // 2
        pygame.draw.circle(surface, Colors.WHITE,
                          (left_eye_x - shine_offset, eye_y - shine_offset),
                          shine_radius)
        pygame.draw.circle(surface, Colors.WHITE,
                          (x + eye_offset_x - shine_offset, eye_y - shine_offset),
                          shine_radius)

        # Nose (small dot)
        nose_y = y + radius // 6
        pygame.draw.circle(surface, Colors.DEEP_BLUE, (x, nose_y), 4)

        # Smile
        smile_y = y + radius // 3
        smile_rect = pygame.Rect(x - radius // 2, smile_y - radius // 4,
                                radius, radius // 2)
        pygame.draw.arc(surface, Colors.DEEP_BLUE, smile_rect,
                       math.pi + 0.3, 2 * math.pi - 0.3, 3)

        # Blush circles (cute cartoon style)
        blush_y = y + radius // 6
        blush_radius = radius // 5
        blush_color = (255, 180, 180, 128)  # Light pink

        # Create a temporary surface for blush with alpha
        blush_surf = pygame.Surface((blush_radius * 2, blush_radius * 2),
                                   pygame.SRCALPHA)
        pygame.draw.circle(blush_surf, blush_color,
                          (blush_radius, blush_radius), blush_radius)
        surface.blit(blush_surf, (x - eye_offset_x - radius // 3 - blush_radius,
                                  blush_y - blush_radius))
        surface.blit(blush_surf, (x + eye_offset_x + radius // 4 - blush_radius,
                                  blush_y - blush_radius))

    def _draw_body(self, surface: pygame.Surface, player: PlayerLandmarks,
                  color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """Draw the cartoon body/torso."""
        left_shoulder = self._smooth_point(player.left_shoulder, 'l_shoulder')
        right_shoulder = self._smooth_point(player.right_shoulder, 'r_shoulder')
        left_hip = self._smooth_point(player.left_hip, 'l_hip')
        right_hip = self._smooth_point(player.right_hip, 'r_hip')

        if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
            return

        # Create body polygon
        body_points = [
            (int(left_shoulder[0]), int(left_shoulder[1])),
            (int(right_shoulder[0]), int(right_shoulder[1])),
            (int(right_hip[0]), int(right_hip[1])),
            (int(left_hip[0]), int(left_hip[1])),
        ]

        # Draw shadow
        shadow_points = [(p[0] + 4, p[1] + 4) for p in body_points]
        pygame.draw.polygon(surface, Colors.DEEP_BLUE, shadow_points)

        # Draw body fill
        pygame.draw.polygon(surface, color, body_points)

        # Draw outline
        pygame.draw.polygon(surface, outline_color, body_points, self.line_width)

    def _draw_limbs(self, surface: pygame.Surface, player: PlayerLandmarks,
                   color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """Draw arms and legs."""
        # Arms
        self._draw_limb(surface, player.left_shoulder, player.left_elbow,
                       color, outline_color, 'l_shoulder', 'l_elbow')
        self._draw_limb(surface, player.left_elbow, player.left_hand,
                       color, outline_color, 'l_elbow', 'l_hand')
        self._draw_limb(surface, player.right_shoulder, player.right_elbow,
                       color, outline_color, 'r_shoulder', 'r_elbow')
        self._draw_limb(surface, player.right_elbow, player.right_hand,
                       color, outline_color, 'r_elbow', 'r_hand')

        # Legs
        self._draw_limb(surface, player.left_hip, player.left_knee,
                       color, outline_color, 'l_hip', 'l_knee')
        self._draw_limb(surface, player.left_knee, player.left_ankle,
                       color, outline_color, 'l_knee', 'l_ankle')
        self._draw_limb(surface, player.right_hip, player.right_knee,
                       color, outline_color, 'r_hip', 'r_knee')
        self._draw_limb(surface, player.right_knee, player.right_ankle,
                       color, outline_color, 'r_knee', 'r_ankle')

    def _draw_limb(self, surface: pygame.Surface,
                  start: Optional[Tuple[float, float]],
                  end: Optional[Tuple[float, float]],
                  color: Tuple[int, int, int],
                  outline_color: Tuple[int, int, int],
                  start_key: str, end_key: str):
        """Draw a single limb segment."""
        start = self._smooth_point(start, start_key)
        end = self._smooth_point(end, end_key)

        if not start or not end:
            return

        start_pos = (int(start[0]), int(start[1]))
        end_pos = (int(end[0]), int(end[1]))

        # Draw shadow
        shadow_start = (start_pos[0] + 3, start_pos[1] + 3)
        shadow_end = (end_pos[0] + 3, end_pos[1] + 3)
        pygame.draw.line(surface, Colors.DEEP_BLUE,
                        shadow_start, shadow_end, self.body_width)

        # Draw limb
        pygame.draw.line(surface, color, start_pos, end_pos, self.body_width)

        # Draw outline
        pygame.draw.line(surface, outline_color, start_pos, end_pos,
                        self.body_width + 4)
        pygame.draw.line(surface, color, start_pos, end_pos, self.body_width)

    def _draw_hands(self, surface: pygame.Surface, player: PlayerLandmarks,
                   color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """Draw cartoon hands (important for game interaction!)."""
        for hand, key in [(player.left_hand, 'l_hand'),
                         (player.right_hand, 'r_hand')]:
            hand = self._smooth_point(hand, key)
            if not hand:
                continue

            x, y = int(hand[0]), int(hand[1])
            radius = self.hand_radius

            # Draw hand shadow
            pygame.draw.circle(surface, Colors.DEEP_BLUE,
                              (x + 3, y + 3), radius)

            # Draw hand (skin colored for visibility)
            pygame.draw.circle(surface, Colors.SKIN_LIGHT, (x, y), radius)

            # Draw outline
            pygame.draw.circle(surface, outline_color, (x, y), radius, 3)

            # Draw finger lines (simple cartoon style)
            for angle in [-0.4, 0, 0.4]:
                end_x = x + int(math.cos(angle - math.pi/2) * radius * 0.8)
                end_y = y + int(math.sin(angle - math.pi/2) * radius * 0.8)
                pygame.draw.line(surface, outline_color, (x, y - radius//2),
                               (end_x, end_y - radius//2), 2)

    def get_hand_positions(self, player: PlayerLandmarks) -> List[Tuple[float, float]]:
        """Get smoothed hand positions for collision detection."""
        positions = []

        left = self._smooth_point(player.left_hand, 'l_hand')
        if left:
            positions.append(left)

        right = self._smooth_point(player.right_hand, 'r_hand')
        if right:
            positions.append(right)

        return positions

    def get_collision_radius(self) -> float:
        """Get the collision radius for hands."""
        return self.hand_radius
