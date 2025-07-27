import sys
import random
import hmac
import hashlib
import secrets

class Dice:
    def __init__(self, faces):
        if not all(isinstance(f, int) for f in faces):
            raise ValueError("Dice must have only integer faces.")
        self.faces = faces

    def roll(self, secret=None):
        if secret is None:
            return random.choice(self.faces)
        else:
            index = int(secret, 16) % len(self.faces)
            return self.faces[index]

class HMACGenerator:
    def __init__(self):
        self.key = secrets.token_bytes(16)
        self.nonce = secrets.token_hex(16)

    def generate_commitment(self, choice):
        msg = f"{self.nonce}:{choice}".encode()
        h = hmac.new(self.key, msg, hashlib.sha3_256)
        return h.hexdigest()

    def verify_commitment(self, commitment, choice, nonce):
        msg = f"{nonce}:{choice}".encode()
        h = hmac.new(self.key, msg, hashlib.sha3_256)
        return h.hexdigest() == commitment

class Game:
    def __init__(self, dice_configs):
        self.dice_list = []
        self.parse_dice(dice_configs)

    def parse_dice(self, configs):
        if len(configs) < 3:
            raise ValueError("You must specify at least 3 dice. Example: python dice_game.py 2,3,4,5,6,1 1,1,1,1,9,9 7,7,7,2,2,2")
        for i, config in enumerate(configs):
            try:
                faces = list(map(int, config.split(',')))
                self.dice_list.append(Dice(faces))
            except Exception:
                raise ValueError(f"Invalid format in dice {i+1}: '{config}'. Dice must be comma-separated integers.")

    def fair_coin_toss(self):
        print("\n🔒 Tossing a fair coin using HMAC to decide who picks first...")
        hmac_gen = HMACGenerator()
        coin = random.choice(["heads", "tails"])
        commitment = hmac_gen.generate_commitment(coin)
        print(f"HMAC (SHA3-256) commitment: {commitment}")
        input("Press Enter to reveal the result...")

        print(f"Revealed choice: {coin}")
        print(f"Nonce: {hmac_gen.nonce}")
        print(f"Verification key: {hmac_gen.key.hex()}")
        if hmac_gen.verify_commitment(commitment, coin, hmac_gen.nonce):
            print("✅ Commitment verified.")
        else:
            print("❌ HMAC verification failed!")

        return "user" if coin == "heads" else "computer"

    def user_select_dice(self):
        while True:
            print("\n🎲 Available Dice:")
            for idx, dice in enumerate(self.dice_list):
                print(f"{idx + 1}. {dice.faces}")
            print("H. Help")
            print("E. Exit")
            choice = input("Select your dice (number): ").strip().lower()
            if choice == 'e':
                print("Game exited by user.")
                sys.exit()
            if choice == 'h':
                print("Help: Enter a number to select your dice. Each dice has 6 faces. Highest roll wins.")
                continue
            if choice.isdigit() and 1 <= int(choice) <= len(self.dice_list):
                return int(choice) - 1
            print("❗ Invalid choice. Try again.")

    def computer_select_dice(self):
        index = random.randint(0, len(self.dice_list) - 1)
        print(f"\n🤖 Computer selected dice {index + 1}: {self.dice_list[index].faces}")
        return index

    def play_round(self):
        starter = self.fair_coin_toss()

        if starter == "user":
            user_idx = self.user_select_dice()
            comp_idx = self.computer_select_dice()
        else:
            comp_idx = self.computer_select_dice()
            user_idx = self.user_select_dice()

        hmac_gen = HMACGenerator()
        comp_secret = secrets.token_hex(16)
        comp_commit = hmac_gen.generate_commitment(comp_secret)
        print(f"\n🤖 Computer has committed to a roll. Commitment: {comp_commit}")

        user_roll = self.dice_list[user_idx].roll()
        print(f"🎯 You rolled: {user_roll}")

        print(f"\n🔓 Computer reveals secret: {comp_secret}")
        print(f"Verification key: {hmac_gen.key.hex()}")
        print(f"Nonce: {hmac_gen.nonce}")
        if not hmac_gen.verify_commitment(comp_commit, comp_secret, hmac_gen.nonce):
            print("❌ Computer's commitment verification failed. Exiting.")
            sys.exit(1)

        comp_roll = self.dice_list[comp_idx].roll(comp_secret)
        print(f"🤖 Computer rolled: {comp_roll}")

        if user_roll > comp_roll:
            print("🏆 You win!")
        elif comp_roll > user_roll:
            print("💻 Computer wins!")
        else:
            print("⚖️ It's a draw!")

def main():
    try:
        if len(sys.argv) < 4:
            raise ValueError("❗ Error: You must pass at least 3 dice as command line arguments.\n"
                             "Example: python dice_game.py 2,3,4,4,5,6 1,1,8,8,6,6 7,5,3,7,5,3")
        game = Game(sys.argv[1:])
        game.play_round()
    except ValueError as ve:
        print(f"❌ {ve}")
    except Exception as e:
        print("❌ Unexpected error occurred.")
        print(str(e))

if __name__ == "__main__":
    main()