import time
import random
from PIL import ImageDraw, ImageFont, Image
import pin_setting as setting

#wait button A press
class Repeat:
    def __init__(self):
        while True:
            if not setting.button_A.value:  
                break
        time.sleep(0.01)
  
#import tiltle image
class Open_title:
    def __init__(self):
        self.start = Image.open("/home/pi/work/imbedded_icw0207/start.png")
        self.game_over = Image.open("/home/pi/work/imbedded_icw0207/game_over.png")

class Background:
    def __init__(self):
        self.background_space = Image.open("/home/pi/work/imbedded_icw0207/background.png")

        
class U_cat:
    def __init__(self):
        #import image, UxU_cat that mean U-cat have mini cat imgage
        self.UxU_cat = Image.open("/home/pi/work/imbedded_icw0207/U_cat_with_mini_cat.png")
        self.U_cat = Image.open("/home/pi/work/imbedded_icw0207/U_cat.png")
        
        #start center of y
        self.y = 120
        # have_minicat that mean minicat status, 1 == have cat, 0 == shooted cat, -1 == lost cat
        self.have_minicat = 1
        
    def move_up(self):
        self.y -= 12
        if self.y < 0:
            self.y = 0
    
    def move_down(self):
        self.y += 12
        #don't go out of screen, 207 is 240(screen height) - 33(cat height)
        if self.y > 207:
            self.y = 207
            
    #snap minicat?        
    def select_cat_image(self):
        if (self.have_minicat == 1):
            return self.UxU_cat
        else:
            return self.U_cat

class Bullet:
    def __init__(self, u_cat_y):
      self.bullet = Image.open("/home/pi/work/imbedded_icw0207/bullet.png")
    
      #set initial coordi
      self.y = u_cat_y + 16 #center-y of u-cat
      self.x = 69 #U-cat width + 5
      
    def move_bullet(self):
      self.x += 10
    
    def check_touch_wall(self):
      #bullet touch screen right wall
      if self.x > 240:
          return 'touch_right_wall'
      else:
          return 0

class Minicat:
     def __init__(self):
         #import image head right and left
         self.mini_cat = Image.open("/home/pi/work/imbedded_icw0207/Mini_cat.png")
         self.mini_cat_left = Image.open("/home/pi/work/imbedded_icw0207/Mini_cat_left.png")
         
         #set initial coordi
         self.x = 74 #u_cat width + 5
         #mini cat can select direction Right or Left, so True = Right, False = Left
         self.direction = True
     
     def shoot(self, u_cat_y, have_minicat):
         #if button B pressed but U-cat don't have minicat
         if (have_minicat < 1) :
             return have_minicat
         
         self.y = u_cat_y
        
         #change player's have_minicat status
         return 0
        
     def move(self, u_cat_y, have_minicat):
         if (self.direction == True): #head right, go right
             self.x += 15
         else: #head left
             self.x -= 15
       
         #touch right wall
         if (self.x > 192):
             self.x = 192
             #turn left
             self.direction = False
            
         #touch U-cat
         if ((self.x < 64) and ((u_cat_y - self.y) < 21) and ((u_cat_y - self.y) > -33)):
             #return to U-cat and turn right
             self.direction = True
             return 1
        
         #touch left wall
         if (self.x < 0):
             #lost minicat
             return -1
            
         return 0
      
     def select_image_direction(self):
             if (self.direction == True):
                 return self.mini_cat
             else:
                 return self.mini_cat_left
             
#big Meteor
class Meteor:
      def __init__(self):
            #import image
            self.meteor = Image.open("/home/pi/work/imbedded_icw0207/Big_meteor.png")
            self.meteor_crack = Image.open("/home/pi/work/imbedded_icw0207/Big_meteor_crack.png")
            
            #set initial status
            self.y = random.randrange(0, 196) #196 is 240 - meteor height
            self.x = 196
            self.size = 54 #image size
            self.hp = 10

      def move(self):
            self.x -= 1
            
      def check_touch_wall(self):
            #if touch the left wall
            if (self.x < 0):
                return 1
            else:
                return 0
            
      def decrease_hp(self):
            self.hp -= 1

      #when big meteor broken, call two small meteors
      def append_meteor(self, meteor_size, meteor_list):
            #if broken meteor is small meteor, return same list
            if (meteor_size != 54):
                return meteor_list
            
            #appen meteors and return
            meteor_list.append(Small_meteor(True, self.x, self.y))
            meteor_list.append(Small_meteor(False, self.x, self.y))
            return meteor_list
        
      def select_image(self):
            if (self.hp > 5):
                return self.meteor
            else:
                return self.meteor_crack

class Small_meteor(Meteor):
      def __init__(self, direction, big_meteor_x, big_meteor_y):
            self.meteor = Image.open("/home/pi/work/imbedded_icw0207/Small_meteor.png")
            self.meteor_crack = Image.open("/home/pi/work/imbedded_icw0207/Small_meteor_crack.png")
            
            #set initial status
            self.x = big_meteor_x + 5
            self.size = 34
            self.hp = 5
            
            #direction True == up, False == down
            if (direction == True):
                self.y = big_meteor_y - 30
                self.direction = True
            else:
                self.y = big_meteor_y + 5
                self.direction = False
           
      def move(self):
            self.x -= 2
            
            if (self.direction == True):
                self.y -= 2
            else:
                self.y += 2
                
      def check_touch_wall(self):
            #if touch the left wall
            if (self.x < 0):
                return 'touch_left_wall'
            
            #if touch roof
            if (self.y < 0):
                self.direction = False
                self.y = 0
                
            #if touch bottom
            if (self.y > 206):
                self.direction = True
                self.y = 206
                
            return 0
       
      def select_image(self):
            if (self.hp > 3):
                return self.meteor
            else:
                return self.meteor_crack
    
class Check_crash:
      def check_crash_cat_and_meteor(self, cat_image, meteor_size, cat_y, meteor_x, meteor_y):
          if ((cat_image.width > meteor_x) and
              (cat_y + cat_image.height > meteor_y) and (meteor_y + meteor_size > cat_y)):
                return 'gameover'
          else:
                return 0
            
      def check_crash_bullet_and_meteor(self, meteor_size, bullet_x, bullet_y, meteor_x, meteor_y):
          if ((bullet_x + 4 > meteor_x) and (bullet_x < meteor_x + meteor_size) and
             (bullet_y + 4 > meteor_y) and (bullet_y < meteor_y + meteor_size)):
                return 'crash'
          else:
                return 0
            
      def check_crash_minicat_and_meteor(self, meteor_size, minicat_direction, minicat_x, minicat_y, meteor_x, meteor_y):
          #check y-boundary
          if (meteor_y < minicat_y + 11 < meteor_y + meteor_size):
                #minicat head right and hit meteor
                if ((minicat_direction == True) and (meteor_x < minicat_x + 48 < meteor_x + meteor_size)):
                    return 1
                #minicat head left and hit meteor
                if ((minicat_direction == False) and (meteor_x < minicat_x < meteor_x + meteor_size)):
                    return 1
          return 0      
