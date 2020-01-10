class Judger(object):
    ''' Judger decides whether the round/game ends and return the winner of the round/game
    '''

    def judge_round(self, **kwargs):
        ''' Decide whether the round ends, and return the winner of the round
        Returns:
            int: return the player's id who wins the round or -1 meaning the round has not ended
        '''
        raise NotImplementedError

    def judge_game(self, **kwargs):
        ''' Decide whether the game ends, and return the winner of the game
        Returns:
            int: return the player's id who wins the game or -1 meaning the game has not ended
        '''
        raise NotImplementedError