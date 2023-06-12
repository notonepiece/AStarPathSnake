import time as t
import pygame
from pygame import *
import random
from enum import Enum
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="wzh",
  database="snake"
)

mycursor = mydb.cursor()

# 颜色
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
GREY = (128, 128, 128)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)

h = 0



# 定义节点
# class Node:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y

# 定义方位
class Direction(Enum):
    up = 0
    down = 1
    left = 2
    right = 3


# 定义点的坐标
class Point:
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
    def copy(self):
        return Point(row=self.row, col=self.col)

# 初始化
pygame.init()
# 文字
font01 = pygame.font.Font("10014.ttf", 50)
surface1 = font01.render("Game Over", True, RED)

# 设置大小
window_size = weight, height = 400, 400
window = pygame.display.set_mode(window_size)

Row = int(height // 20)
Col = int(weight // 20)

W = weight//Row
H = height//Col

direction = Direction.up.value

# 定义蛇的头和蛇的身子
snake_head = Point(row=int(height/2/Row), col=int(weight/2/Col))
snake_body = [
    Point(row=snake_head.row+1, col=snake_head.col),
    Point(row=snake_head.row+2, col=snake_head.col),
    Point(row=snake_head.row+3, col=snake_head.col)
]


# 设置标题
pygame.display.set_caption("snake")

def rect(Point, color):
    left = Point.col * Col
    top = Point.row * Row
    pygame.draw.rect(window, color, (left, top, Col, Row))


# 随机生成障碍
obstacles = []
def obstacle():
    while True:
        obstacle = Point(
            row=random.randint(0, height / Row - 1),
            col=random.randint(0, weight / Col - 1))
        isObstacleInSnakeBody = False
        for body in snake_body:
            if obstacle.row == body.row and obstacle.col == body.col:
                isObstacleInSnakeBody = True
                break
        if obstacle.row != snake_head.row and obstacle.col != snake_head.col and not isObstacleInSnakeBody :
            return obstacle

for o in range(5):
    obstacles.append(obstacle())


# 绘制网格线
def draw_grid(win, rows, width):

    # gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * rows), (width, i * rows))
    for j in range(rows):
        pygame.draw.line(win, GREY, (j * rows, 0), (j * rows, width))

# 随机生成食物
def genfood():
    while True:
        food = Point(
            row=random.randint(0, height / Row - 1),
            col=random.randint(0, weight / Col - 1))
        isFoodInSnakeBody = False
        for body in snake_body:
            if food.row == body.row and food.col == body.col:
                isFoodInSnakeBody = True
                break
        isObstacleEqualFood = False
        for o in obstacles:
            if food.row == o.row and food.col == o.col:
                isObstacleEqualFood = True
                break
        if food.row != snake_head.row and food.col != snake_head.col and not isFoodInSnakeBody and not isObstacleEqualFood:
            return food

class Node:
    g = 0
    h = 0
    f = 0
    isPath = False
    def __init__(self, row, col):
        self.row = row
        self.col = col
    def setG(self, g):
        self.g = g
    def setH(self, h):
        self.h = h
    def setF(self, f):
        self.f = f
    def setIsPath(self):
        self.isPath = True
    def setSons(self, sons):
        self.sons = sons

# 计算H值
def computeH(begin, end):
    return abs(begin.row - end.row) + abs(begin.col - end.col)


# 获取地图
def getMap(row, col, snakeBody, obstacles):
    map = []
    for i in range(row):
        y = []
        for j in range(col):
            y.append(1)
        map.append(y)
    for i in snakeBody:
        map[i.row][i.col] = 0
    for i in obstacles:
        map[i.row][i.col] = 0
    return map


# 获取路径
def getPath(map, begin, end):
    begin = begin
    # 终点
    end = end
    map_copy = []
    for x in range(len(map)):
        col = []
        for y in range(len(map[x])):
            col.append(0)
        map_copy.append(col)
    pCurrent = begin
    map_copy[pCurrent.row][pCurrent.col] = 1
    result = []

    while True:
        son = []
        for i in range(4):
            x = pCurrent.row
            y = pCurrent.col
            g = pCurrent.g
            h = pCurrent.h
            f = pCurrent.f
            pTemp = Node(x, y)
            pTemp.setH(h)
            pTemp.setG(g)
            pTemp.setF(f)
            if i == Direction.up.value:
                pTemp.row -= 1
            elif i == Direction.down.value:
                pTemp.row += 1
            elif i == Direction.left.value:
                pTemp.col -= 1
            elif i == Direction.right.value:
                pTemp.col += 1
            # print(f"getPath中的{pTemp.row,pTemp.col}")
            if pTemp.row >= 0 and pTemp.col >= 0 and pTemp.row < Row and pTemp.col < Col:
                if map_copy[pTemp.row][pTemp.col] != 1 and map[pTemp.row][pTemp.col] != 0:
                    # 计算h值
                    pTemp.h = computeH(pTemp, end)
                    # 计算f值
                    pTemp.f = pTemp.h
                    # 加入节点
                    son.append(pTemp)

        pCurrent.setSons(son)

        if len(pCurrent.sons) == 0:

            if len(result) != 0:
                result.pop()
                if len(result) != 0:
                    pCurrent = result[-1]
        else:
            # 找到孩子节点中f值最小的
            min = pCurrent.sons[0].f
            for node in pCurrent.sons:
                if min >= node.f:
                    pCurrent = node
                    min = node.f
            result.append(pCurrent)
            # print(f"({pCurrent.row, pCurrent.col}, f={pCurrent.f})")
            map_copy[pCurrent.row][pCurrent.col] = 1
        if pCurrent.col == end.col and pCurrent.row == end.row:
            break
        if len(result) == 0:
            print("not found")
            break
    return result

begin = Node(int(height//2//Row), int(weight//2//Col))


# 游戏循环
quit_game = True
food = genfood()
end = Node(food.row, food.col)
clock = pygame.time.Clock()

AI = 1
result = []
game_finish = True
score = 0
isInsert = False
while quit_game:


    # 绘制
    pygame.draw.rect(window, WHITE, (0, 0, weight, height))

    rect(snake_head, RED)
    for body in snake_body:
        rect(body, PURPLE)
    rect(food, GREEN)
    for o in obstacles:
        rect(o, BLACK)
    draw_grid(window, Row, weight)
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game = False
        Key_pressed = pygame.key.get_pressed()
        if Key_pressed[K_UP]:
            if direction == Direction.left.value or direction == Direction.right.value:
                direction = Direction.up.value
        if Key_pressed[K_DOWN]:
            if direction == Direction.left.value or direction == Direction.right.value:
                direction = Direction.down.value
        if Key_pressed[K_LEFT]:
            if direction == Direction.up.value or direction == Direction.down.value:
                direction = Direction.left.value
        if Key_pressed[K_RIGHT]:
            if direction == Direction.up.value or direction == Direction.down.value:
                direction = Direction.right.value
        if Key_pressed[K_SPACE]:
            AI += 1
            break

    if game_finish:
        if AI % 2 == 0:
            pass
            begin = Node(snake_head.row, snake_head.col)
            end = Node(food.row, food.col)
            map = getMap(Row, Col, snake_body, obstacles)
            result = getPath(map, begin, end)

            if len(result) != 0:
                snake_body.insert(0, snake_head.copy())
                snake_head.row = result[0].row
                snake_head.col = result[0].col
                # print(f"{snake_head.row, snake_head.col}")
                del result[0]
                # 处理食物
                eat = (snake_head.row == food.row and snake_head.col == food.col)
                if eat:
                    food = genfood()
                    score += 1
                if not eat:
                    snake_body.pop()
            else:
                begin = Node(snake_head.row, snake_head.col)
                end = Node(food.row, food.col)
                map = getMap(Row, Col, snake_body, obstacles)
                result = getPath(map, begin, end)

        else:
            result = []
            # 处理蛇的身子
            snake_body.insert(0, snake_head.copy())
            # 处理食物
            eat = (snake_head.row == food.row and snake_head.col == food.col)

            if eat:
                food = genfood()
                score += 1
            if not eat:
                snake_body.pop()

            if direction == Direction.up.value:
                snake_head.row -= 1
            elif direction == Direction.down.value:
                snake_head.row += 1
            elif direction == Direction.left.value:
                snake_head.col -= 1
            elif direction == Direction.right.value:
                snake_head.col += 1

    # 游戏结束
    dead = False
    if snake_head.row < 0 or snake_head.col < 0 or snake_head.row >= W or snake_head.col >= H:
        dead = True

    for snake in snake_body:
        if snake.row == snake_head.row and snake.col == snake_head.col:
            dead = True

    for o in obstacles:
        if o.row == snake_head.row and o.col == snake_head.col:
            dead = True

    if dead:
        game_finish = False
        window.blit(surface1, (weight // 2 - 110, height // 2 - 50))
        score_show = font01.render(f"得分:{str(score)}", True, RED)
        window.blit(score_show, (weight // 2 - 110, height // 2 + 30))
        if not isInsert:
            sql = "INSERT INTO t_score (s_score) VALUES ({})".format(score)
            mycursor.execute(sql)
            mydb.commit()
            isInsert = True
        mycursor.execute("SELECT * FROM t_score ORDER BY s_score DESC LIMIT 1")
        for x in mycursor:
            max_score = x[1]
        max_score_show = font01.render(f"最高得分:{str(max_score)}", True, RED)
        window.blit(max_score_show, (weight // 2 - 110, height // 2 + 90))
    # 渲染
    pygame.display.flip()

    clock.tick(10)



