import os
import json
import numpy as np
from collections import OrderedDict

import rlcard

from rlcard.games.cotos.card import CotosCard as Card

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of abstract action to its index and a list of abstract action
with open(
        os.path.join(
            ROOT_PATH, 'games/cotos/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())

# a map of color to its index
SUIT_MAP = {'o': 0, 'c': 1, 'e': 2, 'b': 3}

# a map of trait to its index
TRAIT_MAP = {
    '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6,
    'sota': 7, 'caballo': 8, 'rey': 9}

# WILD = ['r-wild', 'g-wild', 'b-wild', 'y-wild']
# WILD_DRAW_4 = ['r-wild_draw_4', 'g-wild_draw_4', 'b-wild_draw_4', 'y-wild_draw_4']


def init_deck():
    ''' Generate unocotos deck of 40 cards
    '''
    deck = []
    card_info = Card.info
    for suit in card_info['suit']:

        # init number cards
        for num in card_info['trait']:
            deck.append(Card(suit, num))

    return deck


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
        plane (array): 3*4*15 numpy array
        hand (list): list of string of hand's card

    Returns:
        (array): 3*4*15 numpy array
    '''
    # TODO: ESTO ESTA POR PENSAR!!
    # plane = np.zeros((3, 4, 15), dtype=int)
    plane[0] = np.ones((4, 15), dtype=int)
    hand = hand2dict(hand)
    for card, count in hand.items():
        card_info = card.split('-')
        suit = SUIT_MAP[card_info[0]]
        trait = TRAIT_MAP[card_info[1]]
        if trait >= 13:
            if plane[1][0][trait] == 0:
                for index in range(4):
                    plane[0][index][trait] = 0
                    plane[1][index][trait] = 1
        else:
            plane[0][suit][trait] = 0
            plane[count][suit][trait] = 1
    return plane

def encode_target(plane, target):
    ''' Encode target and represerve it into plane

    Args:
        plane (array): 1*4*15 numpy array
        target(str): string of target card

    Returns:
        (array): 1*4*15 numpy array
    '''
    # TODO: ESTO ESTA POR PENSAR!!
    target_info = target.split('-')
    suit = SUIT_MAP[target_info[0]]
    trait = TRAIT_MAP[target_info[1]]
    plane[suit][trait] = 1
    return plane
