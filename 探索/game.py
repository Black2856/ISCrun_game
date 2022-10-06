import copy

class Block: #ブロック
    color = 0 # 1:赤 2:青 3:緑 4:黄
    bonus = 0 # 0か1

    def __init__(self, color:int, bonus:int):
        self.color = color
        self.bonus = bonus

class Marker: #交点マーカー
    markerPosID = 0 #1~16
    aroundMarker = [0, 0, 0, 0] #[上,右,下,左]
    aroundBlock = [0, 0, 0, 0]

    def __init__(self, markerPosID:int):
        self.markerPosID = markerPosID

    def aroundMarkerSet(self, aroundMarker): #Markerクラスの参照 または 0 の4つの配列[上,右,下,左]
        self.aroundMarker = aroundMarker

    def aroundBlockSet(self, aroundBlock): #BlockPlaceクラスの参照 または 0 の4つの配列[rightup, rightdown, leftdown, leftup]
        self.aroundBlock = aroundBlock

class BlockPlace: #ブロック置き場
    blockPosID = 0 #6~13
    aroundMarker = [0, 0, 0, 0]
    placedBlock = 0 #Blockクラス または 0

    def __init__(self, blockPosID:int, block):
        self.blockPosID = blockPosID
        self.placedBlock = block

    def aroundMarkerSet(self, aroundMarker): #Markerクラスの参照 [rightup, rightdown, leftdown, leftup]
        self.aroundMarker = aroundMarker

    def changeBlock(self, block):
        self.placedBlock = block

class IntrusionCircle: #侵入サークル
    BlockPosID = 5
    placedBlock = 0

    def __init__(self, blockColor):
        self.placedBlock = Block(blockColor, 1)

class BaseCircle: #ベースサークル
    blockPosID = 0 #1~4
    placedBlock = 0 #Blockクラス または 0

    def __init__(self, blockPosID:int, blockColor):
        self.blockPosID = blockPosID
        self.placedBlock = Block(blockColor, 0)

class BlockBaseArea: #ブロックベースエリア
    placedBlock = [] #配置されているブロック
    placedMarker = [] #配置処理が行われたマーカー
    baseCircle = 0 #BaseCircleのクラス

    def __init__(self, blockPosID:int, blockColor):
        self.baseCircle = BaseCircle(blockPosID, blockColor)
        self.placedBlock = []
        placedMarker = []
        baseCircle = 0

    def add(self, block, marker):
        self.placedBlock.append(block)
        self.placedMarker.append(marker)

class BlockArea: #ブロックエリア
    marker = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    blockPlace = [0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, blockColor): #ブロックの配色を配列で受け取り初期化
        for i in range(len(self.marker)):
            self.marker[i] = Marker(i + 1)
        for i in range(len(self.marker)):
            aroundMarker = [0, 0, 0, 0]
            if((i-4) > -1):
                aroundMarker[0] = self.marker[i-4]
            if((i+1) < 16):
                aroundMarker[1] = self.marker[i+1]
            if((i+4) < 16):
                aroundMarker[2] = self.marker[i+4]
            if((i-1) > -1):
                aroundMarker[3] = self.marker[i-1]
            self.marker[i].aroundMarkerSet(aroundMarker)

        for i in range(len(self.blockPlace)):
            self.blockPlace[i] = BlockPlace(i + 6, Block(blockColor[i], 0))

        for i in range(0,2+1):
            aroundMarker = [0, 0, 0, 0]
            aroundMarker[0] = self.marker[i+1]
            aroundMarker[1] = self.marker[i+4]
            aroundMarker[2] = self.marker[i+5]
            aroundMarker[3] = self.marker[i]
            aroundMarker[0].aroundBlockSet([0, 0, self.blockPlace[i], 0])
            aroundMarker[1].aroundBlockSet([0, 0, 0, self.blockPlace[i]])
            aroundMarker[2].aroundBlockSet([self.blockPlace[i], 0, 0, 0])
            aroundMarker[3].aroundBlockSet([0, self.blockPlace[i], 0, 0])
            self.blockPlace[i].aroundMarkerSet(aroundMarker)
        for i in range(0,1+1):
            aroundMarker = [0, 0, 0, 0]
            aroundMarker[0] = self.marker[i*2+1 +4]
            aroundMarker[1] = self.marker[i*2+4 +4]
            aroundMarker[2] = self.marker[i*2+5 +4]
            aroundMarker[3] = self.marker[i*2 +4]
            aroundMarker[0].aroundBlockSet([0, 0, self.blockPlace[i+3], 0])
            aroundMarker[1].aroundBlockSet([0, 0, 0, self.blockPlace[i+3]])
            aroundMarker[2].aroundBlockSet([self.blockPlace[i+3], 0, 0, 0])
            aroundMarker[3].aroundBlockSet([0, self.blockPlace[i+3], 0, 0])
            self.blockPlace[i+3].aroundMarkerSet(aroundMarker)
        for i in range(0,2+1):
            aroundMarker = [0, 0, 0, 0]
            aroundMarker[0] = self.marker[i+1 +8]
            aroundMarker[1] = self.marker[i+4 +8]
            aroundMarker[2] = self.marker[i+5 +8]
            aroundMarker[3] = self.marker[i +8]
            aroundMarker[0].aroundBlockSet([0, 0, self.blockPlace[i+5], 0])
            aroundMarker[1].aroundBlockSet([0, 0, 0, self.blockPlace[i+5]])
            aroundMarker[2].aroundBlockSet([self.blockPlace[i+5], 0, 0, 0])
            aroundMarker[3].aroundBlockSet([0, self.blockPlace[i+5], 0, 0])
            self.blockPlace[i+5].aroundMarkerSet(aroundMarker)

