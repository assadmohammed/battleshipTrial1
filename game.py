import random
import json
from typing import List, Dict, Tuple
import os

class Ship:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.positions = []
        self.hits = 0

    def is_sunk(self) -> bool:
        return self.hits == self.size

class Player:
    def __init__(self, name: str):
        self.name = name
        self.wins = 0
        self.losses = 0

class Battleship:
    def __init__(self):
        self.board_size = 10
        self.column_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.ships = {
            "player": [
                Ship("Aircraft Carrier", 5),
                Ship("Battleship", 4),
                Ship("Cruiser", 3),
                Ship("Submarine", 3),
                Ship("Destroyer", 2)
            ],
            "computer": [
                Ship("Aircraft Carrier", 5),
                Ship("Battleship", 4),
                Ship("Cruiser", 3),
                Ship("Submarine", 3),
                Ship("Destroyer", 2)
            ]
        }
        self.player_board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.computer_board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.player_guess_board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.players_data = self.load_players_data()

    def load_players_data(self) -> Dict:
        if os.path.exists('players.json'):
            with open('players.json', 'r') as f:
                return json.load(f)
        return {}

    def save_players_data(self):
        with open('players.json', 'w') as f:
            json.dump(self.players_data, f)

    def display_leaderboard(self):
        print("\n" + "="*50)
        print("║" + "LEADERBOARD".center(48) + "║")
        print("="*50)
        for name, stats in self.players_data.items():
            print(f"║ {name:<20} | Wins: {stats['wins']:<5} | Losses: {stats['losses']:<5} ║")
        print("="*50 + "\n")

    def display_board(self, board: List[List[str]], title: str = ""):
        print("\n" + "="*41)
        if title:
            print(f"{title:^41}")
            print("="*41)
        
        print("   ", end="")
        for col in self.column_labels:
            print(f"  {col} ", end="")
        print("\n   +" + "---+"*self.board_size)
        
        for i in range(self.board_size):
            print(f" {i} |", end="")
            for j in range(self.board_size):
                cell = board[i][j]
                if cell == ' ':
                    print("   |", end="")
                elif cell == 'S':
                    print(" ⛴ |", end="")
                elif cell == 'H':
                    print(" 💥 |", end="")
                elif cell == 'M':
                    print(" 💨 |", end="")
            print("\n   +" + "---+"*self.board_size)

    def display_ship_status(self, ships: List[Ship], title: str):
        print("\n" + "="*50)
        print("║" + title.center(48) + "║")
        print("="*50)
        for ship in ships:
            status = "🔥 SUNK" if ship.is_sunk() else "🚢 ACTIVE"
            print(f"║ {ship.name:<15} | Size: {ship.size} | Status: {status:<10} ║")
        print("="*50)

    def is_valid_placement(self, board: List[List[str]], ship: Ship, start_row: int, start_col: int, is_horizontal: bool) -> bool:
        if is_horizontal:
            if start_col + ship.size > self.board_size:
                print("❌ Error: Ship placement exceeds board boundaries!")
                return False
            for i in range(ship.size):
                if board[start_row][start_col + i] != ' ':
                    print("❌ Error: Space already occupied by another ship!")
                    return False
        else:
            if start_row + ship.size > self.board_size:
                print("❌ Error: Ship placement exceeds board boundaries!")
                return False
            for i in range(ship.size):
                if board[start_row + i][start_col] != ' ':
                    print("❌ Error: Space already occupied by another ship!")
                    return False
        return True

    def place_ship(self, board: List[List[str]], ship: Ship, start_row: int, start_col: int, is_horizontal: bool):
        positions = []
        if is_horizontal:
            for i in range(ship.size):
                board[start_row][start_col + i] = 'S'
                positions.append((start_row, start_col + i))
        else:
            for i in range(ship.size):
                board[start_row + i][start_col] = 'S'
                positions.append((start_row + i, start_col))
        ship.positions = positions

    def place_computer_ships(self):
        for ship in self.ships["computer"]:
            while True:
                is_horizontal = random.choice([True, False])
                if is_horizontal:
                    row = random.randint(0, self.board_size - 1)
                    col = random.randint(0, self.board_size - ship.size)
                else:
                    row = random.randint(0, self.board_size - ship.size)
                    col = random.randint(0, self.board_size - 1)
                
                if self.is_valid_placement(self.computer_board, ship, row, col, is_horizontal):
                    self.place_ship(self.computer_board, ship, row, col, is_horizontal)
                    break

    def convert_column_to_index(self, col_letter: str) -> int:
        return self.column_labels.index(col_letter.upper())

    def check_hit(self, row: int, col: int, board: List[List[str]], ships: List[Ship]) -> bool:
        if board[row][col] == 'S':
            board[row][col] = 'H'
            for ship in ships:
                if (row, col) in ship.positions:
                    ship.hits += 1
                    if ship.is_sunk():
                        print(f"🎯 You sunk the {ship.name}!")
            return True
        return False

    def player_turn(self) -> bool:
        while True:
            try:
                print("\n🎯 Your turn to attack!")
                row = int(input("Enter row number to attack (0-9): "))
                col_letter = input("Enter column letter to attack (A-J): ")
                col = self.convert_column_to_index(col_letter)
                
                if 0 <= row < self.board_size and 0 <= col < self.board_size:
                    if self.player_guess_board[row][col] != ' ':
                        print("❌ You already attacked this position!")
                        continue
                    if self.check_hit(row, col, self.computer_board, self.ships["computer"]):
                        print("💥 Direct Hit!")
                        self.player_guess_board[row][col] = 'H'
                        return True
                    else:
                        print("💨 Miss!")
                        self.player_guess_board[row][col] = 'M'
                        return False
                else:
                    print("❌ Invalid coordinates. Please try again.")
            except (ValueError, IndexError):
                print("❌ Please enter valid coordinates (Row: 0-9, Column: A-J).")

    def computer_turn(self) -> bool:
        while True:
            row = random.randint(0, self.board_size - 1)
            col = random.randint(0, self.board_size - 1)
            if self.player_board[row][col] not in ['H', 'M']:
                print(f"\n🤖 Computer attacks position ({row}, {self.column_labels[col]})")
                if self.check_hit(row, col, self.player_board, self.ships["player"]):
                    print("💥 Computer hit your ship!")
                    self.player_board[row][col] = 'H'
                    return True
                else:
                    print("💨 Computer missed!")
                    self.player_board[row][col] = 'M'
                    return False

    def play(self):
        print("\n" + "="*50)
        print("║" + "WELCOME TO BATTLESHIP".center(48) + "║")
        print("="*50)
        
        self.display_leaderboard()
        
        player_name = input("👤 Enter your name: ")
        if player_name not in self.players_data:
            self.players_data[player_name] = {"wins": 0, "losses": 0}
        
        print("\n🚢 Place your ships:")
        for ship in self.ships["player"]:
            while True:
                print(f"\nPlacing {ship.name} (size: {ship.size})")
                self.display_board(self.player_board, "YOUR BOARD")
                try:
                    row = int(input(f"Enter starting row (0-9) for {ship.name}: "))
                    col_letter = input(f"Enter starting column (A-J) for {ship.name}: ")
                    col = self.convert_column_to_index(col_letter)
                    is_horizontal = input("Place horizontally? (y/n): ").lower() == 'y'
                    
                    if self.is_valid_placement(self.player_board, ship, row, col, is_horizontal):
                        self.place_ship(self.player_board, ship, row, col, is_horizontal)
                        break
                except (ValueError, IndexError):
                    print("❌ Please enter valid coordinates (Row: 0-9, Column: A-J).")

        print("\n🤖 Computer is placing ships...")
        self.place_computer_ships()

        while True:
            print("\n" + "="*50)
            self.display_board(self.player_board, "YOUR BOARD")
            self.display_board(self.player_guess_board, "YOUR ATTACKS")
            self.display_ship_status(self.ships["player"], "YOUR SHIPS STATUS")
            self.display_ship_status(self.ships["computer"], "COMPUTER'S SHIPS STATUS")

            if self.player_turn():
                if all(ship.is_sunk() for ship in self.ships["computer"]):
                    print(f"\n🎉 Congratulations {player_name}! You won! 🏆")
                    self.players_data[player_name]["wins"] += 1
                    break
            
            if self.computer_turn():
                if all(ship.is_sunk() for ship in self.ships["player"]):
                    print("\n🤖 Computer wins! Better luck next time! 💔")
                    self.players_data[player_name]["losses"] += 1
                    break

        self.save_players_data()

if __name__ == "__main__":
    game = Battleship()
    game.play()




