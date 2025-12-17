"""
Avatar Rendering System - Bluey Character Style
Renders Bluey, Bingo, Mum (Chilli), and Dad (Bandit) style dog avatars.
"""

import pygame
import math
from typing import Optional, Tuple, List, Dict
from player_detection import PlayerLandmarks


class BlueyColors:
    """Color palettes for each Bluey character."""

    # Bluey - Blue Heeler puppy
    BLUEY = {
        'fur_main': (108, 172, 228),      # Light blue
        'fur_dark': (70, 130, 180),       # Darker blue spots
        'fur_belly': (168, 210, 240),     # Light belly
        'nose': (45, 45, 55),             # Dark nose
        'eye_white': (255, 255, 255),
        'eye_pupil': (35, 35, 45),
        'eye_shine': (255, 255, 255),
        'tongue': (240, 150, 150),
        'inner_ear': (240, 180, 170),
        'outline': (50, 80, 120),
    }

    # Bingo - Red Heeler puppy (Bluey's sister)
    BINGO = {
        'fur_main': (235, 150, 90),       # Orange/tan
        'fur_dark': (190, 100, 60),       # Darker orange spots
        'fur_belly': (255, 220, 190),     # Light belly
        'nose': (45, 45, 55),
        'eye_white': (255, 255, 255),
        'eye_pupil': (35, 35, 45),
        'eye_shine': (255, 255, 255),
        'tongue': (240, 150, 150),
        'inner_ear': (240, 180, 170),
        'outline': (120, 70, 40),
    }

    # Chilli - Mum (Red Heeler)
    CHILLI = {
        'fur_main': (220, 120, 80),       # Reddish orange
        'fur_dark': (180, 90, 60),        # Darker spots
        'fur_belly': (250, 210, 180),     # Light belly
        'nose': (45, 45, 55),
        'eye_white': (255, 255, 255),
        'eye_pupil': (35, 35, 45),
        'eye_shine': (255, 255, 255),
        'tongue': (240, 150, 150),
        'inner_ear': (240, 180, 170),
        'outline': (100, 60, 40),
        'shirt': (120, 180, 140),         # Green top
    }

    # Bandit - Dad (Blue Heeler)
    BANDIT = {
        'fur_main': (90, 140, 190),       # Darker blue than Bluey
        'fur_dark': (60, 100, 150),       # Dark blue spots
        'fur_belly': (150, 190, 220),     # Light belly
        'nose': (45, 45, 55),
        'eye_white': (255, 255, 255),
        'eye_pupil': (35, 35, 45),
        'eye_shine': (255, 255, 255),
        'tongue': (240, 150, 150),
        'inner_ear': (240, 180, 170),
        'outline': (40, 70, 110),
        'shirt': (200, 140, 80),          # Orange/brown shirt
    }

    CHARACTERS = [BLUEY, BINGO, CHILLI, BANDIT]
    CHARACTER_NAMES = ['Bluey', 'Bingo', 'Mum', 'Dad']