class GameArea:#ブロック de　お方付け
    blockArea = 0
    blockBaseArea = [0, 0, 0, 0]
    intrusionCircle = 0
    
    def __init__(self, colorBlock, baseColorBlock, bonusColorBlock): #[8],[4] それぞれ1~4
        self.blockArea = BlockArea(colorBlock)
        self.intrusionCircle = IntrusionCircle(bonusColorBlock)
        for i in range(len(self.blockBaseArea)):
            self.blockBaseArea[i] = BlockBaseArea(i + 1, baseColorBlock[i])

    def display(self):
        print("intrusionCircle.placedBlock.color (posID = ",self.intrusionCircle.BlockPosID," ) =",self.intrusionCircle.placedBlock.color)
        for i in range(len(self.blockBaseArea)):
            print("blockbaseArea[",i,"].placedBlock=",self.blockBaseArea[i].placedBlock)
            print("blockbaseArea[",i,"].placedBlock.baseCircle.placedBlock (posID = ",self.blockBaseArea[i].baseCircle.blockPosID,") =",self.blockBaseArea[i].baseCircle.placedBlock.color)
        for i in range(len(self.blockArea.blockPlace)):
            if(self.blockArea.blockPlace[i].placedBlock != 0):
                print("blockArea.blockPlace[",i,"].placedBlock.color =",self.blockArea.blockPlace[i].placedBlock.color)
            else:
                print("blockArea.blockPlace[",i,"].placedBlock.color = 0")

    def getMarker(self, markerPosID):
        if(1 <= markerPosID and markerPosID <= 16):
            return self.blockArea.marker[markerPosID - 1]

    def getBlock(self, blockPosID):
        if(1 <= blockPosID and blockPosID <= 4):
            return self.blockBaseArea[blockPosID - 1].baseCircle.placedBlock
        elif(blockPosID == 5):
            return self.intrusionCircle.placedBlock
        elif(6 <= blockPosID and blockPosID <= 13):
            return self.blockArea.blockPlace[blockPosID - 6].placedBlock

    def setBlock(self, blockPosID, block):#ブロック配置 排除はblock = 0
        if(1 <= blockPosID and blockPosID <= 4):
            self.blockBaseArea[blockPosID - 1].baseCircle.placedBlock = block
        elif(blockPosID == 5):
            self.intrusionCircle.placedBlock = block
        elif(6 <= blockPosID and blockPosID <= 13):
            self.blockArea.blockPlace[blockPosID - 6].placedBlock = block

