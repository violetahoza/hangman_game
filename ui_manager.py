import pygame
import math
from game_engine import GameState
from hangman_drawer import HangmanDrawer
from settings import *

class Button:
    
    def __init__(self, x, y, width, height, text, font_size=FONTS['button']):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_clicked = False
        self.enabled = True
        self.animation_scale = 1.0
    
    def handle_event(self, event):
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_hovered != was_hovered:
                self.animation_scale = 1.05 if self.is_hovered else 1.0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_clicked = True
                return True
        return False
    
    def update(self):
        target_scale = 1.05 if self.is_hovered and self.enabled else 1.0
        self.animation_scale += (target_scale - self.animation_scale) * 0.2
    
    def draw(self, screen):
        scale_offset = int((self.animation_scale - 1.0) * self.rect.width / 2)
        scaled_rect = pygame.Rect(
            self.rect.x - scale_offset,
            self.rect.y - scale_offset,
            int(self.rect.width * self.animation_scale),
            int(self.rect.height * self.animation_scale)
        )
        
        if not self.enabled:
            color = COLORS['button_disabled']
        elif self.is_hovered:
            color = COLORS['button_hover']
        else:
            color = COLORS['button']
        
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, COLORS['shadow_dark'], shadow_rect, border_radius=12)
        
        pygame.draw.rect(screen, color, scaled_rect, border_radius=12)
        
        border_color = COLORS['accent'] if self.is_hovered and self.enabled else COLORS['border']
        pygame.draw.rect(screen, border_color, scaled_rect, 2, border_radius=12)
        
        text_color = COLORS['text_light'] if self.enabled else COLORS['text_disabled']
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        screen.blit(text_surface, text_rect)

