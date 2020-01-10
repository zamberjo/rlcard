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