class Player: #走行体
    currentLocation = 0 #Markerクラス参照
    rotation = 0 #0~359
    block = 0 #所持ブロック
    gameArea = 0

    def __init__(self,gameArea, currentLocation, rotation, block):
        self.gameArea = gameArea
        self.currentLocation = gameArea.getMarker(currentLocation) #Markerクラス
        self.roration = rotation
        self.block = block #blockクラス

    def display(self):
        print("currentLocation.markerPosID :",self.currentLocation.markerPosID)
        print("rotation :",self.rotation)
        if(self.block != 0):
            print("block.color :",self.block.color)
        else:
            print("block.color : 0")

    def rotate(self, rotate):#回転
        self.rotation = self.rotation + rotate
        if(self.rotation >= 360 or self.rotation < 0):
            self.rotation = self.rotation % 360


    def move(self, operation):#移動 1:前進 2:後退]
        moveRotation = self.rotation
        if(operation == 2):
            moveRotation = (moveRotation + 180) % 360

        if(moveRotation == 0 and self.currentLocation.aroundMarker[0] != 0):
            self.currentLocation = self.currentLocation.aroundMarker[0]
        elif(moveRotation == 90 and self.currentLocation.aroundMarker[1] != 0):
            self.currentLocation = self.currentLocation.aroundMarker[1]
        elif(moveRotation == 180 and self.currentLocation.aroundMarker[2] != 0):
            self.currentLocation = self.currentLocation.aroundMarker[2]
        elif(moveRotation == 270 and self.currentLocation.aroundMarker[3] != 0):
            self.currentLocation = self.currentLocation.aroundMarker[3]

    def diagonalMove(self):#ブロック取得動作
        if(self.rotation == 45):
            if(self.currentLocation.aroundBlock[0] != 0):
                if(self.block != 0):
                    return
                self.block = self.currentLocation.aroundBlock[0].placedBlock
                self.gameArea.setBlock(self.currentLocation.aroundBlock[0].blockPosID, 0)
            try:
                self.currentLocation = self.currentLocation.aroundMarker[0].aroundMarker[1]
            except:
                a = 1
        elif(self.rotation == 135):
            if(self.currentLocation.aroundBlock[1] != 0):
                if(self.block != 0):
                    return
                self.block = self.currentLocation.aroundBlock[1].placedBlock
                self.gameArea.setBlock(self.currentLocation.aroundBlock[1].blockPosID, 0)
            try:
                self.currentLocation = self.currentLocation.aroundMarker[1].aroundMarker[2]
            except:
                a = 1
        elif(self.rotation == 225):
            if(self.currentLocation.aroundBlock[2] != 0):
                if(self.block != 0):
                    return
                self.block = self.currentLocation.aroundBlock[2].placedBlock
                self.gameArea.setBlock(self.currentLocation.aroundBlock[2].blockPosID, 0)
            try:
                self.currentLocation = self.currentLocation.aroundMarker[2].aroundMarker[3]
            except:
                a = 1
        elif(self.rotation == 315):
            if(self.currentLocation.aroundBlock[3] != 0):
                if(self.block != 0):
                    return
                self.block = self.currentLocation.aroundBlock[3].placedBlock
                self.gameArea.setBlock(self.currentLocation.aroundBlock[3].blockPosID, 0)
            try:
                self.currentLocation = self.currentLocation.aroundMarker[3].aroundMarker[0]
            except:
                a = 1

    def putMove(self):#ブロック配置
        li1 = [2, 3, 5 ,8, 9, 12, 14, 15] #追加動作 markerPosID
        li2 = [1, 2, 3, 4, 5, 8, 9, 12, 13, 14, 15, 16] #動作可能 markerPosID
        
        if(self.block == 0 or (self.currentLocation.markerPosID in li2) == False):
            return

        if(self.rotation == 0 and (self.currentLocation in self.gameArea.blockBaseArea[0].placedMarker) == False):
            self.gameArea.blockBaseArea[0].add(self.block, self.currentLocation)
            self.block = 0
        elif(self.rotation == 90 and (self.currentLocation in self.gameArea.blockBaseArea[1].placedMarker) == False):
            self.gameArea.blockBaseArea[1].add(self.block, self.currentLocation)
            self.block = 0
        elif(self.rotation == 180 and (self.currentLocation in self.gameArea.blockBaseArea[2].placedMarker) == False):
            self.gameArea.blockBaseArea[2].add(self.block, self.currentLocation)
            self.block = 0
        elif(self.rotation == 270 and (self.currentLocation in self.gameArea.blockBaseArea[3].placedMarker) == False):
            self.gameArea.blockBaseArea[3].add(self.block, self.currentLocation)
            self.block = 0
        
        if((self.currentLocation.markerPosID in li1) == True):
            self.move(2)