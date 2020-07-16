from play import BasePlayer, Game
from typing import List

class TestPlayer(BasePlayer):
    def __init__(self, roles, targets):
        self.roles = roles
        self.targets = targets
    
    def select_roles(self, player_index, scores, units, wind) -> List[str]:
        return self.roles.pop(0)
    
    def select_targets(self, player_index, scores, units, wind, roles) -> List[str]:
        return self.targets.pop(0)


def test_basic_game():
    players = [TestPlayer(
        roles=[
            ['K', 'K', 'Q']
        ], targets=[
            ['2', 'A', 'A']
        ]
    ), TestPlayer(
        roles=[
            ['J', 'J', 'Q']
        ], targets=[
            ['2', '3', '4']
        ]
    )]
    game = Game(*players)
    game.play()