class LetterButton(Button):
    
    def __init__(self, x, y, letter):
        super().__init__(x, y, 45, 45, letter, FONTS['body'])
        self.letter = letter
        self.status = 'available'
        self.pulse_alpha = 0
    
    def update(self):
        super().update()
        if self.status == 'correct':
            self.pulse_alpha = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 20
    
    def draw(self, screen):
        scale_offset = int((self.animation_scale - 1.0) * self.rect.width / 2)
        scaled_rect = pygame.Rect(
            self.rect.x - scale_offset,
            self.rect.y - scale_offset,
            int(self.rect.width * self.animation_scale),
            int(self.rect.height * self.animation_scale)
        )
        
        if self.status == 'correct':
            color = COLORS['success']
            border_color = COLORS['success_dark']
        elif self.status == 'wrong':
            color = COLORS['danger']
            border_color = COLORS['danger_dark']
        elif self.is_hovered and self.enabled:
            color = COLORS['button_hover']
            border_color = COLORS['accent']
        else:
            color = COLORS['button_light']
            border_color = COLORS['border']
        
        if not self.enabled:
            color = COLORS['button_disabled']
            border_color = COLORS['border_light']
        
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, COLORS['shadow_light'], shadow_rect, border_radius=8)
        
        pygame.draw.rect(screen, color, scaled_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, scaled_rect, 2, border_radius=8)
        
        if self.status == 'correct' and self.pulse_alpha > 0:
            pulse_surface = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(pulse_surface, (*COLORS['success'], int(self.pulse_alpha)), 
                           (0, 0, *scaled_rect.size), border_radius=8)
            screen.blit(pulse_surface, scaled_rect.topleft)
        
        text_color = COLORS['text_light'] if self.enabled else COLORS['text_disabled']
        if self.status in ['correct', 'wrong']:
            text_color = COLORS['text_light']
        else:
            text_color = COLORS['text_primary']
            
        text_surface = self.font.render(self.letter, True, text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        screen.blit(text_surface, text_rect)

class UIManager:
    
    def __init__(self, screen):
        self.screen = screen
        self.hangman_drawer = HangmanDrawer()
        
        self.fonts = {}
        for name, size in FONTS.items():
            self.fonts[name] = pygame.font.Font(None, size)
        
        self.setup_buttons()
        
        self.title_pulse = 0
        self.fade_alpha = 255
        
    def setup_buttons(self):
        menu_center_x = WINDOW_WIDTH // 2 - (LAYOUT['button_width'] + 40) // 2
        self.new_game_button = Button(menu_center_x, 380, LAYOUT['button_width'] + 40, LAYOUT['button_height'] + 10, "New Game", FONTS['button'])
        self.quit_button = Button(menu_center_x, 460, LAYOUT['button_width'] + 40, LAYOUT['button_height'] + 10, "Quit Game", FONTS['button'])
        
        self.hint_button = Button(POSITIONS['info_panel_x'] + 25, 480, 110, 40, "Get Hint", FONTS['small'])
        self.menu_button = Button(POSITIONS['info_panel_x'] + 150, 480, 110, 40, "Main Menu", FONTS['small'])
        
        self.victory_new_game_button = Button(0, 0, LAYOUT['button_width'] + 20, LAYOUT['button_height'], "New Game", FONTS['button'])
        self.victory_menu_button = Button(0, 0, LAYOUT['button_width'] + 20, LAYOUT['button_height'], "Main Menu", FONTS['button'])
        
        self.letter_buttons = {}
        keyboard_layout = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]
        
        keyboard_start_x = 50
        keyboard_start_y = 490
        button_size = 45
        button_spacing = 50
        
        for row_idx, row in enumerate(keyboard_layout):
            row_offset = (10 - len(row)) * button_spacing // 2
            
            for col_idx, letter in enumerate(row):
                x = keyboard_start_x + row_offset + col_idx * button_spacing
                y = keyboard_start_y + row_idx * button_spacing
                self.letter_buttons[letter] = LetterButton(x, y, letter)
    
    def handle_event(self, event, game_engine):
        if game_engine.state == GameState.MENU:
            if self.new_game_button.handle_event(event):
                game_engine.start_new_game()
            elif self.quit_button.handle_event(event):
                pygame.quit()
                return
        
        elif game_engine.state == GameState.PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.unicode.isalpha():
                    letter = event.unicode.upper()
                    if game_engine.is_letter_available(letter):
                        game_engine.make_guess(letter)
            
            for letter, button in self.letter_buttons.items():
                if button.handle_event(event) and game_engine.is_letter_available(letter):
                    game_engine.make_guess(letter)
            
            if self.hint_button.handle_event(event):
                game_engine.get_hint()
            
            if self.menu_button.handle_event(event):
                game_engine.state = GameState.MENU
        
        elif game_engine.state in [GameState.WON, GameState.LOST]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  
                    game_engine.start_new_game()
                elif event.key == pygame.K_ESCAPE:  
                    game_engine.state = GameState.MENU
            
            if self.victory_new_game_button.handle_event(event):
                game_engine.start_new_game()
            elif self.victory_menu_button.handle_event(event):
                game_engine.state = GameState.MENU
    
    def update(self):
        self.title_pulse = math.sin(pygame.time.get_ticks() * 0.003) * 3
        
        self.new_game_button.update()
        self.quit_button.update()
        
        self.hint_button.update()
        self.menu_button.update()
        
        self.victory_new_game_button.update()
        self.victory_menu_button.update()
        
        for button in self.letter_buttons.values():
            button.update()
    
    def render(self, game_engine):
        if game_engine.state == GameState.MENU:
            self.render_menu()
        elif game_engine.state == GameState.PLAYING:
            self.render_game(game_engine)
        elif game_engine.state == GameState.WON:
            self.render_victory(game_engine)
        elif game_engine.state == GameState.LOST:
            self.render_defeat(game_engine)
    
    def render_menu(self):
        title_y = 120 + self.title_pulse
        
        shadow_offset = 3
        self.draw_text("HANGMAN", self.fonts['title'], COLORS['shadow_dark'], 
                      WINDOW_WIDTH // 2 + shadow_offset, title_y + shadow_offset, center=True)
        self.draw_text("HANGMAN", self.fonts['title'], COLORS['text_light'], 
                      WINDOW_WIDTH // 2, title_y, center=True)
        
        subtitle_y = title_y + 80
        self.draw_text("A Classic Word Guessing Game", 
                      self.fonts['subheading'], COLORS['text_light_secondary'], 
                      WINDOW_WIDTH // 2, subtitle_y, center=True)
        
        instruction_y = subtitle_y + 60
        self.draw_text("Guess the hidden word letter by letter", 
                      self.fonts['body'], COLORS['text_light_secondary'], 
                      WINDOW_WIDTH // 2, instruction_y, center=True)
        
        self.new_game_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        self.draw_decorative_elements()
    
    def render_game(self, game_engine):
        stats = game_engine.get_game_stats()
        
        self.draw_text("HANGMAN", self.fonts['heading'], COLORS['text_light'], 
                      WINDOW_WIDTH // 2, 25, center=True)
        
        self.hangman_drawer.draw(self.screen, stats['wrong_guesses'], 
                               POSITIONS['hangman_x'], POSITIONS['hangman_y'])
        
        self.draw_word(stats['display_word'])
        
        self.draw_keyboard(game_engine.get_alphabet_status())
        
        self.draw_info_panel(stats)
    
    def render_victory(self, game_engine):
        stats = game_engine.get_game_stats()
        
        title_y = 200
        
        pulse_offset = math.sin(pygame.time.get_ticks() * 0.01) * 5
        
        self.draw_text("VICTORY!", self.fonts['title'], COLORS['success'], 
                      WINDOW_WIDTH // 2, title_y + pulse_offset, center=True)
        
        self.draw_text(f"You discovered: {stats['word']}", self.fonts['subheading'], COLORS['text_light'], 
                      WINDOW_WIDTH // 2, title_y + 80, center=True)
        
        self.draw_text(f"Final Score: {stats['score']} points", self.fonts['subheading'], COLORS['accent'], 
                      WINDOW_WIDTH // 2, title_y + 120, center=True)
        
        button_y = title_y + 180
        button_spacing = 180
        center_x = WINDOW_WIDTH // 2
        
        self.victory_new_game_button.rect.x = center_x - button_spacing // 2 - self.victory_new_game_button.rect.width // 2
        self.victory_new_game_button.rect.y = button_y
        self.victory_new_game_button.draw(self.screen)
        
        self.victory_menu_button.rect.x = center_x + button_spacing // 2 - self.victory_menu_button.rect.width // 2
        self.victory_menu_button.rect.y = button_y
        self.victory_menu_button.draw(self.screen)
        
        self.draw_text("Press SPACE for new game or ESC for menu", self.fonts['small'], 
                      COLORS['text_light_secondary'], WINDOW_WIDTH // 2, button_y + 80, center=True)
    
    def render_defeat(self, game_engine):
        stats = game_engine.get_game_stats()
        
        title_y = 180
        
        self.draw_text("DEFEAT", self.fonts['title'], COLORS['danger'], 
                      WINDOW_WIDTH // 2, title_y, center=True)
        
        self.draw_text(f"The word was: {stats['word']}", self.fonts['subheading'], COLORS['text_light'], 
                      WINDOW_WIDTH // 2, title_y + 70, center=True)
        
        hangman_x = WINDOW_WIDTH // 2 - 100
        hangman_y = title_y + 120
        self.hangman_drawer.draw(self.screen, 6, hangman_x, hangman_y)
        
        button_y = title_y + 300
        button_spacing = 180
        center_x = WINDOW_WIDTH // 2
        
        self.victory_new_game_button.rect.x = center_x - button_spacing // 2 - self.victory_new_game_button.rect.width // 2
        self.victory_new_game_button.rect.y = button_y
        self.victory_new_game_button.draw(self.screen)
        
        self.victory_menu_button.rect.x = center_x + button_spacing // 2 - self.victory_menu_button.rect.width // 2
        self.victory_menu_button.rect.y = button_y
        self.victory_menu_button.draw(self.screen)
        
        self.draw_text("Press SPACE for new game or ESC for menu", self.fonts['small'], 
                      COLORS['text_light_secondary'], WINDOW_WIDTH // 2, button_y + 80, center=True)
    
    def draw_word(self, display_word):
        letter_size = 50
        letter_spacing = 20
        total_width = len(display_word) * (letter_size + letter_spacing) - letter_spacing
        start_x = (WINDOW_WIDTH - total_width) // 2
        word_y = 400  
        
        for i, letter in enumerate(display_word):
            x = start_x + i * (letter_size + letter_spacing)
            
            letter_rect = pygame.Rect(x, word_y, letter_size, letter_size)
            
            shadow_rect = letter_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, COLORS['shadow_light'], shadow_rect, border_radius=10)
            
            box_color = COLORS['card_light'] if letter != '_' else COLORS['card']
            pygame.draw.rect(self.screen, box_color, letter_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS['accent'], letter_rect, 3, border_radius=10)
            
            if letter != '_':
                self.draw_text(letter, self.fonts['heading'], COLORS['text_primary'], 
                              x + letter_size // 2, word_y + letter_size // 2, center=True)
    
    def draw_keyboard(self, alphabet_status):
        for letter, button in self.letter_buttons.items():
            button.status = alphabet_status[letter]
            button.enabled = alphabet_status[letter] == 'available'
            button.draw(self.screen)
    
    def draw_info_panel(self, stats):
        panel_x = POSITIONS['info_panel_x'] 
        panel_y = POSITIONS['info_panel_y']
        panel_width = POSITIONS['info_panel_width']
        panel_height = 300 
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(self.screen, COLORS['shadow_dark'], shadow_rect, border_radius=15)
        
        pygame.draw.rect(self.screen, COLORS['card'], panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['accent'], panel_rect, 3, border_radius=15)
        
        y_offset = panel_y + 25
        
        self.draw_text("Game Statistics", self.fonts['subheading'], COLORS['text_primary'], 
                      panel_x + 25, y_offset)
        y_offset += 50
        
        remaining = stats['remaining_guesses']
        if remaining > 3:
            color = COLORS['success']
        elif remaining > 1:
            color = COLORS['warning']
        else:
            color = COLORS['danger']
            
        self.draw_text(f"Guesses left: {remaining}", self.fonts['body'], color, 
                      panel_x + 25, y_offset)
        y_offset += 35
        
        progress = len(stats['correct_letters']) / len(stats['word']) if stats['word'] else 0
        self.draw_text(f"Progress: {progress:.0%}", self.fonts['body'], COLORS['text_primary'], 
                      panel_x + 25, y_offset)
        
        bar_y = y_offset + 25
        self.draw_progress_bar(panel_x + 25, bar_y, 280, 12, progress, 
                              COLORS['border_light'], COLORS['success'])
        y_offset += 55
        
        self.draw_text(f"Word length: {len(stats['word'])} letters", self.fonts['body'], 
                      COLORS['text_primary'], panel_x + 25, y_offset)
        y_offset += 35
        
        if stats['wrong_letters']:
            self.draw_text("Incorrect guesses:", self.fonts['body'], COLORS['text_primary'], 
                          panel_x + 25, y_offset)
            y_offset += 25
            wrong_text = ' • '.join(stats['wrong_letters'])
            self.draw_text(wrong_text, self.fonts['small'], COLORS['danger'], 
                          panel_x + 25, y_offset)
        
        hint_y = panel_y + 250
        hint_text = "Hint already used" if stats['hint_used'] else "Hint available"
        hint_color = COLORS['text_secondary'] if stats['hint_used'] else COLORS['accent']
        self.draw_text(hint_text, self.fonts['body'], hint_color, 
                      panel_x + 25, hint_y)
        
        self.hint_button.enabled = not stats['hint_used']
        self.hint_button.draw(self.screen)
        self.menu_button.draw(self.screen)
    
    def draw_text(self, text, font, color, x, y, center=False):
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))
    
    def draw_progress_bar(self, x, y, width, height, progress, bg_color, fill_color):
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=height // 2)
        
        fill_width = int(width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=height // 2)
        
        pygame.draw.rect(self.screen, COLORS['border'], bg_rect, 2, border_radius=height // 2)
    
    def draw_decorative_elements(self):
        time_ms = pygame.time.get_ticks()
        
        for i in range(8):
            angle = (time_ms * 0.001 + i * 0.785) % (2 * math.pi)
            x = WINDOW_WIDTH // 2 + math.cos(angle) * (150 + i * 20)
            y = WINDOW_HEIGHT // 2 + math.sin(angle) * (80 + i * 10)
            
            alpha = int(50 + 30 * math.sin(time_ms * 0.003 + i))
            size = 3 + int(2 * math.sin(time_ms * 0.002 + i))
            
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*COLORS['accent'], alpha), (size, size), size)
            self.screen.blit(particle_surface, (int(x - size), int(y - size)))