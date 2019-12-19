# https://python-socketio.readthedocs.io/en/latest/client.html
import socketio
import asyncio
import time
import sys
from random import randrange

# SERVER = "https://cotosgame.es"
SERVER = "http://localhost:8080"

class Player():
    id = None
    name = None
    index = None
    team = None
    hand = None
    is_turn = False
    lastcards_mode = False
    trump = {}
    deck = []
    winner_team = False
    team1_score = 0
    team2_score = 0

    def __init__(self, name, debug=False):
        self.name = name
        self.debug = debug
        self.table = [None, None, None, None]
        self.deck = []
        self.sio = socketio.Client()
        self.define_events()

    def connect(self):
        self.sio.connect(SERVER)

    def emit(self, event, params=None):
        if not self.sio.sid:
            self.connect()
        if not params:
            params = {}
        return self.sio.emit(event, params)

    def enter_game(self):
        return self.emit('newPlayer', {'playerName': self.name})

    def serialize(self):
        return {
            # "id": self.id, 
            "hand": [self.print_card(c) for c in self.hand],
            "is_turn": self.is_turn,
        }

    def getPlayerIndexWinner(self):
        start_turn_player_index = (self.index + 1) % 4
        card_played = self.table[start_turn_player_index]
        value_card_played = self.get_card_turn_value(
            card_played, card_played.get("suit"))
        winner_player_index = start_turn_player_index
        for _ in range(2):
            start_turn_player_index = (start_turn_player_index + 1) % 4
            next_card_played = self.table[start_turn_player_index]
            value_next_card_played = self.get_card_turn_value(
                next_card_played, card_played.get("suit"))
            if value_card_played < value_next_card_played:
                winner_player_index = start_turn_player_index
        return winner_player_index

    def check_trusted(self):
        trusted = False
        n_cards_played = len([c for c in self.table if c])
        if n_cards_played == 3:
            playerIndexTurnWinner = self.getPlayerIndexWinner()
            trusted = (
                (self.index in (0, 2) and playerIndexTurnWinner in (0, 2)) or
                (self.index in (1, 3) and playerIndexTurnWinner in (1, 3))
            )
        return trusted

    def check_last_turn_winned(self):
        # TODO: Hacer esto!
        return True

    def check_sing_fourty(self):
        can_sing = False
        if self.check_last_turn_winned():
            cards = list(filter(
                lambda c: c.get("number") in ('K', 'S'),
                self.hand))
                # TODO: ACABAR ESTO!
            can_sing = True
        return can_sing

    def check_sing_twenty(self):
        can_sing = False
        if self.check_last_turn_winned():
            cards = list(filter(
                lambda c: c.get("number") in ('K', 'S'),
                self.hand))
            can_sing = True
        return can_sing

    def get_legal_actions(self):
        if not self.lastcards_mode:
            return self.hand
        for index in range(1, 4):
            player_index = (self.index + index) % 4
            card = self.table[player_index]
            if not card:
                continue
            first_card = card
            break
        else:
            return self.hand
        availables_cards = []
        cards_same_suit = list(filter(
            lambda c: c.get("suit") == first_card.get("suit"), self.hand))
        if cards_same_suit:
            for card in cards_same_suit:
                card_value = self.get_card_turn_value(
                    card, first_card.get("suit"))
                for card_played in self.table:
                    if not card_played:
                        continue
                    card_played_value = self.get_card_turn_value(
                        card_played, first_card.get("suit"))
                    if card_value < card_played_value:
                        break
                else:
                    availables_cards += [card]
            if not availables_cards:
                availables_cards = cards_same_suit
        else:
            cards_trump = list(filter(
                lambda c: c.get("suit") == self.trump.get("suit"), self.hand))
            if not cards_trump:
                return self.hand
            if self.check_trusted():
                return self.hand
            for card in cards_trump:
                card_value = self.get_card_turn_value(
                    card, first_card.get("suit"))
                for card_played in self.table:
                    if not card_played:
                        continue
                    card_played_value = self.get_card_turn_value(
                        card_played, first_card.get("suit"))
                    if card_value < card_played_value:
                        break
                else:
                    availables_cards += [card]
            if not availables_cards:
                availables_cards = cards_trump
        sing_fourty = self.check_sing_fourty()
        sing_twenty = self.check_sing_twenty()
        return list(availables_cards)

    def get_card_turn_value(self, card, turn_suit):
        value = 0
        cardsValue = {
            '1': 10,
            '3': 9,
            'K': 8,
            'S': 7,
            'C': 6,
            '7': 5,
            '6': 4,
            '5': 3,
            '4': 2,
            '2': 1,
        }
        if self.trump.get("suit") == card.get("suit"):
            value += 20
        elif turn_suit == card.get("suit"):
            value += 10
        value += cardsValue[card.get("number")]
        return value

    def print(self):
        if self.debug:
            print("#" * 50)
            # print(f"Turno: {self.is_turn}")
            print("Hand: {}".format(self.serialize().get("hand")))
            print("Table: {}".format(self.serialize_table()))

    def serialize_table(self):
        return [
            c and self.print_card(c) or "-" for c in self.table]

    def play_card(self):
        try:
            cards_legal_actions = self.get_legal_actions()
            if not cards_legal_actions:
                time.sleep(1)
                return
            card_index = randrange(len(cards_legal_actions))
            card = cards_legal_actions[card_index]
            # if self.lastcards_mode:
            #     print("\tTrump: {}".format(self.print_card(self.trump)))
            #     print("\tTable: {}".format(self.serialize_table()))
            #     print("\tHand: {}".format(self.serialize().get("hand")))
            #     print("\tLegal: {}".format([
            #         self.print_card(c) for c in cards_legal_actions]))
            #     print("\tCard: {}".format(self.print_card(card)))
            #     print("")
            self.emit("playCard", {"card": card})
            self.is_turn = False
        except Exception as e:
            print("ERROR: {}".format(e))
            print(f"card_index: {card_index}")
            print("Mano: {}".format(self.serialize().get("hand")))
        return card

    def get_payload(self, data):
        mult = 1
        if data.get("turnTeamWinner") != self.team:
            mult = -1
        payload = data.get("tableScore")
        payload = (payload * 100) / 54
        return payload * mult

    def print_card(self, card):
        numbers = {
            '1': 'AS', 
            '2': 'Dos', 
            '3': 'Tres', 
            '4': 'Cuatro', 
            '5': 'Cinco', 
            '6': 'Seis', 
            '7': 'Siete', 
            'S': 'Sota', 
            'C': 'Caballo', 
            'K': 'Rey', 
        }
        suits = {
            'O': 'Oros',
            'C': 'Copas',
            'E': 'Espadas',
            'B': 'Bastos',
        }
        return ("{} de {}{}".format(
            numbers.get(card.get("number")),
            suits.get(card.get("suit")),
            "" if card.get("suit") != self.trump.get("suit") else " (*)"
        ))
    
    def get_next_turn_player(self):
        self.sio.emit("getNextTurnPlayer", {})

    def define_events(self):
        sio = self.sio

        @sio.on('playerAccepted')
        def player_accepted(data):
            player_data = data.get("playerData", {})
            self.id = player_data.get("id")
            self.name = player_data.get("name")
            self.index = player_data.get("index")
            self.team = player_data.get("team", {}).get("id")
            self.hand = player_data.get("hand")
        
        @sio.on('canStartGame')
        def start_game(data):
            sio.emit("getHand", {})
            sio.emit("getNextTurnPlayer", {})
            sio.emit("getTrump", {})

        @sio.on('setHand')
        def set_hand(data):
            self.hand = data.get("hand", [])

        @sio.on('setNextTurnPlayer')
        def set_next_turn_player(data):
            self.is_turn = data.get("nextTurnPlayer", {}).get("id") == self.id
        
        @sio.on('setTrump')
        def set_trump(data):
            self.trump = data.get("trump")

        @sio.on('playedCard')
        def played_card(data):
            player_index = data.get("playerIndex")
            if data.get("error"):
                self.is_turn = True
                return
            card = data.get("card")
            if self.index == player_index:
                self.hand = [
                    c for c in self.hand if c.get(
                        "name") != card.get("name")]
            self.table[player_index] = card
            self.deck += [card]
            if data.get("endTurn"):
                if self.debug:
                    # TODO: Que hacer con el payload!!
                    payload = self.get_payload(data)
                self.table = [None, None, None, None]
                sio.emit("getHand", {})
            if data.get("endGame"):
                sio.emit('checkWinners', {})
            elif data.get("lastCardsMode"):
                self.lastcards_mode = True

        @sio.on('endGame')
        def end_game(data):
            if data.get("deVueltaMode"):
                self.is_turn = False
                sio.emit("getTrump", {})
                sio.emit("getHand", {})
                sio.emit("getNextTurnPlayer", {})
            else:
                self.winner_team = "team1"
                self.team1_score = data.get("team1")
                self.team2_score = data.get("team2")
                if data.get("team1") < data.get("team2"):
                    self.winner_team = "team2"
                sio.disconnect()
            

while True:
    game_start_time = time.time()
    print("#" * 50)
    print("Partida nueva!")
    print("#" * 50)
    player1 = Player("Player1", debug=True)
    player1.enter_game()
    player2 = Player("Player2")
    player2.enter_game()
    player3 = Player("Player3")
    player3.enter_game()
    player4 = Player("Player4")
    player4.enter_game()
    time.sleep(5)
    while True:
        try:
            if player1.winner_team:
                print(f"Team 1: {player1.team1_score}")
                print(f"Team 2: {player1.team2_score}")
                print(f"Ganador: {player1.winner_team}")
                break
            if player1.is_turn:
                player1.play_card()
            elif player2.is_turn:
                player2.play_card()
            elif player3.is_turn:
                player3.play_card()
            elif player4.is_turn:
                player4.play_card()
            player1.get_next_turn_player()
            player2.get_next_turn_player()
            player3.get_next_turn_player()
            player4.get_next_turn_player()
            time.sleep(1)
        except Exception:
            pass
    print("Time %.2f" % (time.time() - game_start_time))
    time.sleep(1)