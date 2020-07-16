from typing import List
import os
from game import BasePlayer, Game, validate_roles, validate_targets

def clear_terminal():
    # https://stackoverflow.com/a/2084628
    os.system('cls' if os.name == 'nt' else 'clear')

class CliPlayer(BasePlayer):
    def select_roles(self, player_index, scores, units, wind) -> List[str]:
        clear_terminal()
        print(f"========== Player {player_index}'s turn ==========")
        print(f"> Your score: {scores[player_index]}, Opponent's score: {scores[1 - player_index]}")
        if wind == player_index:
            print(f"> You have the wind")
        else:
            print(f"> Your opponent has the wind")
        print()

        print(' | '.join([f' {i} ' for i in units[1 - player_index]]))
        print('-----'.join(['-' for _ in range(len(units[0]))]))
        print(' | '.join([f' {i} ' for i in units[player_index]]))
        
        while True:
            roles = list(input(f'Player {player_index}, select your roles (e.g., "KKJ"): '))
            try:
                validate_roles(roles)
                return roles
            except ValueError as e:
                print(f'Invalid roles: {e}')
    
    def select_targets(self, player_index, scores, units, wind, roles) -> List[str]:
        clear_terminal()
        print(f"========== Player {player_index}'s turn ==========")
        print(f"> Your score: {scores[player_index]}, Opponent's score: {scores[1 - player_index]}")
        if wind == player_index:
            print(f"> You have the wind")
        else:
            print(f"> Your opponent has the wind")
        print()

        print(' | '.join([f' {i} ' for i in units[1 - player_index]]))
        print(' | '.join([f'({r})' for r in roles[1 - player_index]]))
        print('-----'.join(['-' for _ in range(len(units[0]))]))
        print(' | '.join([f'({r})' for r in roles[player_index]]))
        print(' | '.join([f' {i} ' for i in units[player_index]]))

        while True:
            targets = list(input(f'Player {player_index}, select your targets (e.g., "2AA"): '))
            try:
                validate_targets(targets)
                return targets
            except ValueError as e:
                print(f'Invalid targets: {e}')

if __name__ == '__main__':
    players = [CliPlayer(), CliPlayer()]
    game = Game(*players)
    game.play()