import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from game_engine import GameEngine
    from ui_manager import UIManager
    from settings import *
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all game files are in the same directory.")
    sys.exit(1)

class HangmanApp:    
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        
        try:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("🎮 Hangman Game")
        except pygame.error as e:
            print(f"Display error: {e}")
            print("Make sure you have a display available (X11/Wayland forwarding for WSL)")
            sys.exit(1)
        
        try:
            icon = pygame.Surface((32, 32))
            icon.fill(COLORS['primary'])
            pygame.display.set_icon(icon)
        except:
            pass
        
        self.clock = pygame.time.Clock()
        
        try:
            self.game_engine = GameEngine()
            self.ui_manager = UIManager(self.screen)
        except Exception as e:
            print(f"Game initialization error: {e}")
            pygame.quit()
            sys.exit(1)
        
        self.running = True
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            try:
                self.ui_manager.handle_event(event, self.game_engine)
            except Exception as e:
                print(f"Event handling error: {e}")
    
    def update(self):
        try:
            self.ui_manager.update()
        except Exception as e:
            print(f"Update error: {e}")
    
    def render(self):
        try:
            if not pygame.display.get_surface():
                self.running = False
                return
            
            self.draw_gradient_background()
            
            self.ui_manager.render(self.game_engine)
            
            pygame.display.flip()
        except Exception as e:
            print(f"Render error: {e}")
            self.running = False
    
    def draw_gradient_background(self):
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(COLORS['bg_start'][0] * (1 - ratio) + COLORS['bg_end'][0] * ratio)
            g = int(COLORS['bg_start'][1] * (1 - ratio) + COLORS['bg_end'][1] * ratio)
            b = int(COLORS['bg_start'][2] * (1 - ratio) + COLORS['bg_end'][2] * ratio)
            
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
    
    def run(self):
        try:
            while self.running:
                self.handle_events()
                if not self.running:
                    break
                self.update()
                self.render()
                self.clock.tick(FPS)
        except KeyboardInterrupt:
            print("\nGame interrupted by user.")
        except Exception as e:
            print(f"Game loop error: {e}")
        finally:
            pygame.quit()
            sys.exit()

def main():
    try:
        app = HangmanApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        if pygame.get_init():
            pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()