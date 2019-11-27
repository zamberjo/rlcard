# from copy import deepcopy

from rlcard.games.cotos.dealer import CotosDealer as Dealer
from rlcard.games.cotos.player import CotosPlayer as Player
from rlcard.games.cotos.round import CotosRound as Round


class CotosGame(object):

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.num_players = 4
        self.trump = None
        self.payoffs = [0 for _ in range(self.num_players)]
        self.second_round_flag = False
        self.last_cards_flag = False
        self.team_scores = [0, 0]

    def init_game(self):
        ''' Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        '''
        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize a dealer that can deal cards
        self.dealer = Dealer()

        # Initialize four players to play the game
        self.players = [Player(i) for i in range(self.num_players)]

        # Deal 6 cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player, 6)

        # Initialize a Round
        self.round = Round(self.dealer, self.num_players)

        # flip and perfrom top card
        self.trump = self.round.flip_top_card()

        # Save the hisory for stepping back to the last state.
        self.history = []

        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): A specific action

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        '''
        end_round = self.round.proceed_round(self.players, action)
        if end_round:
            self.update_score()
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def update_score(self):
        player_win, score = self.round.get_score()
        self.next_round_player = player_win
        team_player = player_win % 2
        self.team_scores[team_player] += score

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        return False

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        state = self.round.get_state(self.players, player_id)
        return state

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        winner = self.round.winner
        if winner is not None and len(winner) == 1:
            self.payoffs[winner[0]] = 1
            self.payoffs[1 - winner[0]] = -1
        return self.payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions(
            self.players, self.round.current_player)

    def get_player_num(self):
        ''' Return the number of players in Cotos

        Returns:
            (int): The number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_action_num():
        ''' Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 6 possible actions
        '''
        return 6

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            (int): current player's id
        '''
        return self.round.current_player

    def is_over(self):
        ''' Check if the game is over

        Returns:
            (boolean): True if the game is over
        '''
        return self.round.is_over


# For test
if __name__ == '__main__':
    import numpy as np
    # import time
    # random.seed(0)
    # start = time.time()
    game = CotosGame()
    for _ in range(1):
        state, button = game.init_game()
        print(button, state)
        i = 0
        while not game.is_over():
            i += 1
            legal_actions = game.get_legal_actions()
            print('legal_actions', legal_actions)
            action = np.random.choice(legal_actions)
            print('action', action)
            print()
            state, button = game.step(action)
            print(button, state)
        print(game.get_payoffs())
    print('step', i)
