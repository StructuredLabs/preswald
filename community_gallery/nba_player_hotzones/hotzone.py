from collections import defaultdict
from constants import Ranges , FG, Areas

class HotZoneClassifier:
    def __init__(self):
        '''
        For each shot zone keep track of the shots attempted and shots made
        '''
        self.area = defaultdict(lambda: defaultdict(lambda : FG(attempted=0, made=0)))
        self.ranges = {
            "Less Than 8 ft." : 0,
            "8-16 ft." : 1,
            "16-24 ft." : 2,
            "24+ ft." : 3
        }

    def addShot(self, area : str, range : str, shotMade : int) -> None:
        '''
        Add shot record for corresponding area and range
        '''
        self.area[area][self.ranges[range]].attempted += 1
        self.area[area][self.ranges[range]].made += shotMade
    
    def fgPercentage(self, area : str, range : str) -> float:
        '''
        calculate shots made / shots attempted for a given area and range
        '''
        return self.area[area][self.ranges[range]].made / self.area[area][self.ranges[range]].attempted
    
    def getPercentageAllZones(self) -> dict:
        '''
        Get the FG percentage of every area at every range
        '''
        res = defaultdict(list)
        for a in self.area.keys():
            for r in Ranges:
                if (self.area[a][self.ranges[r.value.description]].attempted == 0):
                    res[a].append(0)
                else:
                    res[a].append(self.area[a][self.ranges[r.value.description]].made / self.area[a][self.ranges[r.value.description]].attempted)
        
        for a in Areas:
            if a.value not in res:
                res[a.value] = [0,0,0,0]
        res[Areas.LC.value][Ranges.BETWEEN_8_16_FT.value.idx] = res[Areas.C.value][Ranges.BETWEEN_8_16_FT.value.idx]
        res[Areas.RC.value][Ranges.BETWEEN_8_16_FT.value.idx] = res[Areas.C.value][Ranges.BETWEEN_8_16_FT.value.idx]
        return res
    