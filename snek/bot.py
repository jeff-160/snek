import nextcord
from nextcord.ext import commands

from random import randint
from time import sleep
from re import sub

intents = nextcord.Intents.all()
intents.reactions = True
snek = commands.Bot(command_prefix="!", intents=intents)
players = []

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
        self.x = self.y = 0
        self.body = []
        self.tail = 3
        self.velocity = Pos(0,0)

class Game():
    Tiles = {
        "Grid": "🟩",
        "Apple": "🍎",
        "Snake": "🟪",
        "Dead": "⬜"
    }

    def __init__(self, context, sender):
        self.context = context
        self.message = None
        self.player = sender
        players.append(sender)

        self.GridWidth = 11
        self.grid = []
        self.apple = Pos(0,0); self.spawnapple()
        self.score = 0
        
        self.snake = Snake()
        self.snake.x = self.snake.y = int(self.GridWidth/2)

        @snek.event
        async def on_message_edit(before, after):
            if before.id!=self.message.id: return
            self.message.content = after.content
    
    
    async def AddReaction(self):
        for emoji in ["⬆", "⬇", "⬅", "➡"]:
            await self.message.add_reaction(emoji) 
        def ChangeVelocity(emoji, user):
            if user!=self.player: return
            
            match emoji:
                case "⬆":
                    self.snake.velocity = Pos(0,-1)
                case "⬇":
                    self.snake.velocity = Pos(0,1)
                case "⬅":
                    self.snake.velocity = Pos(-1,0)
                case "➡":
                    self.snake.velocity = Pos(1,0)
        @snek.event
        async def on_reaction_add(reaction, user):
            ChangeVelocity(str(reaction.emoji), user)
        @snek.event
        async def on_reaction_remove(reaction, user):
            ChangeVelocity(str(reaction.emoji), user)
                
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
        message = f"{self.grid}\nApples eaten: {self.score}"
        if self.message: 
            await self.message.edit(content=message)
        else:
            self.message = await self.context.send(message)
            await self.AddReaction()

    def spawnapple(self):
        self.apple = Pos(randint(0, self.GridWidth-1), randint(0, self.GridWidth-1))

    def checkcollision(self):
        return (self.snake.x<0 or
            self.snake.y<0 or
            self.snake.x>=self.GridWidth or
            self.snake.y>=self.GridWidth)
    
    async def endgame(self):
        await self.message.clear_reactions()
        endmessage = (str(self.message.content)
                      .replace(Game.Tiles["Snake"], Game.Tiles["Dead"])
                      .replace("Apples eaten", "YOU DIED YOU FUCKING RETARD\nScore"))
        await self.message.edit(content=endmessage)
        players.pop(players.index(self.player))
        
    async def gameloop(self):
        self.snake.x+=self.snake.velocity.x
        self.snake.y+=self.snake.velocity.y
        self.snake.body.append(Pos(self.snake.x, self.snake.y))

        if self.checkcollision(): 
            return await self.endgame()
        
        if self.snake.x==self.apple.x and self.snake.y==self.apple.y:
            self.score+=1
            self.snake.tail+=1
            self.spawnapple()

        await self.display()
        while len(self.snake.body)>self.snake.tail:
            self.snake.body.pop(0)
        sleep(0.1)
        return await self.gameloop()
                

@snek.command(name="start", help="Start a new game of snake")
async def start(ctx):
    if ctx.message.author in players:
        return await ctx.send("You're already in a game!")
    new_game = Game(ctx, ctx.message.author)
    await new_game.gameloop()