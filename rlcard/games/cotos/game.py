import time

from rlcard.games.cotos.player import CotosPlayer as Player
from rlcard.games.cotos.utils import ACTION_LIST
from rlcard.games.cotos.utils import cards2list


class CotosGame(object):
    ''' Cotos game class. This class will interact with outer environment.
    '''
    trump = None
    payoffs = []
    lastcards_mode = False
    last_turn_winner = None
    winner_team = None
    sing_suits = []
    players = []
    over = False
    started = False
    deVueltaMode = False

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.num_players = 4
        self.payoffs = [0 for _ in range(self.num_players)]
        self.table = [None for _ in range(self.num_players)]
        self.turn_number = 0

    def init_game(self):
        ''' Initialize players in the game and start round 1
        '''
        self.trump = None
        self.lastcards_mode = False
        self.last_turn_winner = None
        self.winner_team = None
        self.sing_suits = []
        self.over = False
        self.started = False
        self.payoffs = [0 for _ in range(self.num_players)]
        self.table = [None for _ in range(self.num_players)]
        self.turn_number = 0

        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize four players to play the game
        for playerIndex in range(self.num_players):
            player = Player(
                self, playerIndex, "Player {}".format(playerIndex),
                self.server_game_id)
            player.enter_game()
            self.players += [player]

        # Wait unitl game not started
        while True:
            print("Waiting game is started...")
            if self.started:
                break
            time.sleep(1)

        player_turn = self.get_next_player_turn()
        state = self.get_state(player_turn)
        return state, player_turn.index

    def get_next_player_turn(self):
        while True:
            print("getting next turn player...")
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
            self.payoffs[index] += player.payoff
            # player.reset_payoff()
        # TODO: Reseteamos la mesa ya?
        # self.payoffs = [0 for _ in range(self.num_players)]
        self.table = [None for _ in range(self.num_players)]
        self.turn_number += 1

    def set_lastcards_mode(self, mode):
        ''' Establece el modo últimas cartas.
        '''
        if self.lastcards_mode != mode:
            print("[set_lastcards_mode] {}".format(mode))
        self.lastcards_mode = mode

    def reset(self):
        if not self.deVueltaMode:
            print("# " * 50)
            print("De vuelta!")
            print("# " * 50)
            self.deVueltaMode = True
            self.sing_suits = []
            self.set_lastcards_mode(False)
            self.trump = None
            self.winner_team = None
            self.over = False

    def end_game(self, team):
        ''' Establecemos el fin del juego.
        '''
        self.over = True

    def check_last_turn_winned(self, team):
        return self.last_turn_winner == team

    def get_state(self, player):
        ''' Devolvemos el estado de un jugador.
        '''
        if isinstance(player, int):
            player = self.players[player]
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
        print("PAYOFFS = {}".format(self.payoffs))
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
        turn_number = self.turn_number
        player = self.get_next_player_turn()
        print("Player {}: action -> {}".format(player.index, action))
        if "sing_" in action:
            suit = action[-1]
            player.sing(suit)
            player_turn = player
            state = self.get_state(player_turn)
            res = state, player_turn.index
        elif action == "change_seven":
            player.change_seven()
            player_turn = player
            state = self.get_state(player_turn)
            import pdb; pdb.set_trace()
            res = state, player_turn.index
        else:
            player.play_card(action)

            # TODO: async
            while turn_number >= self.turn_number and \
                    not self.table[player.index]:
                print("Waiting turn...")
                time.sleep(1)

            player_turn = self.get_next_player_turn()
            state = self.get_state(player_turn)
            res = state, player_turn.index
        return res

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        player = self.get_next_player_turn()
        raise player.index

    def is_over(self):
        ''' Return whether the current game is over

        TODO: No dependar de la llamada, sino comprobar los score de los team
        '''
        if self.over:
            for player in self.players:
                player.sio.disconnect()
        return self.over
