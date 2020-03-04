
# import asyncio
import time

from rlcard.games.cotos.card import CARDS
from rlcard.games.cotos.card import CotosCard as Card
from rlcard.games.cotos.utils import cards2list

try:
    import socketio
except ImportError:
    print("pip install python-socketio==4.4.0")

SERVER = "http://localhost:9000"


class CotosPlayer(object):
    ''' Player stores cards in the player's hand, and can determine the
    actions can be made according to the rules
    '''
    id = None
    name = None
    index = None
    team = None
    sio = None
    hand = []
    is_turn = False
    payoff = None
    server_game_id = None

    def __init__(self, game, _id, name, server_game_id):
        ''' Every player should have a unique player id
        '''
        self.game = game
        self.name = name
        self.id = _id
        self.payoff = 0
        self.sio = socketio.Client()
        self.define_events()
        self.connect()
        self.server_game_id = server_game_id

    def connect(self, options={}):
        self.sio.connect(SERVER, options)

    def emit(self, event, params=None):
        if not self.sio.sid:
            self.connect({'force new connection': true})
        if not params:
            params = {}
        return self.sio.emit(event, params)

    def enter_game(self):
        return self.emit('playerJoinGame', {
            'login': self.name,
            'gameId': self.server_game_id,
        })

    def set_hand(self, cards_data):
        if not cards_data or not any(cards_data):
            return
        self.hand = []
        for card_data in cards_data:
            self.hand += [Card(card_data.get("id"))]

    def add_payoff(self, score):
        self.payoff += (score * 100) / 54

    def reset_payoff(self):
        self.payoff = 0

    def check_sing_suit(self, suit):
        if self.game.check_last_turn_winned(self.team):
            cards = list(filter(
                lambda c: (
                    c.number in ('K', 'S') and
                    c.suit == suit and
                    suit not in self.game.sing_suits
                ), self.hand))
        return bool(len(cards) == 2)

    def check_sing(self):
        suits_can_sing = []
        if self.game.check_last_turn_winned(self.team):
            hand_suits = list(
                set(map(lambda c: c.suit, self.hand)))
            suits_can_sing = list(
                filter(self.check_sing_suit, hand_suits))
        return suits_can_sing

    def getPlayerIndexWinner(self):
        start_turn_player_index = (self.index + 1) % 4
        card_played = self.game.table[start_turn_player_index]
        value_card_played = card_played.get_card_turn_value(
            card_played.suit, self.game.trump.suit)
        winner_player_index = start_turn_player_index
        for _ in range(2):
            start_turn_player_index = (start_turn_player_index + 1) % 4
            next_card_played = self.game.table[start_turn_player_index]
            value_next_card_played = next_card_played.get_card_turn_value(
                card_played.suit, self.game.trump.suit)
            if value_card_played < value_next_card_played:
                winner_player_index = start_turn_player_index
        return winner_player_index

    def check_trusted(self):
        trusted = False
        n_cards_played = len([c for c in self.game.table if c])
        if n_cards_played == 3:
            playerIndexTurnWinner = self.getPlayerIndexWinner()
            trusted = (
                (self.index in (0, 2) and playerIndexTurnWinner in (0, 2)) or
                (self.index in (1, 3) and playerIndexTurnWinner in (1, 3))
            )
        return trusted

    def get_legal_actions(self, table):
        suits_sing = self.check_sing()
        change_seven = self.check_change()

        if not self.game.lastcards_mode:
            return suits_sing, change_seven, cards2list(self.hand)

        for index in range(1, 4):
            player_index = (self.index + index) % 4
            card = self.game.table[player_index]
            if not card:
                continue
            first_card = card
            break
        else:
            return suits_sing, change_seven, cards2list(self.hand)

        availables_cards = []
        cards_same_suit = list(filter(
            lambda c: c.suit == first_card.suit, self.hand))

        if cards_same_suit:
            for card in cards_same_suit:
                card_value = card.get_card_turn_value(
                    first_card.suit, self.game.trump.suit)
                for card_played in self.game.table:
                    if not card_played:
                        continue
                    card_played_value = card_played.get_card_turn_value(
                        first_card.suit, self.game.trump.suit)
                    if card_value < card_played_value:
                        break
                else:
                    availables_cards += [card]
            if not availables_cards:
                availables_cards = cards_same_suit

        else:
            cards_trump = list(filter(
                lambda c: c.suit == self.game.trump.suit, self.hand))

            if not cards_trump:
                return suits_sing, change_seven, cards2list(self.hand)

            if self.check_trusted():
                return suits_sing, change_seven, cards2list(self.hand)

            for card in cards_trump:
                card_value = card.get_card_turn_value(
                    first_card.suit, self.game.trump.suit)
                for card_played in self.game.table:
                    if not card_played:
                        continue
                    card_played_value = card_played.get_card_turn_value(
                        first_card.suit, self.game.trump.suit)
                    if card_value < card_played_value:
                        break
                else:
                    availables_cards += [card]

            if not availables_cards:
                availables_cards = cards_trump

        return suits_sing, change_seven, cards2list(list(availables_cards))

    def check_change(self):
        check_seven = False
        if self.game.check_last_turn_winned(self.team):
            check_seven = bool(len(list(filter(
                lambda c: (
                    c.suit == self.game.trump.suit and
                    c.number == "7" and
                    c.get_card_turn_value(
                        c.suit, self.game.trump.suit
                    ) < self.game.trump.get_card_turn_value(
                        self.game.trump.suit, self.game.trump.suit)),
                self.hand))) > 0)
        return check_seven

    def get_next_turn_player(self):
        self.emit("gameGetNextTurn", {})

    def sing(self, suit):
        ''' TODO: await '''
        self.emit("playerSing", {"suit": suit})
        self.is_turn = False

    def change_seven(self):
        ''' TODO: await '''
        self.emit("playerChangeSeven", {})
        self.is_turn = False

    def play_card(self, card_name):
        card_index = list(
            filter(lambda k: CARDS.get(k) == card_name, CARDS))
        if not card_index:
            raise NotImplementedError
        card = Card(card_index[0])
        self.emit("playerPlayCard", {
            "card": card.serializer(),
            "gameId": self.server_game_id,
        })
        self.is_turn = False

    def define_events(self):
        sio = self.sio

        @sio.on('playerAccepted')
        def player_accepted(data):
            player_data = data.get("playerData", {})
            self.id = player_data.get("id")
            self.name = player_data.get("name")
            self.index = player_data.get("index")
            # TODO: Crear TEAM
            self.team = player_data.get("team", {}).get("id")
            self.set_hand(player_data.get("hand"))

        @sio.on('gameCanStart')
        def start_game(data):
            sio.emit("playerGetHand", {})
            sio.emit("gameGetNextTurn", {})
            sio.emit("gameGetTrump", {})
            self.game.started = True

        @sio.on('playerSetHand')
        def set_hand(data):
            if data.get("hand"):
                self.set_hand(data.get("hand"))
            else:
                sio.emit("playerGetHand", {})

        @sio.on('gameSetNextTurn')
        def set_next_turn_player(data):
            self.is_turn = bool(
                data.get("nextTurnPlayer", {}).get("id", False) == self.id)

        @sio.on('gameSetTrump')
        def set_trump(data):
            card_trump = Card(data.get("trump", {}).get("id"))
            self.game.set_trump(card_trump)

        @sio.on('playerChangedSeven')
        def trumpChanged(data):
            if data.get("error"):
                return
            if self.id == data.get("playerId"):
                sio.emit("playerGetHand", {})
                self.is_turn = False
            if data.get("newTrump"):
                card_trump = Card(data.get("newTrump", {}).get("id"))
                self.game.set_trump(card_trump)

        @sio.on('playerSinged')
        def singed(data):
            if data.get("suit"):
                self.game.add_sing_suits(data.get("suit"))
            if data.get("playerId") == self.id:
                score = data.get("scoreAdded")
                self.add_payoff(score)

        @sio.on('playerPlayedCard')
        def played_card(data):
            player_index = data.get("playerId")
            if data.get("error"):
                self.is_turn = True
                return

            card = Card(data.get("card", {}).get("id"))
            if self.id == player_index:
                self.hand = [c for c in self.hand if c.id != card.id]
                self.game.play_card(self, card)

            if data.get("endTurn"):
                mult = 1
                if data.get("turnTeamWinner") != self.team:
                    mult = -1
                self.add_payoff(data.get("tableScore") * mult)
                self.game.set_end_turn(data.get("turnTeamWinner"))
                sio.emit("playerGetHand", {})

            if data.get("endGame"):
                sio.emit('gameCheckWinners', {})

            elif data.get("lastCardsMode"):
                self.game.set_lastcards_mode(True)

        @sio.on('gameEndGame')
        def end_game(data):
            if data.get("deVueltaMode"):
                self.game.reset()
                self.is_turn = False
                sio.emit("gameGetTrump", {})
                sio.emit("playerGetHand", {})
                sio.emit("gameGetNextTurn", {})
            else:
                self.winner_team = "team1"
                self.team1_score = data.get("team1")
                self.team2_score = data.get("team2")
                if data.get("team1") < data.get("team2"):
                    self.winner_team = "team2"
                print("Finaliza la partida!")
                self.game.end_game(self.winner_team)

    def available_order(self):
        ''' Get the actions can be made based on the rules
        Returns:
            list: a list of available orders
        '''
        raise NotImplementedError

    def play(self):
        ''' Player's actual action in the round
        '''
        raise NotImplementedError
