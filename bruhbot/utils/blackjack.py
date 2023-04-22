from aenum import Enum, NoAlias
import random

class Cards(Enum):
    _settings_ = NoAlias

    ACE_1 = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 10
    QUEEN = 10
    KING = 10
    ACE = 11

    @classmethod
    def from_int(cls, i: int):
        match i:
            case 2:
                return cls.TWO
            case 3:
                return cls.THREE
            case 4:
                return cls.FOUR
            case 5:
                return cls.FIVE
            case 6:
                return cls.SIX
            case 7:
                return cls.SEVEN
            case 8:
                return cls.EIGHT
            case 9:
                return cls.NINE
            case 10:
                return cls.TEN

    # was going to add __add__ for epic but too lazy
    # maybe __radd__ or somn idk



def get_card(stack):

    type = random.randint(0, 3)
    card = stack[type].pop(random.randint(0, len(stack[type]) - 1))

    match card:
        case 1:
            card = Cards.ACE
        case 11:
            card = Cards.JACK
        case 12:
            card = Cards.QUEEN
        case 13:
            card = Cards.KING
        case _:
            card = Cards.from_int(card)

    return type, card

def count_value(cards: list[Cards]) -> int:
    # uso `while True` para cambiar los ases que vale 11 a los que valen 1 uno por uno, asique no tendria que ser infinito y nunca muchas repeticiones, de todas formas abria que hacer un contador por si hay algun fallo para que no me maxee la cpu 👍
    while True:
        if sum([c.value for c in cards]) <= 21:
            break

        if Cards.ACE not in cards:
            break

        for i, c in enumerate(cards):
            if c == Cards.ACE:
                cards[i] = Cards.ACE_1
                break
        
    return sum([c.value for c in cards])

# no abrir ⚠️‼️
def get_card_emoji(type: int, value: Cards):
    # yes this is going to be awful
    # i could fetch all emojis in a guild and get it by name which is more organized and shit
    # but im scared about ratelimits so imma keep it like this 😁 (😨)

    # yes i really hate myself
    match [type, value]:
        case [0, Cards.ACE | Cards.ACE_1]:
            return "<:ac:1017157524874596353>"
        case [0, Cards.TWO]:
            return "<:2c:1017158057433763851>"
        case [0, Cards.THREE]:
            return "<:3c:1017158017390759957>"
        case [0, Cards.FOUR]:
            return "<:4c:1017157981235839036>"
        case [0, Cards.FIVE]:
            return "<:5c:1017157924856021022>"
        case [0, Cards.SIX]:
            return "<:6c:1017157870070018119>"
        case [0, Cards.SEVEN]:
            return "<:7c:1017157823395799040>"
        case [0, Cards.EIGHT]:
            return "<:8c:1017157775765282977>"
        case [0, Cards.NINE]:
            return "<:9c:1017157735130865695>"
        case [0, Cards.TEN]:
            return "<:10c:1017157675932467220>"
        case [0, Cards.JACK]:
            return "<:jc:1017157275183501352>"
        case [0, Cards.QUEEN]:
            return "<:qc:1017156885058703483>"
        case [0, Cards.KING]:
            return "<:kc:1017157204413009990>"
        case [1, Cards.ACE | Cards.ACE_1]:
            return "<:ad:1017157523654053958>"
        case [1, Cards.TWO]:
            return "<:2d:1017158059019206656>"
        case [1, Cards.THREE]:
            return "<:3d:1017158019022323773>"
        case [1, Cards.FOUR]:
            return "<:4d:1017157982733209641>"
        case [1, Cards.FIVE]:
            return "<:5d:1017157926168829983>"
        case [1, Cards.SIX]:
            return "<:6d:1017157870896300163>"
        case [1, Cards.SEVEN]:
            return "<:7d:1017157825027395735>"
        case [1, Cards.EIGHT]:
            return "<:8d:1017157777010987028>"
        case [1, Cards.NINE]:
            return "<:9d:1017157736825368576>"
        case [1, Cards.TEN]:
            return "<:10d:1017157677064913056>"
        case [1, Cards.JACK]:
            return "<:jd:1017157276555034714>"
        case [1, Cards.QUEEN]:
            return "<:qd:1017156887579480096>"
        case [1, Cards.KING]:
            return "<:kd:1017157205893578853>"
        case [2, Cards.ACE | Cards.ACE_1]:
            return "<:ah:1017157489596313691>"
        case [2, Cards.TWO]:
            return "<:2h:1017158060260724806>"
        case [2, Cards.THREE]:
            return "<:3h:1017158020733607956>"
        case [2, Cards.FOUR]:
            return "<:4h:1017157984729706607>"
        case [2, Cards.FIVE]:
            return "<:5h:1017157927494221886>"
        case [2, Cards.SIX]:
            return "<:6h:1017157872456581201>"
        case [2, Cards.SEVEN]:
            return "<:7h:1017157826491207821>"
        case [2, Cards.EIGHT]:
            return "<:8h:1017157778156048425>"
        case [2, Cards.NINE]:
            return "<:9h:1017157738444357662>"
        case [2, Cards.TEN]:
            return "<:10h:1017157678390333450>"
        case [2, Cards.JACK]:
            return "<:jh:1017157277964320849>"
        case [2, Cards.QUEEN]:
            return "<:qh:1017156889357848666>"
        case [2, Cards.KING]:
            return "<:kh:1017157207210610720>"
        case [3, Cards.ACE | Cards.ACE_1]:
            return "<:as:1017157491781533818>"
        case [3, Cards.TWO]:
            return "<:2s:1017158061481271446>"
        case [3, Cards.THREE]:
            return "<:3s:1017158022402953290>"
        case [3, Cards.FOUR]:
            return "<:4s:1017157986348707871>"
        case [3, Cards.FIVE]:
            return "<:5s:1017157928760909914>"
        case [3, Cards.SIX]:
            return "<:6s:1017157873496772681>"
        case [3, Cards.SEVEN]:
            return "<:7s:1017157827787235440>"
        case [3, Cards.EIGHT]:
            return "<:8s:1017157779418529842>"
        case [3, Cards.NINE]:
            return "<:9s:1017157733667065866>"
        case [3, Cards.TEN]:
            return "<:10s:1017157679518584872>"
        case [3, Cards.JACK]:
            return "<:js:1017157273841307728>"
        case [3, Cards.QUEEN]:
            return "<:qs:1017156890926518383>"
        case [3, Cards.KING]:
            return "<:ks:1017157202663985244>"