class AvatarRenderer:
    """Renders Bluey-style dog avatars for detected players."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Smoothing for positions (reduces jitter)
        self.smooth_factor = 0.4
        self.previous_positions: Dict[str, Tuple[float, float]] = {}

        # Line thickness for outlines
        self.outline_width = 3

    def render_player(self, surface: pygame.Surface, player: PlayerLandmarks,
                     player_index: int = 0):
        """Render a Bluey-style dog avatar for a player."""
        if not player.is_visible:
            return

        # Get character colors
        colors = BlueyColors.CHARACTERS[player_index % len(BlueyColors.CHARACTERS)]
        char_name = BlueyColors.CHARACTER_NAMES[player_index % len(BlueyColors.CHARACTER_NAMES)]

        # Get smoothed key positions
        positions = self._get_smoothed_positions(player, player_index)

        if not positions:
            return

        # Calculate body scale based on shoulder width
        body_scale = self._calculate_body_scale(positions)

        # Draw character parts in order (back to front)
        self._draw_tail(surface, positions, colors, body_scale)
        self._draw_legs(surface, positions, colors, body_scale)
        self._draw_body(surface, positions, colors, body_scale, char_name)
        self._draw_arms(surface, positions, colors, body_scale)
        self._draw_head(surface, positions, colors, body_scale, char_name)

    def _get_smoothed_positions(self, player: PlayerLandmarks,
                                player_index: int) -> Optional[Dict]:
        """Get smoothed positions for all body parts."""
        prefix = f"p{player_index}_"

        def smooth(point: Optional[Tuple[float, float]], key: str) -> Optional[Tuple[float, float]]:
            if point is None:
                return self.previous_positions.get(prefix + key)

            full_key = prefix + key
            if full_key in self.previous_positions:
                prev = self.previous_positions[full_key]
                smoothed = (
                    prev[0] + (point[0] - prev[0]) * self.smooth_factor,
                    prev[1] + (point[1] - prev[1]) * self.smooth_factor
                )
                self.previous_positions[full_key] = smoothed
                return smoothed

            self.previous_positions[full_key] = point
            return point

        positions = {
            'nose': smooth(player.nose, 'nose'),
            'left_shoulder': smooth(player.left_shoulder, 'l_shoulder'),
            'right_shoulder': smooth(player.right_shoulder, 'r_shoulder'),
            'left_elbow': smooth(player.left_elbow, 'l_elbow'),
            'right_elbow': smooth(player.right_elbow, 'r_elbow'),
            'left_hand': smooth(player.left_hand, 'l_hand'),
            'right_hand': smooth(player.right_hand, 'r_hand'),
            'left_hip': smooth(player.left_hip, 'l_hip'),
            'right_hip': smooth(player.right_hip, 'r_hip'),
            'left_knee': smooth(player.left_knee, 'l_knee'),
            'right_knee': smooth(player.right_knee, 'r_knee'),
            'left_ankle': smooth(player.left_ankle, 'l_ankle'),
            'right_ankle': smooth(player.right_ankle, 'r_ankle'),
        }

        # Need at least shoulders and nose to render
        if not positions['nose'] or not positions['left_shoulder'] or not positions['right_shoulder']:
            return None

        # Calculate center points
        if positions['left_shoulder'] and positions['right_shoulder']:
            positions['neck'] = (
                (positions['left_shoulder'][0] + positions['right_shoulder'][0]) / 2,
                (positions['left_shoulder'][1] + positions['right_shoulder'][1]) / 2
            )

        if positions['left_hip'] and positions['right_hip']:
            positions['hip_center'] = (
                (positions['left_hip'][0] + positions['right_hip'][0]) / 2,
                (positions['left_hip'][1] + positions['right_hip'][1]) / 2
            )
        elif positions['neck']:
            # Estimate hip position if not detected
            positions['hip_center'] = (
                positions['neck'][0],
                positions['neck'][1] + 150
            )
            positions['left_hip'] = (positions['hip_center'][0] - 40, positions['hip_center'][1])
            positions['right_hip'] = (positions['hip_center'][0] + 40, positions['hip_center'][1])

        return positions

    def _calculate_body_scale(self, positions: Dict) -> float:
        """Calculate scale factor based on detected body size."""
        if positions['left_shoulder'] and positions['right_shoulder']:
            shoulder_width = abs(positions['right_shoulder'][0] - positions['left_shoulder'][0])
            # Base scale on shoulder width (typical ~150-200 pixels)
            return max(0.5, min(2.0, shoulder_width / 150))
        return 1.0

    def _draw_body(self, surface: pygame.Surface, positions: Dict,
                   colors: Dict, scale: float, char_name: str):
        """Draw the torso/body."""
        neck = positions.get('neck')
        hip_center = positions.get('hip_center')
        left_shoulder = positions.get('left_shoulder')
        right_shoulder = positions.get('right_shoulder')
        left_hip = positions.get('left_hip')
        right_hip = positions.get('right_hip')

        if not all([neck, left_shoulder, right_shoulder]):
            return

        # Create body polygon
        body_points = []

        # Shoulders (slightly inward from actual shoulder points for rounder look)
        shoulder_inset = 10 * scale
        if left_shoulder:
            body_points.append((left_shoulder[0] + shoulder_inset, left_shoulder[1]))
        if right_shoulder:
            body_points.append((right_shoulder[0] - shoulder_inset, right_shoulder[1]))

        # Hips
        if right_hip:
            body_points.append((right_hip[0] - shoulder_inset, right_hip[1]))
        if left_hip:
            body_points.append((left_hip[0] + shoulder_inset, left_hip[1]))

        if len(body_points) >= 3:
            # Draw body shadow
            shadow_points = [(p[0] + 4, p[1] + 4) for p in body_points]
            pygame.draw.polygon(surface, self._darken(colors['fur_main'], 0.5), shadow_points)

            # Draw main body
            pygame.draw.polygon(surface, colors['fur_main'], body_points)

            # Draw belly (lighter oval in center)
            if neck and hip_center:
                belly_center = (
                    int((neck[0] + hip_center[0]) / 2),
                    int((neck[1] + hip_center[1]) / 2 + 20 * scale)
                )
                belly_width = int(50 * scale)
                belly_height = int(80 * scale)
                belly_rect = pygame.Rect(
                    belly_center[0] - belly_width // 2,
                    belly_center[1] - belly_height // 2,
                    belly_width, belly_height
                )
                pygame.draw.ellipse(surface, colors['fur_belly'], belly_rect)

            # Draw shirt for adult characters
            if char_name in ['Mum', 'Dad'] and 'shirt' in colors:
                shirt_points = body_points[:2] + [
                    ((body_points[1][0] + body_points[2][0]) / 2,
                     (body_points[1][1] + body_points[2][1]) / 2),
                    ((body_points[0][0] + body_points[3][0]) / 2,
                     (body_points[0][1] + body_points[3][1]) / 2),
                ]
                pygame.draw.polygon(surface, colors['shirt'], shirt_points)

            # Draw outline
            pygame.draw.polygon(surface, colors['outline'], body_points, self.outline_width)

    def _draw_head(self, surface: pygame.Surface, positions: Dict,
                   colors: Dict, scale: float, char_name: str):
        """Draw the dog head with ears, snout, and eyes."""
        nose_pos = positions.get('nose')
        neck = positions.get('neck')

        if not nose_pos:
            return

        # Head position - between detected nose and neck
        if neck:
            head_x = int((nose_pos[0] * 0.7 + neck[0] * 0.3))
            head_y = int((nose_pos[1] * 0.7 + neck[1] * 0.3))
        else:
            head_x, head_y = int(nose_pos[0]), int(nose_pos[1])

        # Head size based on scale
        head_width = int(70 * scale)
        head_height = int(60 * scale)

        # Draw ears first (behind head)
        self._draw_ears(surface, head_x, head_y, head_width, head_height, colors, scale)

        # Draw head shadow
        pygame.draw.ellipse(surface, self._darken(colors['fur_main'], 0.5),
                           (head_x - head_width // 2 + 4, head_y - head_height // 2 + 4,
                            head_width, head_height))

        # Draw main head
        pygame.draw.ellipse(surface, colors['fur_main'],
                           (head_x - head_width // 2, head_y - head_height // 2,
                            head_width, head_height))

        # Draw face markings (darker patches)
        self._draw_face_markings(surface, head_x, head_y, head_width, colors, scale)

        # Draw snout
        self._draw_snout(surface, head_x, head_y, head_height, colors, scale)

        # Draw eyes
        self._draw_eyes(surface, head_x, head_y, head_width, colors, scale)

        # Draw head outline
        pygame.draw.ellipse(surface, colors['outline'],
                           (head_x - head_width // 2, head_y - head_height // 2,
                            head_width, head_height), self.outline_width)

    def _draw_ears(self, surface: pygame.Surface, head_x: int, head_y: int,
                   head_width: int, head_height: int, colors: Dict, scale: float):
        """Draw floppy dog ears."""
        ear_width = int(25 * scale)
        ear_height = int(40 * scale)

        for side in [-1, 1]:  # Left and right
            ear_x = head_x + side * (head_width // 2 - 5)
            ear_y = head_y - head_height // 3

            # Ear points (floppy triangular shape)
            ear_points = [
                (ear_x, ear_y),
                (ear_x + side * ear_width, ear_y + ear_height // 2),
                (ear_x + side * ear_width * 0.7, ear_y + ear_height),
                (ear_x, ear_y + ear_height * 0.6),
            ]

            # Draw ear shadow
            shadow_points = [(p[0] + 3, p[1] + 3) for p in ear_points]
            pygame.draw.polygon(surface, self._darken(colors['fur_main'], 0.5), shadow_points)

            # Draw outer ear
            pygame.draw.polygon(surface, colors['fur_dark'], ear_points)

            # Draw inner ear
            inner_points = [
                (ear_x + side * 5, ear_y + 8),
                (ear_x + side * (ear_width - 8), ear_y + ear_height // 2),
                (ear_x + side * (ear_width * 0.6), ear_y + ear_height - 10),
                (ear_x + side * 5, ear_y + ear_height * 0.5),
            ]
            pygame.draw.polygon(surface, colors['inner_ear'], inner_points)

            # Ear outline
            pygame.draw.polygon(surface, colors['outline'], ear_points, 2)

    def _draw_face_markings(self, surface: pygame.Surface, head_x: int, head_y: int,
                            head_width: int, colors: Dict, scale: float):
        """Draw darker fur patches on face."""
        # Eye patches (darker areas around eyes)
        patch_size = int(20 * scale)
        for side in [-1, 1]:
            patch_x = head_x + side * int(15 * scale)
            patch_y = head_y - int(5 * scale)
            pygame.draw.ellipse(surface, colors['fur_dark'],
                              (patch_x - patch_size // 2, patch_y - patch_size // 2,
                               patch_size, int(patch_size * 0.8)))

    def _draw_snout(self, surface: pygame.Surface, head_x: int, head_y: int,
                    head_height: int, colors: Dict, scale: float):
        """Draw the dog snout/muzzle."""
        snout_width = int(35 * scale)
        snout_height = int(25 * scale)
        snout_y = head_y + int(10 * scale)

        # Snout (lighter colored muzzle area)
        snout_rect = pygame.Rect(
            head_x - snout_width // 2, snout_y,
            snout_width, snout_height
        )
        pygame.draw.ellipse(surface, colors['fur_belly'], snout_rect)

        # Nose
        nose_width = int(15 * scale)
        nose_height = int(10 * scale)
        nose_rect = pygame.Rect(
            head_x - nose_width // 2, snout_y + 2,
            nose_width, nose_height
        )
        pygame.draw.ellipse(surface, colors['nose'], nose_rect)

        # Nose shine
        pygame.draw.ellipse(surface, (80, 80, 90),
                           (head_x - nose_width // 4, snout_y + 3,
                            nose_width // 3, nose_height // 3))

        # Mouth line
        mouth_y = snout_y + snout_height - 5
        pygame.draw.arc(surface, colors['outline'],
                       (head_x - 10, mouth_y - 5, 20, 15),
                       0.2, math.pi - 0.2, 2)

    def _draw_eyes(self, surface: pygame.Surface, head_x: int, head_y: int,
                   head_width: int, colors: Dict, scale: float):
        """Draw cartoon dog eyes."""
        eye_size = int(18 * scale)
        pupil_size = int(10 * scale)
        eye_y = head_y - int(8 * scale)
        eye_spacing = int(22 * scale)

        for side in [-1, 1]:
            eye_x = head_x + side * eye_spacing

            # Eye white
            pygame.draw.ellipse(surface, colors['eye_white'],
                              (eye_x - eye_size // 2, eye_y - eye_size // 2,
                               eye_size, eye_size))

            # Pupil (slightly offset for lively look)
            pupil_offset_x = side * 2
            pygame.draw.circle(surface, colors['eye_pupil'],
                             (eye_x + pupil_offset_x, eye_y), pupil_size // 2)

            # Eye shine
            shine_size = int(5 * scale)
            pygame.draw.circle(surface, colors['eye_shine'],
                             (eye_x + pupil_offset_x - 2, eye_y - 2), shine_size // 2)

            # Eye outline
            pygame.draw.ellipse(surface, colors['outline'],
                              (eye_x - eye_size // 2, eye_y - eye_size // 2,
                               eye_size, eye_size), 2)

    def _draw_arms(self, surface: pygame.Surface, positions: Dict,
                   colors: Dict, scale: float):
        """Draw arms with paws."""
        arm_width = int(22 * scale)
        paw_size = int(28 * scale)

        for side, (shoulder_key, elbow_key, hand_key) in [
            ('left', ('left_shoulder', 'left_elbow', 'left_hand')),
            ('right', ('right_shoulder', 'right_elbow', 'right_hand'))
        ]:
            shoulder = positions.get(shoulder_key)
            elbow = positions.get(elbow_key)
            hand = positions.get(hand_key)

            if not shoulder:
                continue

            # Draw upper arm
            if elbow:
                self._draw_limb_segment(surface, shoulder, elbow, arm_width, colors)

                # Draw lower arm
                if hand:
                    self._draw_limb_segment(surface, elbow, hand, arm_width - 4, colors)

                    # Draw paw
                    self._draw_paw(surface, hand, paw_size, colors)
            elif hand:
                # No elbow detected, draw straight to hand
                self._draw_limb_segment(surface, shoulder, hand, arm_width, colors)
                self._draw_paw(surface, hand, paw_size, colors)

    def _draw_legs(self, surface: pygame.Surface, positions: Dict,
                   colors: Dict, scale: float):
        """Draw legs with paws."""
        leg_width = int(26 * scale)
        paw_size = int(30 * scale)

        for side, (hip_key, knee_key, ankle_key) in [
            ('left', ('left_hip', 'left_knee', 'left_ankle')),
            ('right', ('right_hip', 'right_knee', 'right_ankle'))
        ]:
            hip = positions.get(hip_key)
            knee = positions.get(knee_key)
            ankle = positions.get(ankle_key)

            if not hip:
                continue

            # Draw upper leg
            if knee:
                self._draw_limb_segment(surface, hip, knee, leg_width, colors)

                # Draw lower leg
                if ankle:
                    self._draw_limb_segment(surface, knee, ankle, leg_width - 4, colors)
                    self._draw_paw(surface, ankle, paw_size, colors, is_foot=True)
            elif ankle:
                self._draw_limb_segment(surface, hip, ankle, leg_width, colors)
                self._draw_paw(surface, ankle, paw_size, colors, is_foot=True)

    def _draw_limb_segment(self, surface: pygame.Surface,
                           start: Tuple[float, float], end: Tuple[float, float],
                           width: int, colors: Dict):
        """Draw a single limb segment (arm or leg part)."""
        start_pos = (int(start[0]), int(start[1]))
        end_pos = (int(end[0]), int(end[1]))

        # Calculate perpendicular offset for limb width
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = max(1, math.sqrt(dx * dx + dy * dy))
        nx, ny = -dy / length, dx / length  # Normal vector

        half_width = width // 2

        # Create polygon for limb
        points = [
            (start_pos[0] + nx * half_width, start_pos[1] + ny * half_width),
            (start_pos[0] - nx * half_width, start_pos[1] - ny * half_width),
            (end_pos[0] - nx * half_width, end_pos[1] - ny * half_width),
            (end_pos[0] + nx * half_width, end_pos[1] + ny * half_width),
        ]

        # Draw shadow
        shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
        pygame.draw.polygon(surface, self._darken(colors['fur_main'], 0.5), shadow_points)

        # Draw limb
        pygame.draw.polygon(surface, colors['fur_main'], points)

        # Draw outline
        pygame.draw.polygon(surface, colors['outline'], points, 2)

        # Draw joint circles at connections
        pygame.draw.circle(surface, colors['fur_main'], start_pos, half_width)
        pygame.draw.circle(surface, colors['outline'], start_pos, half_width, 2)
        pygame.draw.circle(surface, colors['fur_main'], end_pos, half_width)
        pygame.draw.circle(surface, colors['outline'], end_pos, half_width, 2)

    def _draw_paw(self, surface: pygame.Surface, position: Tuple[float, float],
                  size: int, colors: Dict, is_foot: bool = False):
        """Draw a cartoon paw (hand or foot)."""
        x, y = int(position[0]), int(position[1])

        # Paw shadow
        pygame.draw.ellipse(surface, self._darken(colors['fur_main'], 0.5),
                           (x - size // 2 + 3, y - size // 2 + 3, size, size))

        # Main paw
        pygame.draw.ellipse(surface, colors['fur_belly'],
                           (x - size // 2, y - size // 2, size, size))

        # Paw pads
        pad_color = (60, 60, 70)
        if is_foot:
            # Foot has larger central pad
            pygame.draw.ellipse(surface, pad_color,
                              (x - size // 4, y - size // 6, size // 2, size // 3))
        else:
            # Hand paw pads (3 small circles)
            pad_size = size // 5
            for i, offset in enumerate([-1, 0, 1]):
                pad_x = x + offset * (size // 4)
                pad_y = y - size // 6
                pygame.draw.circle(surface, pad_color, (pad_x, pad_y), pad_size // 2)

        # Paw outline
        pygame.draw.ellipse(surface, colors['outline'],
                           (x - size // 2, y - size // 2, size, size), 2)

    def _draw_tail(self, surface: pygame.Surface, positions: Dict,
                   colors: Dict, scale: float):
        """Draw a wagging tail."""
        hip_center = positions.get('hip_center')
        if not hip_center:
            return

        tail_length = int(40 * scale)
        tail_width = int(15 * scale)

        # Tail wagging animation based on time
        wag = math.sin(pygame.time.get_ticks() / 150) * 0.4

        # Tail base position (behind the body)
        tail_start = (hip_center[0], hip_center[1] + 10)

        # Tail curves outward and up
        tail_mid = (
            tail_start[0] - tail_length * 0.5 + wag * 20,
            tail_start[1] - tail_length * 0.3
        )
        tail_end = (
            tail_start[0] - tail_length * 0.8 + wag * 30,
            tail_start[1] - tail_length * 0.7
        )

        # Draw tail segments
        points = [tail_start, tail_mid, tail_end]
        for i in range(len(points) - 1):
            width = tail_width - i * 4
            self._draw_curved_segment(surface, points[i], points[i + 1], width, colors)

    def _draw_curved_segment(self, surface: pygame.Surface,
                             start: Tuple[float, float], end: Tuple[float, float],
                             width: int, colors: Dict):
        """Draw a curved tail/limb segment."""
        pygame.draw.line(surface, colors['fur_main'],
                        (int(start[0]), int(start[1])),
                        (int(end[0]), int(end[1])), width)
        pygame.draw.line(surface, colors['outline'],
                        (int(start[0]), int(start[1])),
                        (int(end[0]), int(end[1])), width + 2)
        pygame.draw.line(surface, colors['fur_main'],
                        (int(start[0]), int(start[1])),
                        (int(end[0]), int(end[1])), width)

        # Round caps
        pygame.draw.circle(surface, colors['fur_main'],
                          (int(end[0]), int(end[1])), width // 2)

    def _darken(self, color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Darken a color by a factor."""
        return (
            int(color[0] * factor),
            int(color[1] * factor),
            int(color[2] * factor)
        )

    def get_hand_positions(self, player: PlayerLandmarks) -> List[Tuple[float, float]]:
        """Get hand positions for collision detection."""
        positions = []
        if player.left_hand:
            positions.append(player.left_hand)
        if player.right_hand:
            positions.append(player.right_hand)
        return positions

    def get_collision_radius(self) -> float:
        """Get the collision radius for hands/paws."""
        return 30
