
CARDS = {
    1: 'O1', 2: 'O2', 3: 'O3', 4: 'O4', 5: 'O5', 6: 'O6', 7: 'O7', 8: 'OS',
    9: 'OC', 10: 'OK', 11: 'C1', 12: 'C2', 13: 'C3', 14: 'C4', 15: 'C5',
    16: 'C6', 17: 'C7', 18: 'CS', 19: 'CC', 20: 'CK', 21: 'E1', 22: 'E2',
    23: 'E3', 24: 'E4', 25: 'E5', 26: 'E6', 27: 'E7', 28: 'ES', 29: 'EC',
    30: 'EK', 31: 'B1', 32: 'B2', 33: 'B3', 34: 'B4', 35: 'B5', 36: 'B6',
    37: 'B7', 38: 'BS', 39: 'BC', 40: 'BK',
}



class Card(object):
    '''
    Card stores the suit and rank of a single card
    Note:
        The suit variable in a standard card game should be one of [O, C, E, B]
        Similarly the rank variable should be one of
        [1, 2, 3, 4, 5, 6, 7, S, C, K]
    '''
 
    id = None
    number = None
    suit = None
    card = None
    valid_suit = ['O', 'C', 'E', 'B']
    valid_number = ['1', '2', '3', '4', '5', '6', '7', 'S', 'C', 'K']

    def __init__(self, _id):
        ''' Initialize the suit and rank of a card
        Args:
            suit: string, suit of the card, should be one of valid_suit
            rank: string, rank of the card, should be one of valid_rank
        '''
        self.id = _id
        self.card = CARDS[self.id]
        self.suit = self.card[0]
        self.number = self.card[1]

    def get_index(self):
        ''' Get index of a card.
        Returns:
            string: the combination of suit and rank of a card. Eg: 1S, 2H, AD, BJ, RJ...
        '''
        return self.id

    def get_str(self):
        ''' Get the string representation of card

        Return:
            (str): The string of card's suit and number
        '''
        return self.card
    