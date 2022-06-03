# Imports
import os
import cv2
import numpy
import pyautogui
import mediapipe as mp
os.system('clear')

################################################### <Constants> ##########################################################

FPS = 30
WIDTH = 1280
HEIGHT = 720
SCORE = 0
LIVE = 5
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Paddle,Font and ball colors
PADDLE_COLOR = (0,255,0)
FONT_COLOR = (255,0,255)
BALLS_COLOR = (255,0,0)

# Paddle width and heights
PADDLE_WIDTH = 130
PADDLE_HEIGHT = 30

# Ball,Score and Live X-Y cordinates
BALLS_X_COR = int(WIDTH/2)
BALLS_Y_COR = int(HEIGHT/2)
SCORE_COR = (20,3*PADDLE_HEIGHT)
LIVE_COR = (WIDTH-250, 3*PADDLE_HEIGHT)

# Balls velocity and radius's 
BALLS_X_VELOCITY = 10
BALLS_Y_VELOCITY = 10
BALLS_RADIUS = 15

# Screen with and heights
SCREEN_SIZE = pyautogui.size()
SCREEN_WIDTH = SCREEN_SIZE[0]
SCREEN_HEIGHT = SCREEN_SIZE[1]

# My Camera object and its settings 
CAM = cv2.VideoCapture(1)
CAM.set(cv2.CAP_PROP_FRAME_WIDTH,WIDTH)
CAM.set(cv2.CAP_PROP_FRAME_HEIGHT,HEIGHT)
CAM.set(cv2.CAP_PROP_FPS,FPS)
CAM.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))

#################################################### </Constants> ##############################################################




class myHands:
    import mediapipe as mp
    def __init__(self,static_image_mode=False, max_num_hands=2, model_complexity=1,min_detection_confidence=0.5,min_tracking_confidence=0.5):
        self.static_image_mode=static_image_mode
        self.max_num_hands=max_num_hands
        self.model_complexity=model_complexity
        self.min_detection_confidence=min_detection_confidence
        self.min_tracking_confidence=min_tracking_confidence
        self.hands = self.mp.solutions.hands.Hands(self.static_image_mode,self.max_num_hands,self.model_complexity,self.min_detection_confidence,self.min_tracking_confidence)
        self.mpDraw = self.mp.solutions.drawing_utils


    def Marks(self,frame):
        myHands = list() # [[first_hand], [second_hand],[third_hand],[...],...]
        result = self.hands.process(frame)
        if (result.multi_hand_landmarks is not None):
            for hand in result.multi_hand_landmarks:
                myHand = list()
                for handLandMarks in hand.landmark:
                    myHand.append((int(handLandMarks.x * WIDTH),int(handLandMarks.y * HEIGHT)))
                myHands.append(myHand)
        return [myHands,result]


    def drawConnection(self,rgbFrame,bgrFrame):
        result = self.Marks(rgbFrame)[1]
        if result.multi_hand_landmarks is not None:
            for LandMarks in result.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(bgrFrame,LandMarks,self.mp.solutions.hands.HAND_CONNECTIONS)





# My Hands object
mpHands = myHands()

while True:
    isTrue,frame = CAM.read()

    if not(isTrue):
        break
    
    frame = cv2.flip(frame,1)
    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    myHands = mpHands.Marks(rgbFrame)
    cv2.circle(frame,(BALLS_X_COR,BALLS_Y_COR),BALLS_RADIUS,BALLS_COLOR,-1)
    cv2.putText(frame,str('Score: ' + str(SCORE)),SCORE_COR,FONT,2,FONT_COLOR,5)
    cv2.putText(frame,str('Lives: ' + str(LIVE)),LIVE_COR,FONT,2,FONT_COLOR,5)

    dot_x1_cor = 0
    dot_x2_cor = 10
    dot_y_cor = PADDLE_HEIGHT

    while dot_x1_cor <= WIDTH:
        cv2.line(frame,(dot_x1_cor,dot_y_cor),(dot_x2_cor,dot_y_cor),(255,255,255),1)
        dot_x1_cor = dot_x2_cor + 5
        dot_x2_cor += 10

    if len(myHands[0]) >= 1:
        for hand in myHands[0]:
            cv2.rectangle(frame,(int(hand[8][0] - PADDLE_WIDTH/2),0), (int(hand[8][0] + PADDLE_WIDTH/2),PADDLE_HEIGHT),(0,255,0),-1)   
            

    ballsTopYcor = BALLS_Y_COR - BALLS_RADIUS
    ballsBottomYcor = BALLS_Y_COR + BALLS_RADIUS
    ballsLeftXcor = BALLS_X_COR - BALLS_RADIUS
    ballsRightXcor = BALLS_X_COR + BALLS_RADIUS

    if ballsLeftXcor <= 0:
        BALLS_X_VELOCITY = BALLS_X_VELOCITY * (-1)

    if ballsRightXcor >= WIDTH:
        BALLS_X_VELOCITY = BALLS_X_VELOCITY * (-1)

    if ballsTopYcor <= PADDLE_HEIGHT:
        if ballsLeftXcor > hand[8][0] - int(PADDLE_WIDTH/2) and ballsRightXcor < hand[8][0]+PADDLE_WIDTH/2:
            BALLS_Y_VELOCITY = BALLS_Y_VELOCITY * (-1)
            SCORE += 1;

            # iNCREASING THE COMPLEXITY AT EACH OF THIS LEVELS 
            if SCORE == 5 or SCORE == 10 or SCORE == 15 or SCORE == 20:
                BALLS_X_VELOCITY *= 2
                BALLS_Y_VELOCITY *= 2

        else:
            LIVE = LIVE - 1
            BALLS_X_COR = int(WIDTH/2)
            BALLS_Y_COR = int(HEIGHT/2)

    if ballsBottomYcor > HEIGHT:
        BALLS_Y_VELOCITY = BALLS_Y_VELOCITY * (-1)


    BALLS_X_COR -= BALLS_X_VELOCITY
    BALLS_Y_COR -= BALLS_Y_VELOCITY

    # mpHands.drawConnection(rgbFrame,frame)
    cv2.imshow('Single Player Pong Game',frame)
    cv2.moveWindow('Single Player Pong Game',(SCREEN_WIDTH//2)-(WIDTH//2),(SCREEN_HEIGHT//2)-(HEIGHT//2))

    if cv2.waitKey(1) == ord('q') or LIVE == 0:
        break

CAM.release()


