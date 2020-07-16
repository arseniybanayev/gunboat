from typing import List
import os
import random
import curses

class BasePlayer:
    def select_roles(self, player_index, scores, units, wind) -> List[str]:
        raise NotImplementedError("Must override select_roles() in subclasses of BasePlayer")
    
    def select_targets(self, player_index, scores, units, wind, roles) -> List[str]:
        raise NotImplementedError("Must override select_targets() in subclasses of BasePlayer")

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

def validate_roles(roles):
    if len(roles) != 3: raise ValueError("Must pick exactly 3 roles")
    if len(set(roles)) == 1: raise ValueError("All 3 roles cannot be the same")
    if any([r not in ['K', 'Q', 'J'] for r in roles]):
        raise ValueError("Invalid roles, must be in [K, Q, J]")

def validate_targets(targets):
    if len(targets) != 3: raise ValueError("Must pick exactly 3 targets")
    if len(set(targets)) == 1: raise ValueError("All 3 targets cannot be the same")  # implies "Cannot have more than 2x A"
    if any([t not in ['2', '3', '4', '5', '6', '7', '8', '9', 'A'] for t in targets]):
        raise ValueError("Invalid targets, must be in [2, 3, 4, 5, 6, 7, 8, 9, A]")
    if len(set([t for t in targets if t != 'A'])) != len([t for t in targets if t != 'A']):
        raise ValueError("Targets other than A must be distinct")

class Game:
    def __init__(self, *players):
        if len(players) != 2:
            raise ValueError('Only the two-player game is supported')
        self.players: List[BasePlayer] = list(players)
        
        # Scores, units, stacks and the wind persist between turns
        self.scores: List[int] = [0 for p in self.players]
        self.units: List[List[int]] = [[2, 3, 4] for p in self.players]
        self.stacks: List[List[int]] = [[5, 6, 7, 8, 9, 10] for p in self.players]
        self.wind: int = random.choice(range(len(self.players)))
        
        # Roles and targets do not persist between turns
        self.roles: List[List[str]] = None
        self.targets: List[List[str]] = None
    
    def get_winners(self) -> List[BasePlayer]:
        winners = []
        for i in range(len(self.players)):
            if self.scores[i] >= 15 or any([u >= 10 for u in self.units[i]]):
                winners.append(self.players[i])
        return winners                

    def play(self):
        while not self.get_winners():  # "not list" includes "len(list) <= 0"
            # Start phase
            self.roles = []
            self.targets = []
            
            # Role phase
            for i in range(len(self.players)):
                roles = self.players[i].select_roles(i, self.scores, self.units, self.wind)
                validate_roles(roles)
                self.roles.append(roles)
            
            # Targets phase
            for i in range(len(self.players)):
                targets = self.players[i].select_targets(i, self.scores, self.units, self.wind, self.roles)
                validate_targets(targets)

                self.targets.append(targets)

            # Resolution phase - TODO not generalized to >2 players, so don't just lift the exception in the constructor
            self.__resolve_two_player_turn()

            # End phase
            self.wind = 0 if self.wind >= len(self.players) - 1 else self.wind + 1
            self.roles = None
            self.targets = None
    
    def __resolve_two_player_turn(self):
        effective_units = [list(us) for us in self.units]

        # Build a dictionary of targets, from source to destination
        targets = {}  # key is (from_player_index, from_unit_index), value is (to_player_index, to_unit_index)
        for player_index, player_targets in enumerate(self.targets):
            for player_unit_index, target in enumerate(player_targets):
                role = self.roles[player_index][player_unit_index]
                if target == 'A':  # a hold doesn't have a target, but first doubles effective units unconditionally
                    effective_units[player_index][player_unit_index] *= 2
                elif role == 'K':  # attacks (K) target the opponent's units
                    try:
                        index_of_targeted_unit = self.units[1 - player_index].index(int(target))
                    except ValueError:  # the attack targeted thin air
                        continue
                    targets[(player_index, player_unit_index)] = (1 - player_index, index_of_targeted_unit)
                elif role in ['Q', 'J']:  # upgrades (Q) and supports (J) target our units
                    try:
                        index_of_targeted_unit = self.units[player_index].index(int(target))
                    except ValueError:  # the support targeted thin air
                        continue
                    targets[(player_index, player_unit_index)] = (player_index, index_of_targeted_unit)
                else:
                    raise RuntimeError(f"Unexpected role: {role}")
        
        successful_upgrades = []
        points_earned = [0 for _ in range(len(self.players))]

        def apply(src):
            dest = targets[src]
            src_role = self.roles[src[0]][src[1]]
            if src_role == 'J':
                effective_units[dest[0]][dest[1]] += self.units[src[0]][src[1]]
            elif src_role == 'Q':
                successful_upgrades.append(dest)
            elif src_role == 'K':
                other_srcs_for_dest = [t for t in targets if targets[t] == dest and t != src]
                for other_src in other_srcs_for_dest:
                    apply(other_src)
                # resolve combat using effective units up to now
                delta = effective_units[src[0]][src[1]] - effective_units[dest[0]][dest[1]]
                if delta > 0:  # successful attack
                    if dest in targets:  # invalidate the move being done at the destination
                        targets.pop(dest)
                    points_earned[src[0]] += delta
                elif delta < 0:  # unsuccessful attack
                    points_earned[dest[0]] -= delta
            else:
                raise ValueError(f'Unexpected role: {src_role}')
            
            targets.pop(src)  # done applying this target

        while len(targets) > 0:
            leaves = [t for t in targets if t not in targets.values() or t == targets[t]]
            if len(leaves) == 0:
                raise CycleDetected()
            leaf = leaves[0]
            apply(leaf)
        
        for upgrade in successful_upgrades:
            next_unit = self.stacks[upgrade[0]].pop(0)
            self.units[upgrade[0]][upgrade[1]] = next_unit
        
        for i in range(len(self.players)):
            self.scores[i] += points_earned[i]

if __name__ == '__main__':
    players = [CliPlayer(), CliPlayer()]
    game = Game(*players)
    game.play()