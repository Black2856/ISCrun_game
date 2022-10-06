import random
import game as g

class MoveCost:
    cost = [
        0,
        1,
        2,
        3,
        4
    ]

class MoveRoute:
    moveCost = MoveCost()
    lastState = 0 #GameArea
    route = [] #経路 (動作定義)
    totalCost = 0
    phase = 0 #経路のフェーズ
    previous = 0 #前の経路のポインタ

    def __init__(self, route):
        self.route = route
        self.calcCost()

    def setRoute(self, route):
        self.route = route
        self.calcCost()

    def addRoute(self, route):
        self.route.append(route)
        self.calcCost()
        
    def calcCost(self):
        self.totalCost = 0
        for i in range(len(self.route)):
            self.totalCost += self.moveCost.cost[self.route[i]]

class MgtRoute:
    moveRoute = []
    latestIdx = []

    def __init__(self):
        moveRoute = []

    def add(self, moveRoute): #MoveRouteクラスをlistに追加
        self.moveRoute.append(moveRoute)
        self.latestIdx.append(moveRoute)
        if(moveRoute.previous != 0):
            self.latestIdx.remove(moveRoute.previous)
        return

    def get(self, idx): #idx番号の配置状態を返す
        return self.moveRoute[idx]

    def calcRoute(self, moveRoute): #全ての距離コスト
        cost = 0
        itr = moveRoute
        while itr.previous != 0:
            cost += itr.totalCost
            itr = itr.previous
        cost += itr.totalCost
        return cost

class Search:
    mgtRoute = MgtRoute()

    def display(self):
        #for i in range(len(self.mgtRoute.moveRoute)):
        #    print(self.mgtRoute.moveRoute[i].totalCost)
        print(self.mgtRoute.moveRoute)
        print("\n")
        print(self.mgtRoute.latestIdx)