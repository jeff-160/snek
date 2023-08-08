import nextcord
from nextcord.ext import commands

from random import randint
from time import sleep


snek = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
@snek.event
async def on_ready():
    print("Snek is running")

class Pos():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Snake():
    def __init__(self):
        self.dir = None
        self.body = [Pos(0,0)]

class Game():
    Tiles = {
        "Grid": "🟩",
        "Apple": "🍎",
        "Snake": "🟪"
    }

    def __init__(self, context):
        self.context = context
        self.message = None

        self.GridWidth = 11
        self.grid = []
        self.apple = Pos(0,0)
        
        self.snake = Snake()
        self.snake.body[0].x = self.snake.body[0].y = int(self.GridWidth/2)

    def changetile(self, x, y, tile):
        strlist = list(self.grid[y])
        strlist[x] = Game.Tiles[tile]
        self.grid[y] = "".join(strlist)

    async def display(self):
        self.grid = []
        for i in range(self.GridWidth):
            self.grid.append([])
            grid = self.grid[len(self.grid)-1]
            for j in range(self.GridWidth):
                grid.append(Game.Tiles["Grid"])
        self.grid = ["".join(line) for line in self.grid]

        for snakeblock in self.snake.body: 
            self.changetile(snakeblock.x, snakeblock.y, "Snake")
        self.changetile(self.apple.x, self.apple.y, "Apple")

        self.grid = "\n".join(self.grid)
        if self.message: 
            await self.message.edit(content=self.grid)
        else:
            self.message = await self.context.send(self.grid)

    async def spawnapple(self):
        self.apple = Pos(randint(0, self.GridWidth-1), randint(0, self.GridWidth-1))

    async def gameloop(self):
        if self.snake.body[0].x==self.apple.x and self.snake.body[0].y==self.apple.y: 
            await self.spawnapple()
        await self.display()
        sleep(0.5)
        self.snake.body[0].x+=1
        return await self.gameloop()
                

@snek.command(name="start", help="Start a new game of snake")
async def start(ctx):
    new_game = Game(ctx)
    await new_game.gameloop()