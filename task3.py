import sys
import secrets
import hmac
import hashlib
from typing import List, Tuple, Optional
from itertools import product
from tabulate import tabulate


class Dice:
    """Represents a dice with arbitrary face values."""
    
    def __init__(self, faces: List[int]):
        if len(faces) != 6:
            raise ValueError("Dice must have exactly 6 faces")
        self.faces = faces
    
    def get_face_value(self, index: int) -> int:
        """Get the value of the face at given index (0-5)."""
        if not 0 <= index <= 5:
            raise ValueError("Face index must be between 0 and 5")
        return self.faces[index]
    
    def __str__(self) -> str:
        return f"[{','.join(map(str, self.faces))}]"
    
    def __repr__(self) -> str:
        return f"Dice({self.faces})"


class DiceConfigParser:
    """Parses and validates dice configuration from command line arguments."""
    
    @staticmethod
    def parse_dice_list(args: List[str]) -> List[Dice]:
        """Parse command line arguments into a list of Dice objects."""
        if len(args) < 3:
            raise ValueError("At least 3 dice are required")
        
        dice_list = []
        for i, arg in enumerate(args):
            try:
                faces = [int(x.strip()) for x in arg.split(',')]
                if len(faces) != 6:
                    raise ValueError(f"Dice {i+1} must have exactly 6 comma-separated integers")
                dice_list.append(Dice(faces))
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Dice {i+1} contains non-integer values: {arg}")
                raise
        
        return dice_list


