import time

from rlcard.games.cotos.player import CotosPlayer as Player
from rlcard.games.cotos.utils import ACTION_LIST
from rlcard.games.cotos.utils import cards2list

class CotosGame(object):
    ''' Cotos game class. This class will interact with outer environment.
    '''
    trump = None
    dealer = None
    payoffs = []
    players = []
    table = []
    lastcards_mode = False
    last_turn_winner = None
    winner_team = None
    sing_suits = []
    over = False

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.num_players = 4
        # 2 payoffs, 1 by team
        self.payoffs = [0 for _ in range(self.num_players)]

    def init_game(self):
        ''' Initialize players in the game and start round 1
        '''
        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize four players to play the game
        for playerIndex in range(self.num_players):
            player = Player(self, playerIndex, "Player {}".format(playerIndex))
            player.enter_game()
            self.players += [player]

        player_turn = self.get_next_player_turn()
        state = self.get_state(player_turn)
        return state, player_turn.index

    def get_next_player_turn(self):
        while True:
            players_turn = list(filter(lambda p: p.is_turn, self.players))
            if players_turn:
                players_turn = players_turn[0]
                break
            for player in self.players:
                player.get_next_turn_player()
            time.sleep(1)
        return players_turn

    def set_trump(self, card):
        ''' Establecemos el triunfo de la partida.
        '''
        self.trump = card

    def add_sing_suits(self, suit):
        ''' Guardamos el palo para no volver a cantar en este.
        '''
        self.sing_suits += [suit]

    def play_card(self, player, card):
        ''' El jugador juega una carta.
        '''
        self.table[player.index] = card

    def set_end_turn(self, team):
        ''' Finaliza el turno, establecemos el equipo ganador.
        '''
        self.last_turn_winner = team
        for index, player in enumerate(self.players):
            self.payoffs[index] = player.payoff
            player.reset_payoff()
        # TODO: Reseteamos la mesa ya?
        self.table = [None, None, None, None]

    def set_lastcards_mode(self, mode):
        ''' Establece el modo últimas cartas.
        '''
        self.lastcards_mode = mode

    def reset(self):
        self.sing_suits = []
    
    def end_game(self, team):
        ''' Establecemos el fin del juego.
        '''
        pass

    def check_last_turn_winned(self, team):
        return self.last_turn_winner == team

    def get_state(self, player):
        ''' Devolvemos el estado de un jugador.
        '''
        state = {}
        state['hand'] = cards2list(player.hand)
        state['trump'] = self.trump.get_str()
        state['table'] = cards2list(self.table)
        state['legal_actions'] = player.get_legal_actions(self.table)
        return state

    def get_legal_actions(self):
        player = list(filter(lambda p: p.is_turn, self.players))
        if not player:
            return []
        return player[0].get_legal_actions(self.table)

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        return self.payoffs

    def get_player_num(self):
        ''' Retrun the number of players in the game
        '''
        return self.num_players

    def get_action_num(self):
        ''' Return the number of possible actions in the game
        '''
        return len(ACTION_LIST)

    def step(self, action):
        ''' Perform one draw of the game and return next player number, and the
        state for next player
        '''
        player = self.get_next_player_turn()
        print("Player {}: action -> {}".format(player.index, action))
        if "sing_" in action:
            suit = action[-1]
            player.sing(suit)
            return None
        if action == "change_seven":
            player.change_seven()
            return None
        player.play_card(action)
        

    def step_back(self):
        ''' Takes one step backward and restore to the last state
        '''
        raise NotImplementedError

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        raise NotImplementedError

    def is_over(self):
        ''' Return whether the current game is over

        TODO: No dependar de la llamada, sino comprobar los score de los team
        '''
        return self.over