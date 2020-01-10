import numpy as np

SUIT_MAP = {'O': 0, 'C': 1, 'E': 2, 'B': 3}
NUMBER_MAP = {
    '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, 'S': 7,
    'C': 8, 'K': 9}

ACTION_SPACE = {}
ACTION_LIST = [
    "change_seven", "sing_O", "sing_C", "sing_E", "sing_B"]
for suit in SUIT_MAP.keys():
    for number in NUMBER_MAP.keys():
        ACTION_LIST += ["{}{}".format(suit, number)]
for index, action in enumerate(ACTION_LIST):
    ACTION_SPACE[action] = index


def cards2list(cards):
    ''' Get the corresponding string representation of cards

    Args:
        cards (list): list of CotosCards objects

    Returns:
        (string): string representation of cards
    '''
    cards_list = []
    for card in cards:
        cards_list.append(card.get_str())
    return cards_list

def hand2dict(hand):
    ''' Get the corresponding dict representation of hand

    Args:
        hand (list): list of string of hand's card

    Returns:
        (dict): dict of hand
    '''
    hand_dict = {}
    for card in hand:
        if card not in hand_dict:
            hand_dict[card] = 1
        else:
            hand_dict[card] += 1
    return hand_dict

def encode_hand(plane, hand):
    ''' Encode hand and represerve it into plane

    Args:
        plane (array): 3*4*10 numpy array
        hand (list): list of string of hand's card

    Returns:
        (array): 3*4*10 numpy array
    '''
    plane[0] = np.ones((4, 10), dtype=int)
    for card in hand:
        suit = SUIT_MAP[card[0]]
        number = NUMBER_MAP[card[1]]
        plane[0][suit][number] = 0
    return plane

def encode_target(plane, card):
    ''' Encode target and represerve it into plane

    Args:
        plane (array): 1*4*10 numpy array
        target(str): string of target card

    Returns:
        (array): 1*4*10 numpy array
    '''
    suit = SUIT_MAP[card[0]]
    number = NUMBER_MAP[card[1]]
    plane[suit][number] = 1
    return plane