class SecureRandomGenerator:
    """Handles cryptographically secure random number generation and HMAC calculation."""
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a cryptographically secure 256-bit key."""
        return secrets.token_bytes(32)  # 32 bytes = 256 bits
    
    @staticmethod
    def generate_secure_random(max_value: int) -> int:
        """Generate a uniformly distributed random integer in range [0, max_value]."""
        return secrets.randbelow(max_value + 1)
    
    @staticmethod
    def calculate_hmac(key: bytes, message: str) -> str:
        """Calculate HMAC-SHA3-256 of the message with the given key."""
        return hmac.new(key, message.encode('utf-8'), hashlib.sha3_256).hexdigest().upper()


class FairRandomProtocol:
    """Implements the fair random number generation protocol."""
    
    def __init__(self, random_gen: SecureRandomGenerator):
        self.random_gen = random_gen
    
    def generate_fair_random(self, max_value: int) -> Tuple[int, str, bytes]:
        """
        Generate a fair random number using the protocol.
        Returns: (computer_number, hmac, key)
        """
        computer_number = self.random_gen.generate_secure_random(max_value)
        
        key = self.random_gen.generate_key()
        
        hmac_value = self.random_gen.calculate_hmac(key, str(computer_number))
        
        return computer_number, hmac_value, key
    
    def combine_numbers(self, computer_number: int, user_number: int, max_value: int) -> int:
        """Combine computer and user numbers using modular arithmetic."""
        return (computer_number + user_number) % (max_value + 1)


class ProbabilityCalculator:
    """Calculates win probabilities between dice pairs."""
    
    @staticmethod
    def calculate_win_probability(dice1: Dice, dice2: Dice) -> float:
        """Calculate probability that dice1 wins against dice2."""
        wins = 0
        total = 0
        
        for face1 in dice1.faces:
            for face2 in dice2.faces:
                total += 1
                if face1 > face2:
                    wins += 1
        
        return wins / total if total > 0 else 0.0


class TableGenerator:
    """Generates ASCII tables for displaying probabilities."""
    
    def __init__(self, probability_calc: ProbabilityCalculator):
        self.probability_calc = probability_calc
    
    def generate_probability_table(self, dice_list: List[Dice]) -> str:
        """Generate a probability table showing win rates between all dice pairs."""
        headers = [f"Dice {i+1}" for i in range(len(dice_list))]
        table_data = []
        
        for i, dice1 in enumerate(dice_list):
            row = [f"Dice {i+1}"]
            for j, dice2 in enumerate(dice_list):
                if i == j:
                    row.append("-")
                else:
                    prob = self.probability_calc.calculate_win_probability(dice1, dice2)
                    row.append(f"{prob:.3f}")
            table_data.append(row)
        
        return tabulate(table_data, headers=[""] + headers, tablefmt="grid")


class DiceGame:
    """Main game controller."""
    
    def __init__(self, dice_list: List[Dice]):
        self.dice_list = dice_list
        self.random_gen = SecureRandomGenerator()
        self.fair_protocol = FairRandomProtocol(self.random_gen)
        self.probability_calc = ProbabilityCalculator()
        self.table_gen = TableGenerator(self.probability_calc)
        
        self.computer_dice: Optional[Dice] = None
        self.user_dice: Optional[Dice] = None
        self.computer_goes_first = False
    
    def display_error(self, message: str):
        """Display error message with usage example."""
        print(f"Error: {message}")
        print("\nUsage example:")
        print("python game.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
        print("\nEach dice must have exactly 6 comma-separated integers.")
        print("At least 3 dice are required.")
    
    def get_user_choice(self, options: List[str], prompt: str = "Your selection: ") -> str:
        """Get user choice from a list of options."""
        while True:
            choice = input(prompt).strip().upper()
            if choice in [str(i) for i in range(len(options))] + ['X', '?']:
                return choice
            print("Invalid choice. Please try again.")
    
    def display_menu(self, options: List[str], show_exit_help: bool = True):
        """Display menu options."""
        for i, option in enumerate(options):
            print(f"{i} - {option}")
        if show_exit_help:
            print("X - exit")
            print("? - help")
    
    def determine_first_player(self) -> bool:
        """Determine who goes first using fair random generation. Returns True if computer goes first."""
        print("Let's determine who makes the first move.")
        
        computer_number, hmac_value, key = self.fair_protocol.generate_fair_random(1)
        print(f"I selected a random value in the range 0..1 (HMAC={hmac_value}).")
        print("Try to guess my selection.")
        
        options = ["0", "1"]
        self.display_menu(options)
        
        while True:
            choice = self.get_user_choice(options)
            if choice == 'X':
                return False
            elif choice == '?':
                print("\nHelp: Choose 0 or 1 to guess the computer's selection.")
                print("If you guess correctly, you go first. Otherwise, computer goes first.\n")
                continue
            
            user_number = int(choice)
            break
        
        result = self.fair_protocol.combine_numbers(computer_number, user_number, 1)
        print(f"My selection: {computer_number} (KEY={key.hex().upper()}).")
        
        computer_goes_first = (user_number != computer_number)
        
        if computer_goes_first:
            print("I make the first move and choose the dice.")
        else:
            print("You guessed correctly! You make the first move and choose the dice.")
        
        return computer_goes_first
    
    def computer_select_dice(self, available_dice: List[int]) -> int:
        """Computer selects a dice from available options."""
        return self.random_gen.generate_secure_random(len(available_dice) - 1)
    
    def user_select_dice(self, available_dice: List[int]) -> Optional[int]:
        """User selects a dice from available options."""
        print("Choose your dice:")
        options = [str(self.dice_list[i]) for i in available_dice]
        self.display_menu(options)
        
        while True:
            choice = self.get_user_choice(options)
            if choice == 'X':
                return None
            elif choice == '?':
                print("\nProbability table:")
                print(self.table_gen.generate_probability_table(self.dice_list))
                print()
                continue
            
            return available_dice[int(choice)]
    
    def perform_dice_selection(self):
        """Handle dice selection phase."""
        available_dice = list(range(len(self.dice_list)))
        
        if self.computer_goes_first:
            computer_choice = self.computer_select_dice(available_dice)
            self.computer_dice = self.dice_list[computer_choice]
            print(f"I choose the {self.computer_dice} dice.")
            
            available_dice.remove(computer_choice)
            
            user_choice = self.user_select_dice(available_dice)
            if user_choice is None:
                return False
            self.user_dice = self.dice_list[user_choice]
            print(f"You choose the {self.user_dice} dice.")
        else:
            user_choice = self.user_select_dice(available_dice)
            if user_choice is None:
                return False
            self.user_dice = self.dice_list[user_choice]
            print(f"You choose the {self.user_dice} dice.")
            
            available_dice.remove(user_choice)
            
            computer_choice = self.computer_select_dice(available_dice)
            self.computer_dice = self.dice_list[computer_choice]
            print(f"I choose the {self.computer_dice} dice.")
        
        return True
    
    def perform_roll(self, dice: Dice, player_name: str) -> Optional[int]:
        """Perform a dice roll using fair random generation."""
        print(f"It's time for {player_name} roll.")
        
        computer_number, hmac_value, key = self.fair_protocol.generate_fair_random(5)
        print(f"I selected a random value in the range 0..5 (HMAC={hmac_value}).")
        print("Add your number modulo 6.")
        
        options = [str(i) for i in range(6)]
        self.display_menu(options)
        
        while True:
            choice = self.get_user_choice(options)
            if choice == 'X':
                return None
            elif choice == '?':
                print(f"\nHelp: Choose a number from 0 to 5.")
                print("This will be added to my secret number to determine the dice face.")
                print("The result will be (my_number + your_number) % 6\n")
                continue
            
            user_number = int(choice)
            break
        
        result_index = self.fair_protocol.combine_numbers(computer_number, user_number, 5)
        face_value = dice.get_face_value(result_index)
        
        print(f"My number is {computer_number} (KEY={key.hex().upper()}).")
        print(f"The fair number generation result is {computer_number} + {user_number} = {result_index} (mod 6).")
        print(f"{player_name.capitalize()} roll result is {face_value}.")
        
        return face_value
    
    def play_game(self) -> bool:
        """Play one complete game. Returns True if game completed successfully."""
        self.computer_goes_first = self.determine_first_player()
        
        if not self.perform_dice_selection():
            return False
        
        computer_roll = self.perform_roll(self.computer_dice, "my")
        if computer_roll is None:
            return False
        
        user_roll = self.perform_roll(self.user_dice, "your")
        if user_roll is None:
            return False
        
        if user_roll > computer_roll:
            print(f"You win ({user_roll} > {computer_roll})!")
        elif computer_roll > user_roll:
            print(f"I win ({computer_roll} > {user_roll})!")
        else:
            print(f"It's a tie ({user_roll} = {computer_roll})!")
        
        return True
    
    def run(self):
        """Main game loop."""
        try:
            self.play_game()
        except KeyboardInterrupt:
            print("\nGame interrupted by user.")
        except Exception as e:
            print(f"An error occurred: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Error: No dice configurations provided.")
        print("\nUsage example:")
        print("python game.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
        print("\nEach dice must have exactly 6 comma-separated integers.")
        print("At least 3 dice are required.")
        return
    
    try:
        dice_list = DiceConfigParser.parse_dice_list(sys.argv[1:])
        
        game = DiceGame(dice_list)
        game.run()
        
    except ValueError as e:
        game = DiceGame([]) 
        game.display_error(str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()