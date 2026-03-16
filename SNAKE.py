import tkinter
import random
import threading
import winsound

ROWS = 25
COLS = 25
TILE_SIZE = 25

WINDOW_WIDTH = TILE_SIZE * ROWS  #625
WINDOW_HEIGHT = TILE_SIZE * COLS 

class Tile :
    def __init__(self,x,y):
        self.x = x
        self.y = y


#نافدة اللعبة 
Window = tkinter.Tk()
Window.title("Snake")
Window.resizable(False,False)

canvas = tkinter.Canvas(Window , bg = "black" , width = WINDOW_WIDTH , 
                        height = WINDOW_HEIGHT , borderwidth = 0 ,  highlightthickness = 0)
canvas.pack()
Window.update()
#توسيط النافدة
Window_width  = Window.winfo_width()
Window_height = Window.winfo_height()
screen_width = Window.winfo_screenwidth()
screen_height = Window.winfo_screenheight()

Window_x = int((screen_width/2) - (Window_width/2))
Window_y = int((screen_height/2) - (Window_height/2))
Window.geometry(f"{Window_width}x{Window_height}+{Window_x}+{Window_y}")

#initialize game
snake = Tile(5*TILE_SIZE , 5*TILE_SIZE) # single tile , snake's head
food = Tile(10*TILE_SIZE , 10*TILE_SIZE)
snake_body = [] #multiple snake tiles
velocityx = 1      #الافعلى بالبداية حتتحرك لليمين حتى ما تاكل الطعام وهي ساكنة
velocityy = 0
game_over = False
score = 0
delay = 100          #السرعة الابتدائية 100
high_score = 0
paused = False
wall_mode = True



def beep_async(freq, duration):
    threading.Thread(target=lambda: winsound.Beep(freq, duration)).start()

def play_eat_sound():
    beep_async(900, 300)   

def play_gameover_sound():
    beep_async(700, 500)    

#highsore
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0  # إذا كان الملف غير موجود أو به خطأ

def reset_game():
    global snake, food, snake_body, velocityx, velocityy, game_over, score , delay
    snake = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)
    food = Tile(10 * TILE_SIZE, 10 * TILE_SIZE)
    snake_body = []
    velocityx = 1   # نبدأ بالحركة لليمين مباشرة
    velocityy = 0
    game_over = False
    score = 0
    delay = 100
    wall_mode = True      # إعادة التعيين للوضع الافتراضي


def change_direction(e): #e=event
    #print(e)
    # print(e.keysym)    #only gives the key
    global velocityx , velocityy , game_over , paused  , wall_mode

    

    if(game_over):
        if e.keycode == 82 :  # 82     الرقم الفيزيائي  -r-كرمال مهما كانت لغة الكيبورد يطبق 
            reset_game()
            return
    if e.keycode == 32 : # spacebar
            paused = not paused
            return    
    if e.keycode == 87:       # W (تبديل وضع الجدران)
        wall_mode = not wall_mode
        return
    if paused: 
        return    
    
    if (e.keysym == "Up" and velocityy !=1 ):
        velocityx = 0
        velocityy = -1
    elif (e.keysym == "Down" and velocityy !=-1 ):
         velocityx = 0
         velocityy = 1
    elif (e.keysym == "Left" and velocityx !=1 ):
        velocityx = -1
        velocityy = 0
    elif (e.keysym == "Right" and velocityx !=-1 ):
        velocityx = 1
        velocityy = 0            

