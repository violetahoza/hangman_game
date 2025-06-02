import pygame
import math
from settings import COLORS, GAME, POSITIONS

class HangmanDrawer:
    
    def __init__(self):
        self.line_width = GAME['hangman_line_width']
        self.gallows_color = COLORS['text_primary']
        self.person_color = COLORS['danger']
        self.rope_color = COLORS['text_secondary']
        
        self.shake_offset = 0
        self.fade_alpha = 255
    
    def draw(self, screen, wrong_guesses, x, y):
        width = POSITIONS['hangman_width']
        height = POSITIONS['hangman_height']
        
        shake_intensity = max(0, wrong_guesses - 4) * 2
        if shake_intensity > 0:
            self.shake_offset = math.sin(pygame.time.get_ticks() * 0.02) * shake_intensity
        else:
            self.shake_offset = 0
        
        base_x = x + self.shake_offset
        base_y = y + height
        post_x = x + 25 + self.shake_offset
        post_top_y = y + 25
        beam_end_x = x + width - 60
        noose_y = y + 70
        
        self.draw_gallows(screen, base_x, base_y, post_x, post_top_y, beam_end_x, noose_y)
        
        if wrong_guesses >= 1:
            self.draw_head(screen, beam_end_x, noose_y + 35)
        
        if wrong_guesses >= 2:
            self.draw_body(screen, beam_end_x, noose_y + 65, noose_y + 155)
        
        if wrong_guesses >= 3:
            self.draw_left_arm(screen, beam_end_x, noose_y + 90)
        
        if wrong_guesses >= 4:
            self.draw_right_arm(screen, beam_end_x, noose_y + 90)
        
        if wrong_guesses >= 5:
            self.draw_left_leg(screen, beam_end_x, noose_y + 155)
        
        if wrong_guesses >= 6:
            self.draw_right_leg(screen, beam_end_x, noose_y + 155)
    
    def draw_gallows(self, screen, base_x, base_y, post_x, post_top_y, beam_end_x, noose_y):
        shadow_offset = 3
        shadow_color = COLORS['shadow_light']
        
        pygame.draw.line(screen, shadow_color, 
                        (base_x + shadow_offset, base_y + shadow_offset), 
                        (base_x + 120 + shadow_offset, base_y + shadow_offset), 
                        self.line_width)
        
        pygame.draw.line(screen, shadow_color, 
                        (post_x + shadow_offset, base_y + shadow_offset), 
                        (post_x + shadow_offset, post_top_y + shadow_offset), 
                        self.line_width)
        
        pygame.draw.line(screen, shadow_color, 
                        (post_x + shadow_offset, post_top_y + shadow_offset), 
                        (beam_end_x + shadow_offset, post_top_y + shadow_offset), 
                        self.line_width)
        
        pygame.draw.line(screen, shadow_color, 
                        (beam_end_x + shadow_offset, post_top_y + shadow_offset), 
                        (beam_end_x + shadow_offset, noose_y + shadow_offset), 
                        self.line_width)
        
        start_pos = (base_x, base_y)
        end_pos = (base_x + 120, base_y)
        pygame.draw.line(screen, self.gallows_color, start_pos, end_pos, self.line_width)
        pygame.draw.circle(screen, self.gallows_color, start_pos, self.line_width // 2)
        pygame.draw.circle(screen, self.gallows_color, end_pos, self.line_width // 2)
        
        start_pos = (post_x, base_y)
        end_pos = (post_x, post_top_y)
        pygame.draw.line(screen, self.gallows_color, start_pos, end_pos, self.line_width)
        pygame.draw.circle(screen, self.gallows_color, start_pos, self.line_width // 2)
        pygame.draw.circle(screen, self.gallows_color, end_pos, self.line_width // 2)
        
        start_pos = (post_x, post_top_y)
        end_pos = (beam_end_x, post_top_y)
        pygame.draw.line(screen, self.gallows_color, start_pos, end_pos, self.line_width)
        pygame.draw.circle(screen, self.gallows_color, end_pos, self.line_width // 2)
        
        start_pos = (beam_end_x, post_top_y)
        end_pos = (beam_end_x, noose_y)
        pygame.draw.line(screen, self.rope_color, start_pos, end_pos, self.line_width - 1)
        
        rope_segments = 8
        segment_height = (noose_y - post_top_y) // rope_segments
        for i in range(rope_segments):
            segment_y = post_top_y + i * segment_height
            if i % 2 == 0:
                pygame.draw.circle(screen, self.gallows_color, (beam_end_x, segment_y), 2)
        
        noose_radius = 12
        pygame.draw.circle(screen, self.rope_color, (beam_end_x, noose_y), noose_radius, 2)
    
    def draw_head(self, screen, center_x, center_y):
        radius = 22
        
        shadow_offset = 2
        pygame.draw.circle(screen, COLORS['shadow_light'], 
                          (int(center_x + shadow_offset), int(center_y + shadow_offset)), 
                          radius, self.line_width)
        
        pygame.draw.circle(screen, self.person_color, (int(center_x), int(center_y)), 
                          radius, self.line_width)
        
        pygame.draw.circle(screen, self.person_color, (int(center_x), int(center_y)), 
                          radius - 3, 1)
        
        self.draw_face(screen, center_x, center_y)
    
    def draw_face(self, screen, center_x, center_y):
        eye_size = 3
        left_eye_x = center_x - 8
        right_eye_x = center_x + 8
        eye_y = center_y - 5
        
        pygame.draw.circle(screen, self.person_color, (int(left_eye_x), int(eye_y)), eye_size)
        pygame.draw.circle(screen, self.person_color, (int(right_eye_x), int(eye_y)), eye_size)
        
        mouth_y = center_y + 8
        pygame.draw.line(screen, self.person_color, 
                        (center_x - 6, mouth_y), (center_x + 6, mouth_y), 2)
    
    def draw_body(self, screen, center_x, start_y, end_y):
        pygame.draw.line(screen, COLORS['shadow_light'], 
                        (center_x + 2, start_y + 2), (center_x + 2, end_y + 2), 
                        self.line_width)
        
        pygame.draw.line(screen, self.person_color, 
                        (center_x, start_y), (center_x, end_y), self.line_width)
        
        segment_count = 4
        segment_height = (end_y - start_y) // segment_count
        for i in range(1, segment_count):
            segment_y = start_y + i * segment_height
            pygame.draw.line(screen, self.person_color,
                           (center_x - 3, segment_y), (center_x + 3, segment_y), 1)
    
    def draw_left_arm(self, screen, center_x, body_y):
        arm_length = 45
        arm_end_x = center_x - arm_length
        arm_end_y = body_y + 25
        
        pygame.draw.line(screen, COLORS['shadow_light'], 
                        (center_x + 1, body_y + 1), (arm_end_x + 1, arm_end_y + 1), 
                        self.line_width)
        
        pygame.draw.line(screen, self.person_color, 
                        (center_x, body_y), (arm_end_x, arm_end_y), self.line_width)
        
        pygame.draw.circle(screen, self.person_color, (arm_end_x, arm_end_y), 4)
    
    def draw_right_arm(self, screen, center_x, body_y):
        arm_length = 45
        arm_end_x = center_x + arm_length
        arm_end_y = body_y + 25
        
        pygame.draw.line(screen, COLORS['shadow_light'], 
                        (center_x + 1, body_y + 1), (arm_end_x + 1, arm_end_y + 1), 
                        self.line_width)
        
        pygame.draw.line(screen, self.person_color, 
                        (center_x, body_y), (arm_end_x, arm_end_y), self.line_width)
        
        pygame.draw.circle(screen, self.person_color, (arm_end_x, arm_end_y), 4)
    
    def draw_left_leg(self, screen, center_x, body_end_y):
        leg_length = 45
        leg_end_x = center_x - leg_length
        leg_end_y = body_end_y + 45
        
        pygame.draw.line(screen, COLORS['shadow_light'], 
                        (center_x + 1, body_end_y + 1), (leg_end_x + 1, leg_end_y + 1), 
                        self.line_width)
        
        pygame.draw.line(screen, self.person_color, 
                        (center_x, body_end_y), (leg_end_x, leg_end_y), self.line_width)
        
        pygame.draw.line(screen, self.person_color,
                        (leg_end_x, leg_end_y), (leg_end_x - 8, leg_end_y), 3)
    
    def draw_right_leg(self, screen, center_x, body_end_y):
        leg_length = 45
        leg_end_x = center_x + leg_length
        leg_end_y = body_end_y + 45
        
        pygame.draw.line(screen, COLORS['shadow_light'], 
                        (center_x + 1, body_end_y + 1), (leg_end_x + 1, leg_end_y + 1), 
                        self.line_width)
        
        pygame.draw.line(screen, self.person_color, 
                        (center_x, body_end_y), (leg_end_x, leg_end_y), self.line_width)
        
        pygame.draw.line(screen, self.person_color,
                        (leg_end_x, leg_end_y), (leg_end_x + 8, leg_end_y), 3)
    
    def draw_animated_hangman(self, screen, wrong_guesses, x, y, animation_progress=1.0):
        self.draw(screen, wrong_guesses, x, y)