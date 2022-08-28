import random
import game as g
import search as s
import copy

colorBlock = [1,1,2,2,3,3,4,4]
baseColorBlock = [1,2,3,4]
bonusColorBlock = random.randint(1, 4)
random.shuffle(colorBlock)
random.shuffle(baseColorBlock)

gameArea = g.GameArea(colorBlock, baseColorBlock, bonusColorBlock)
player = g.Player(gameArea, 1, 0, 0)
player.rotate(135)
player.display()
player.move(1)
gameArea.display()
player.diagonalMove()
player.rotate(-135)
player.move(1)
player.putMove()
print("")
player.display()
#gameArea.setBlock(5, sc.Block(43232, 0))
gameArea.display()
print("")

moveRoute = s.MoveRoute([1,1,1,1,1])
moveRoute.previous = 0
moveRoute.phase = 1

search = s.Search()
search.mgtRoute.add(copy.copy(moveRoute))
moveRoute.setRoute([4])
moveRoute.previous = search.mgtRoute.moveRoute[0]
moveRoute.phase = 2
search.mgtRoute.add(copy.copy(moveRoute))
moveRoute.setRoute([3,2,1,3])
moveRoute.previous = search.mgtRoute.moveRoute[1]
moveRoute.phase = 3
search.mgtRoute.add(copy.copy(moveRoute))

print(search.mgtRoute.calcRoute(search.mgtRoute.moveRoute[2]))

search.display()