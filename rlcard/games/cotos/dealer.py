import random

from rlcard.games.cotos.utils import init_deck


class CotosDealer(object):
    ''' Initialize a cotos dealer class
    '''
    def __init__(self):
        self.deck = init_deck()
        self.shuffle()

    def shuffle(self):
        ''' Shuffle the deck
        '''
        random.shuffle(self.deck)

    def deal_cards(self, player, num):
        ''' Deal some cards from deck to one player

        Args:
            player (object): The object of CotosPlayer
            num (int): The number of cards to be dealed
        '''
        for _ in range(num):
            player.hand.append(self.deck.pop())

    def flip_top_card(self):
        ''' Flip top card when a new game starts

        Returns:
            (object): The object of CotosCard at the top of the deck
        '''
        return self.deck.pop()