def move():
    global snake , food , snake_body , game_over , score , high_score , paused , wall_mode

    if (game_over or paused ):
        return
    
    #if (snake.x < 0 or snake.x >= WINDOW_WIDTH  or snake.y < 0 or snake.y >= WINDOW_HEIGHT):
    #    game_over = True
    #    return
    
    #التصادم مع الجسم 
    for tile in snake_body:
        if(snake.x == tile.x and snake.y == tile.y):
            game_over = True
            play_gameover_sound()
            return
    
    
    #اكل الطعام
    if (snake.x == food.x and snake.y == food.y):
        snake_body.append(Tile(food.x , food.y))
        play_eat_sound()
        # توليد طعام جديد في مكان فارغ
        while True:
            food_x = random.randint(0,COLS-1)* TILE_SIZE
            food_y = random.randint(0, ROWS-1)* TILE_SIZE
            collision = False    
            if snake.x == food_x and snake.y == food_y:
                collision = True
            else: 
                for tile in snake_body:
                    if tile.x == food_x and tile.y == food_y:
                        collision = True
                        break
            if not collision:
                food.x = food_x
                food.y = food_y
                break            
        
        score += 1

        if score > high_score:
            high_score = score
            with open("highscore.txt" , "w") as f :
                f.write(str(high_score))

        global delay
        delay = max(40 , 100 - score * 3) 
                     
    #update snake body
    for i in range(len(snake_body)-1 , -1 , -1):
        tile = snake_body[i]
        if (i==0):
            tile.x = snake.x
            tile.y = snake.y   
        else:
            prev_tile = snake_body[i-1]
            tile.x = prev_tile.x
            tile.y = prev_tile.y

    snake.x += velocityx * TILE_SIZE
    snake.y += velocityy * TILE_SIZE
     
    if wall_mode:
        # Wrap-around
        if snake.x < 0:
            snake.x = WINDOW_WIDTH - TILE_SIZE
        elif snake.x >= WINDOW_WIDTH:
            snake.x = 0
        if snake.y < 0:
            snake.y = WINDOW_HEIGHT - TILE_SIZE
        elif snake.y >= WINDOW_HEIGHT:
            snake.y = 0
    else:
        # الموت عند لمس الجدار
        if (snake.x < 0 or snake.x >= WINDOW_WIDTH or snake.y < 0 or snake.y >= WINDOW_HEIGHT):
            game_over = True
            play_gameover_sound()
            return

    


def draw():
    global snake , food , snake_body , game_over , score , delay , high_score , paused
    
    canvas.delete("all")   
    move()


    canvas.create_text(WINDOW_WIDTH - 80, 20, font="Arial 10", text=f"High: {high_score}", fill="gold")
           
    #draw food
    canvas.create_rectangle(food.x, food.y , food.x + TILE_SIZE, food.y + TILE_SIZE, fill = "red")

    #draw snake 
    canvas.create_rectangle(snake.x , snake.y , snake.x + TILE_SIZE, snake.y + TILE_SIZE, fill = "yellow")

    for tile in snake_body:
        canvas.create_rectangle(tile.x , tile.y , tile.x + TILE_SIZE , tile.y + TILE_SIZE , fill = "lime green")
    if(game_over):
        canvas.create_text(WINDOW_WIDTH/2 , WINDOW_HEIGHT/2 -20 , font = "Arial 20" , text = f"GAME OVER: {score}" , fill = "red")

        canvas.create_text(WINDOW_WIDTH/2 , WINDOW_HEIGHT/2 +20 , font = "Arial 14" , text= f"Press R to restart" , fill="white")
        
        canvas.create_text(WINDOW_WIDTH - 80, 20, font="Arial 10", text=f"High: {high_score}", fill="gold")

        canvas.create_text(30, 20, font="Arial 10",
                       text=f"Final score: {score}", fill="white")
    else:
       canvas.create_text( 30 ,20 ,font = "Arial 10" , text = f"score: {score}" , fill = "white")
       canvas.create_text(30, 40, font="Arial 8", text=f"Speed: {100/delay:.2f}x", fill="gray")
       canvas.create_text(30, 60, font="Arial 8", text="Space = Pause", fill="gray")
       mode_text = "Wrap" if wall_mode else "Wall Death"
       canvas.create_text(WINDOW_WIDTH - 80, 40, font="Arial 8", text=f"Mode: {mode_text}", fill="cyan")
       canvas.create_text(WINDOW_WIDTH - 80, 60, font="Arial 8", text="Press W to switch", fill="cyan")


    if paused and not game_over:
        canvas.create_text(WINDOW_WIDTH/2 , WINDOW_HEIGHT/2 , font="Arial 30" , text="PAUSED", fill="yellow")  


    Window.after(delay, draw) 

draw()

Window.bind("<KeyPress>" , change_direction ) 
Window.mainloop()

