import numpy as np

from rlcard import models
from rlcard.envs.env import Env
from rlcard.games.cotos.card import CotosCard
from rlcard.games.cotos.game import CotosGame as Game
from rlcard.games.cotos.utils import ACTION_LIST, ACTION_SPACE
from rlcard.games.cotos.utils import encode_hand, encode_target


class CotosEnv(Env):

    def __init__(self, allow_step_back=False):
        # TODO: Esto hay que ver que es ya que es de tensorflow.
        super().__init__(Game(allow_step_back), allow_step_back)
        self.state_shape = [7, 4, 10]

    def print_state(self, player):
        ''' Print out the state of a given player

        Args:
            player (int): Player object
        '''
        state = self.game.get_state(player)
        print('\n=============== Your Hand ===============')
        CotosCard.print_cards(state['hand'])
        print('')
        print('=============== table ===============')
        CotosCard.print_cards(state['table'], wild_color=True)
        print('')
        print('========== Agents Card Number ===========')
        for i in range(self.player_num):
            if i != self.active_player:
                print('Agent {} has {} cards.'.format(
                    i, len(self.game.players[i].hand)))
        print('======== Actions You Can Choose =========')
        for i, action in enumerate(state['legal_actions']):
            if i == 0:
                print("Suits can sing: {}".format(action))
            elif i == 1:
                print("Can change seven: {}".format(action))
            elif i == 2:
                CotosCard.print_cards(action, wild_color=True)
            if i < len(state['legal_actions']) - 1:
                print(', ', end='')
        print('\n')

    def print_result(self, player):
        ''' Print the game result when the game is over

        Args:
            player (int): The human player id
        '''
        payoffs = self.get_payoffs()
        print('===============     Result     ===============')
        if payoffs[player] > 0:
            print('You win!')
        else:
            print('You lose!')
        print('')

    @staticmethod
    def print_action(action):
        ''' Print out an action in a nice form

        Args:
            action (str): A string a action
        '''
        CotosCard.print_cards(action, wild_color=True)

    def load_model(self):
        ''' Load pretrained/rule model

        Returns:
            model (Model): A Model object
        '''
        return models.load('cotos-rule-v1')

    def extract_state(self, state):
        obs = np.zeros((7, 4, 10), dtype=int)
        encode_hand(obs[:3], state['hand'])
        encode_target(obs[3], state['trump'])
        encode_hand(obs[4:], state['table'])
        legal_action_id = self.get_legal_actions(
            state['legal_actions'])
        extrated_state = {'obs': obs, 'legal_actions': legal_action_id}
        return extrated_state

    def get_payoffs(self):
        return self.game.get_payoffs()

    def decode_action(self, action_id):
        if action_id:
            return ACTION_LIST[action_id]
        legal_ids = self.get_legal_actions()
        return ACTION_LIST[np.random.choice(legal_ids)]

    def get_legal_actions(self, legal_actions=None):
        legal_ids = []
        if not legal_actions:
            legal_actions = self.game.get_legal_actions()
        if not legal_actions:
            return legal_ids
        for suit_can_sing in legal_actions[0]:
            legal_id = ACTION_SPACE["sing_{}".format(suit_can_sing)]
            legal_ids += [legal_id]
        if legal_actions[1]:
            legal_id = ACTION_SPACE["change_seven"]
            legal_ids += [legal_id]
        for card_legal_action in legal_actions[2]:
            legal_id = ACTION_SPACE[card_legal_action]
            legal_ids += [legal_id]
        return legal_ids
