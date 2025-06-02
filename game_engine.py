import random
from enum import Enum
from settings import GAME

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
    PAUSED = "paused"

class GameEngine:
    
    def __init__(self):
        self.word_list = [
            "APPLE", "HOUSE", "WATER", "MUSIC", "LIGHT",
            "BEACH", "CLOUD", "DANCE", "EARTH", "FLAME",
            "HEART", "MAGIC", "OCEAN", "PEACE", "SMILE",
            
            "COMPUTER", "RAINBOW", "KITCHEN", "FREEDOM", "JOURNEY",
            "MYSTERY", "BALLOON", "COSTUME", "DIAMOND", "ELEPHANT",
            "FANTASY", "GALLERY", "HARMONY", "IMAGINE", "JUSTICE",
            
            "BEAUTIFUL", "CHOCOLATE", "DANGEROUS", "EXCELLENT", "FIREWORKS",
            "GEOGRAPHY", "HURRICANE", "INVISIBLE", "KNOWLEDGE", "LANDSCAPE",
            "ADVENTURE", "SCIENTIST", "TELEPHONE", "WONDERFUL", "ALGORITHM",
        ]
        
        self.reset_game()
    
    def reset_game(self):
        self.state = GameState.MENU
        self.current_word = ""
        self.guessed_letters = set()
        self.correct_letters = set()
        self.wrong_guesses = 0
        self.max_wrong_guesses = GAME['max_wrong_guesses']
        self.score = 0
        self.hint_used = False
    
    def start_new_game(self):
        self.current_word = random.choice(self.word_list).upper()
        self.guessed_letters = set()
        self.correct_letters = set()
        self.wrong_guesses = 0
        self.state = GameState.PLAYING
        self.hint_used = False
    
    def make_guess(self, letter):
        if self.state != GameState.PLAYING:
            return {"status": "invalid", "message": "Game not in progress"}
        
        letter = letter.upper()
        
        if letter in self.guessed_letters:
            return {"status": "already_guessed", "message": f"Already guessed {letter}"}
        
        self.guessed_letters.add(letter)
        
        if letter in self.current_word:
            self.correct_letters.add(letter)
            
            if self.is_word_complete():
                self.state = GameState.WON
                self.calculate_score()
                return {"status": "won", "message": "Congratulations! You won!"}
            
            return {"status": "correct", "message": f"Good guess! {letter} is in the word"}
        else:
            self.wrong_guesses += 1
            
            if self.wrong_guesses >= self.max_wrong_guesses:
                self.state = GameState.LOST
                return {"status": "lost", "message": f"Game over! The word was {self.current_word}"}
            
            return {"status": "incorrect", "message": f"Sorry, {letter} is not in the word"}
    
    def is_word_complete(self):
        return all(letter in self.correct_letters for letter in self.current_word)
    
    def get_display_word(self):
        return ''.join([letter if letter in self.correct_letters else '_' 
                       for letter in self.current_word])
    
    def get_wrong_letters(self):
        return self.guessed_letters - self.correct_letters
    
    def get_remaining_guesses(self):
        return self.max_wrong_guesses - self.wrong_guesses
    
    def get_hint(self):
        if self.hint_used or self.state != GameState.PLAYING:
            return None
        
        unguessed = [letter for letter in self.current_word 
                    if letter not in self.correct_letters]
        
        if not unguessed:
            return None
        
        hint_letter = random.choice(unguessed)
        self.correct_letters.add(hint_letter)
        self.guessed_letters.add(hint_letter)
        self.hint_used = True
        
        if self.is_word_complete():
            self.state = GameState.WON
            self.calculate_score()
        
        return hint_letter
    
    def calculate_score(self):
        if self.state == GameState.WON:
            base_score = 100
            
            guess_bonus = (self.max_wrong_guesses - self.wrong_guesses) * 10
            
            length_bonus = len(self.current_word) * 5
            
            hint_penalty = 25 if self.hint_used else 0
            
            self.score = max(0, base_score + guess_bonus + length_bonus - hint_penalty)
        else:
            self.score = 0
    
    def get_game_stats(self):
        return {
            'word': self.current_word,
            'display_word': self.get_display_word(),
            'guessed_letters': sorted(list(self.guessed_letters)),
            'correct_letters': sorted(list(self.correct_letters)),
            'wrong_letters': sorted(list(self.get_wrong_letters())),
            'wrong_guesses': self.wrong_guesses,
            'remaining_guesses': self.get_remaining_guesses(),
            'score': self.score,
            'hint_used': self.hint_used,
            'state': self.state,
        }
    
    def is_letter_available(self, letter):
        return letter.upper() not in self.guessed_letters
    
    def get_alphabet_status(self):
        alphabet = {}
        for i in range(26):
            letter = chr(ord('A') + i)
            if letter in self.correct_letters:
                alphabet[letter] = 'correct'
            elif letter in self.get_wrong_letters():
                alphabet[letter] = 'wrong'
            else:
                alphabet[letter] = 'available'
        return alphabet