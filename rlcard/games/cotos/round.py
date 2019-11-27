import numpy as np

from rlcard.games.cotos.card import CotosCard as Card
from rlcard.games.cotos.utils import cards2list


class CotosRound(object):

    def __init__(self, dealer, num_players):
        ''' Initialize the round class

        Args:
            dealer (object): the object of CotosDealer
            num_players (int): the number of players in game
        '''
        self.second_round_flag = False
        self.last_cards_flag = False
        self.dealer = dealer
        self.trump = None
        self.current_player = 0
        self.direction = 1
        self.num_players = num_players
        self.played_cards = []
        self.is_over = False
        self.winner = None
        self.second_round_flag = False
        self.last_cards_flag = False

    def flip_top_card(self):
        ''' Flip the top card of the card pile

        Returns:
            (object of CotosCard): the top card in game

        '''
        top = self.dealer.flip_top_card()
        self.trump = top
        return top

    def proceed_round(self, players, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of UnoPlayer
            action (str): string of legal action
        '''
        player = players[self.current_player]
        card_info = action.split('-')
        suit = card_info[0]
        trait = card_info[1]
        # remove correspongding card
        remove_index = None

        for index, card in enumerate(player.hand):
            if suit == card.suit and trait == card.trait:
                remove_index = index
                break

        end_round = False
        if len(self.played_cards) == self.num_players:
            end_round = True

        card = player.hand.pop(remove_index)
        if not player.hand and end_round:
            import pdb; pdb.set_trace()
            self.is_over = True

        self.played_cards.append(card)

        # perform the number action
        self.current_player = (
            self.current_player + self.direction) % self.num_players
        return end_round

    def get_score(self):
        player_win = self.current_player
        card_start = self.played_cards[self.current_player]
        score = card_start.points
        card_win = card_start

        second_player = (self.current_player + 1) % self.num_players
        second_player_card = self.played_cards[second_player]
        score += second_player_card.points
        if self.check_card_win(card_win, second_player_card) == 1:
            player_win = second_player
            card_win = second_player_card

        third_player = (self.current_player + 2) % self.num_players
        third_player_card = self.played_cards[third_player]
        score += third_player_card.points
        if self.check_card_win(card_win, third_player_card) == 1:
            player_win = third_player
            card_win = third_player_card

        fourth_player = (self.current_player + 3) % self.num_players
        fourth_player_card = self.played_cards[fourth_player]
        score += fourth_player_card.points
        if self.check_card_win(card_win, fourth_player_card) == 1:
            player_win = fourth_player
            card_win = fourth_player_card

        return player_win, score

    def check_card_win(self, card1, card2):
        card1_trump_flag = False
        card2_trump_flag = False
        if card1.suit == self.trump.suit:
            card1_trump_flag = True
        if card2.suit == self.trump.suit:
            card2_trump_flag = True
        if card1_trump_flag and not card2_trump_flag:
            return 0
        elif not card1_trump_flag and card2_trump_flag:
            return 1
        elif card1.points > card2.points:
            return 0
        elif card1.points < card2.points:
            return 1
        elif card1.position > card2.position:
            return 0
        elif card1.position < card2.position:
            return 1
        raise NotImplementedError()

    def get_legal_actions(self, players, player_id):
        hand = players[player_id].hand
        legal_actions = []
        if self.last_cards_flag and self.played_cards:
            first_card = self.played_cards[0]
            force_suit = first_card.suit
            cards_have_suit = filter(
                lambda c: c.suit == force_suit)
            cards_have_trump_suit = filter(
                lambda c: c.suit == self.trump.suit)
            if cards_have_suit:
                legal_actions = map(lambda c: c.get_str(), cards_have_suit)
                # TODO: Debe ganar a toda la mesa
            elif cards_have_trump_suit:
                legal_actions = map(lambda c: c.get_str(), cards_have_suit)
                # TODO: Debe ganar a toda la mesa
            else:
                legal_actions = map(lambda c: c.get_str(), hand)
        else:
            legal_actions = map(lambda c: c.get_str(), hand)

        legal_actions = list(legal_actions)
        return legal_actions

    def get_state(self, players, player_id):
        ''' Get player's state

        Args:
            players (list): The list of UnoPlayer
            player_id (int): The id of the player
        '''
        state = {}
        player = players[player_id]
        state['hand'] = cards2list(player.hand)
        state['played_cards'] = cards2list(self.played_cards)
        others_hand = []
        for player in players:
            if player.player_id != player_id:
                others_hand.extend(player.hand)
        state['others_hand'] = cards2list(others_hand)
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        return state