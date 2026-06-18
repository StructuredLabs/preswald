from dataclasses import dataclass
from enum import Enum
from collections import namedtuple


@dataclass
class FG:
    attempted: int
    made: int


@dataclass
class RangeRep:
    description: str
    idx: int


class Ranges(Enum):
    LESS_8_FT = RangeRep("Less Than 8 ft.", 0)
    BETWEEN_8_16_FT = RangeRep("8-16 ft.", 1)
    BETWEEN_16_24_FT = RangeRep("16-24 ft.", 2)
    MORE_24_FT = RangeRep("24+ ft.", 3)


class Areas(Enum):
    LC = "Left Side Center(LC)"
    RC = "Right Side Center(RC)"
    C = "Center(C)"
    R = "Right Side(R)"
    L = "Left Side(L)"
    
playerToCSV = {
    "Anthony Davis" : ["AD", "ADstats"],
    "LeBron James" : ["LBJ", "LBJstats"],
    "Shai Gilgeous-Alexander" : ["SGA", "SGAstats"],
    "Kevin Durant" : ["KD", "KDstats"],
    "Jayson Tatum" : ["JT", "JTstats"],
    "Stephen Curry" : ["SC", "SCstats"],
    "Luka Dončić" : ["LD", "LDstats"],
    "Joel Embiid" : ["JE", "JEstats"],
    "Nikola Jokić" : ["NJ", "NJstats"],
    "Giannis Antetokounmpo" : ["GA", "GAstats"],
}
