class Dealer(object):
    ''' Dealer stores a deck of playing cards, remained cards holded by dealer, and can deal cards to players
    Note: deck variable means all the cards in a single game, and should be a list of Card objects.
    '''

    deck = []
    remained_cards = []

    def __init__(self):
        ''' The dealer should have all the cards at the beginning of a game
        '''
        raise NotImplementedError

    def shuffle(self):
        ''' Shuffle the cards holded by dealer(remained_cards)
        '''
        raise NotImplementedError

    def deal_cards(self, **kwargs):
        ''' Deal specific number of cards to a specific player
        Args:
            player_id: the id of the player to be dealt cards
            num: number of cards to be dealt
        '''
        raise NotImplementedError