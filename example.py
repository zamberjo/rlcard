# https://python-socketio.readthedocs.io/en/latest/client.html
import socketio
import asyncio
import time
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
        # print(f"[EMIT] {event}({params})")
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
            card_index = randrange(len(cards_legal_actions))
            card = cards_legal_actions[card_index]
            if self.lastcards_mode:
                print("\tTrump: {}".format(self.print_card(self.trump)))
                print("\tTable: {}".format(self.serialize_table()))
                print("\tHand: {}".format(self.serialize().get("hand")))
                print("\tLegal: {}".format([
                    self.print_card(c) for c in cards_legal_actions]))
                print("\tCard: {}".format(self.print_card(card)))
                print("")
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
        print("Ganan el turno!" if mult > 0 else "Pierden el turno!")
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
            if self.debug:
                print("TRUMP {}".format(self.trump))
                # print("TRUMP {}".format(self.print_card(self.trump)))

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
            if self.debug:
                try:
                    print("Player {} play card: {}".format(
                        player_index, self.print_card(card)))
                except Exception as e:
                    import pdb; pdb.set_trace()
                    raise
            self.table[player_index] = card
            self.deck += [card]
            if data.get("endTurn"):
                if self.debug:
                    self.print()
                    payload = self.get_payload(data)
                    print(f"Payload: {payload}")
                    print("#" * 50)
                self.table = [None, None, None, None]
                sio.emit("getHand", {})
            if data.get("winner"):
                self.winner = data.get("winner")
                if self.debug:
                    print("WINNER {}".format(data.get("winner")))
            elif data.get("endGame"):
                if self.debug:
                    print("ENDGAME!")
                sio.emit('checkWinners', {})
            elif data.get("lastCardsMode"):
                if self.debug:
                    print("ÚLTIMAS!!")
                self.lastcards_mode = True

        @sio.on('endGame')
        def end_game(data):
            if self.debug:
                print(f"dada: {data}")
            if data.get("deVueltaMode"):
                self.is_turn = False
                sio.emit("getTrump", {})
                sio.emit("getHand", {})
                sio.emit("getNextTurnPlayer", {})
                time.sleep(5)
            else:
                self.winner_team = "team1"
                if data.get("team1") < data.get("team2"):
                    self.winner_team = "team2"
                
            

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
print("END!")