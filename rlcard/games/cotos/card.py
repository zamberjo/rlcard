from termcolor import colored

class CotosCard(object):

    info = {
        'suit': ['o', 'c', 'e', 'b'],
        'trait': [
            '1', '2', '3', '4', '5', '6', '7', 'sota', 'caballo', 'rey'
        ],
    }

    def __init__(self, suit, trait):
        ''' Initialize the class of CotosCard

        Args:
            suit (str): The suit of card
            trait (str): The trait of card
        '''
        self.suit = suit
        self.trait = trait
        self.str = self.get_str()

    def get_str(self):
        ''' Get the string representation of card

        Return:
            (str): The string of card's color and trait
        '''
        return self.suit + '-' + self.trait


    @staticmethod
    def print_cards(cards):
        ''' Print out card in a nice form

        Args:
            card (str or list): The string form or a list of a Cotos card
        '''
        if isinstance(cards, str):
            cards = [cards]
        for i, card in enumerate(cards):
            suit, trait = card.split('-')
            if trait == 'sota':
                trait = 'Sota'
            elif trait == 'caballo':
                trait = 'Caballo'
            elif trait == 'rey':
                trait = 'Rey'

            if suit == 'o':
                print(colored(trait, 'yellow'), end='')
            elif suit == 'c':
                print(colored(trait, 'red'), end='')
            elif suit == 'e':
                print(colored(trait, 'blue'), end='')
            elif suit == 'b':
                print(colored(trait, 'red'), end='')

            if i < len(cards) - 1:
                print(', ', end='')
