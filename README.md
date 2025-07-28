# Secure Dice Game with HMAC Commitments

A Python implementation of a dice game that incorporates secure cryptographic techniques to ensure fairness and prevent cheating. The game uses HMAC commitments for secure dice selection and roll verification.

## Features

- Secure dice selection using HMAC commitments
- Fair coin toss to determine who picks first
- Multiple custom dice configurations
- Secure roll verification using cryptographic hashes
- User-friendly interface with help option
- Probability analysis between dice pairs
- Secure commitment and verification system

## How to Play

1. Run the game using Python:
   ```bash
   python task3.py dice1 dice2 dice3
   ```
   - You must specify at least 3 dice configurations as command line arguments
   - Each dice configuration should be comma-separated integers (e.g., "2,3,4,4,5,6")
   - Use the --help flag to see available options: `python task3.py --help`

2. The game will:
   - Show probability table of dice winning chances
   - Perform a fair coin toss using HMAC to determine who picks first
   - Allow you to select a dice from the available options
   - Show computer's dice selection
   - Commit to a secure roll using HMAC
   - Reveal and verify all rolls
   - Display the winner

## Security Features

- **HMAC Commitments**: Uses SHA3-256 for secure commitments
- **Nonce-based Verification**: Each commitment includes a unique nonce
- **Secure Key Generation**: Uses cryptographically secure random numbers
- **Roll Verification**: Ensures rolls cannot be manipulated after commitment
- **Secure Communication**: All commitments are verified before reveal
- **Fair Random Selection**: Uses cryptographically secure random numbers for all selections

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements
- Python 3.8 or higher
- cryptography library
- argparse library
- tabulate library

## Usage Example

```bash
python task3.py "2,2,4,4,9,9" "6,8,1,1,8,6" "7,5,3,7,5,3"
```

Each dice must have exactly 6 comma-separated integers. The game will:
1. Display a probability table showing winning chances between dice pairs
2. Use a fair random protocol to determine who picks first
3. Allow players to select their dice
4. Perform secure rolls with commitment and verification
5. Display the winner

## Screenshots

### Game Start - Probability Table
![Game Start](screenshots/Screenshot%20%28288%29.png)

### Game Play - Dice Selection and Roll
![Game Play](screenshots/Screenshot%20%28289%29.png)

### Fair Random Selection
![Fair Random](screenshots/Screenshot%20%28290%29.png)

### Dice Roll and Verification
![Dice Roll](screenshots/Screenshot%20%28291%29.png)

- Python 3.x
- Standard Python libraries (random, hmac, hashlib, secrets)

## Error Handling

The game includes several error checks:
- Invalid dice configurations
- Insufficient dice configurations
- Invalid user input
- HMAC verification failures

## Exit Options

- Type 'E' at any dice selection prompt to exit the game
- Type 'H' to view help information

## Example Usage

```bash
python task3.py 2,3,4,5,6,1 1,1,1,1,9,9 7,7,7,2,2,2
```

This will create a game with three custom dice:
1. Dice 1: Faces [2, 3, 4, 5, 6, 1]
2. Dice 2: Faces [1, 1, 1, 1, 9, 9]
3. Dice 3: Faces [7, 7, 7, 2, 2, 2]
