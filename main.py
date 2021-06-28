import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import ImageDraw, ImageFont, Image
import adafruit_rgb_display.st7789 as st7789

import pin_setting as setting
from classes import Open_title, Background, U_cat, Bullet, Minicat, Meteor, Small_meteor, Check_crash, Repeat, delete_trash

# Create the display
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000
fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
spi = board.SPI()

disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for color.
width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Set variables
score = 0
game_over = 0
player = U_cat()
minicat = Minicat()
check_crash = Check_crash()
bullets = []
meteors = []
have_to_delete_bullets = []
have_to_delete_meteors = []
meteor_apper_random_time_cycle = 0
time_last_meteor_appear = 0

#Open title image
image.paste(Open_title().start, (0, 0))
disp.image(image)

#left pressed(button A), start game
Repeat()
 
#~START GAME~
while True:
    
    #~CHECK BUTTON PRESS~
    if not setting.button_U.value:  # up pressed, move U-cat
        player.move_up()

    if not setting.button_D.value:  # down pressed, move U-cat
        player.move_down()
     
    if not setting.button_A.value:  # left pressed(button A), shoot bullet
        bullets.append(Bullet(player.y))
     
    if not setting.button_B.value:  # left pressed(button B), shoot Mini-cat
        #shoot and change player's have_minicat status
        player.have_minicat = minicat.shoot(player.y, player.have_minicat)
        
        
    #~Call meteors random time cycle~
    if (meteor_apper_random_time_cycle < (time.time() - time_last_meteor_appear)):
        meteors.append(Meteor())
        time_last_meteor_appear = time.time()
        #cycle go faster with score higher
        meteor_apper_random_time_cycle = random.randrange(5 - int(score / 100), 10 - int(score / 100))
    
    
    #~MOVING~
    #if minicat shooted, move minicat and change player's have_minicat status
    if (player.have_minicat == 0):
        player.have_minicat = minicat.move(player.y, player.have_minicat)
    
    #move meteors and check meteor touch wall or cat(game over)
    for j in range(len(meteors)):
        meteors[j].move()
        
        #if meteor touch right wall, delete that meteor
        if (meteors[j].check_touch_wall()):
            have_to_delete_meteors.append(j)
            continue
            
        if (check_crash.check_crash_cat_and_meteor(player.select_cat_image(), meteors[j].size, player.y, meteors[j].x, meteors[j].y)):
            game_over = 1
            break
    
    #move bullets and check bullet touch wall
    for i in range(len(bullets)):
        bullets[i].move_bullet()
        
        #if bullet touch right wall, delete that bullet
        if (bullets[i].check_touch_wall()):
            have_to_delete_bullets.append(i)
            
    #delete trash data that touch wall     
    have_to_delete_bullets = delete_trash(bullets, have_to_delete_bullets)
    have_to_delete_meteors = delete_trash(meteors, have_to_delete_meteors)
    
    #~CHECK CHASH~
    #check bullets and meteors
    for i in range(len(bullets)):
        for j in range(len(meteors)):
            #if bullet hit meteor, score up and delete that bullet
            if (check_crash.check_crash_bullet_and_meteor(meteors[j].size, bullets[i].x, bullets[i].y, meteors[j].x, meteors[j].y)):
                meteors[j].decrease_hp()
                score += 1
                have_to_delete_bullets.append(i)
                
                #if bullet break meteor, score up and delete that meteor
                if (meteors[j].hp == 0):
                    have_to_delete_meteors.append(j)
                    score += 10
                    
                    #if broken meteor is big meteor, call two small meteors
                    meteors = meteors[j].append_meteor(meteors[j].size, meteors)
    
    #check minicat and meteors
    if (player.have_minicat == 0):
        for j in range(len(meteors)):
            
            #if minicat hit meteor, score up and delete that meteor
            if (check_crash.check_crash_minicat_and_meteor(meteors[j].size, minicat.direction, minicat.x, minicat.y, meteors[j].x, meteors[j].y)):
                have_to_delete_meteors.append(j)
                score += 10
                
                #if broken meteor is big meteor, call two small meteors
                meteors = meteors[j].append_meteor(meteors[j].size, meteors)
    
    #delete trash data (broken meteors, bullets ... that created by crash)
    have_to_delete_bullets = delete_trash(bullets, have_to_delete_bullets)
    have_to_delete_meteors = delete_trash(meteors, have_to_delete_meteors)
    
    
    #~DRAWING~
    #draw background
    image.paste(Background().background_space, (0, 0))
    
    #meteors
    for j in meteors:
        image.paste(j.select_image(), (j.x, j.y), j.select_image())
        
    #bullets
    for i in bullets:
        image.paste(i.bullet, (i.x, i.y), i.bullet)
        
    #player
    image.paste(player.select_cat_image(), (5, player.y), player.select_cat_image())
    
    #minicat (if minicat shooted)
    if (player.have_minicat == 0):
        image.paste(minicat.select_image_direction(), (minicat.x, minicat.y), minicat.select_image_direction())
    
    
    #~GAME OVER~
    if (game_over == 1):
        #draw game over image
        image.paste(Open_title().game_over, (0, 0))
        draw.text((85, 120), str(score), font=fnt, fill="#FFFFFF")
        disp.image(image)
        
        #reset variables
        score = 0
        game_over = 0
        player = U_cat()
        minicat = Minicat()
        check_crash = Check_crash()
        bullets = []
        meteors = []
        have_to_delete_bullets = []
        have_to_delete_meteors = []
        meteor_apper_random_time_cycle = 0
        time_last_meteor_appear = 0
        
        #wait button A press
        Repeat()
        
        
    #Display the Image
    disp.image(image)
    
    time.sleep(0.01)
