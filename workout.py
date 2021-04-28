''' (c) Winona Richey 2020
This is intened to be a FREE workout generator and robot personal trainer
I HIGHLY encourage the user to edit/customize these exercises to suit your needs/preferences!
Some ideas of how you can customize: 
 - Add/remove exercises based on your preferences and available equipment 
     - don't forget that there's options to switch, jump, pulse, etc.
 - change the duration time = scale_factor *x (changes the proportion of time relative to other exercises)
 - edit the robot text to add descriptors for exercises you forget often!
 - change your workout length, the number of times you want to repeat a circuit, the number of circuits 

 
This code has been tested on Mac only (sorry)
''' 
import subprocess
import random
from datetime import datetime
import time
import math
import sys, tty

#for windows: import pyttsx3

from pynput import keyboard

#if you run into trouble with the substitute feature using pynput
# 1) https://stackoverflow.com/questions/53088995/pynput-keyboard-listener-does-not-detect-keys-on-mac-os-x
# 2) install keyboard instead and implement the substitute feature (esp for windows)
# 3) fore-go the substitue feature and live your life at the mercy of RoboTrainer
# 4) fix it another way and let me know how


'''---------------------------------------------user defined variables---------------------------------------------'''

muscle_groups = [1, 1, 1, 1] # abs, legs, arms, cardio;
                          # 1 = muscle group included
                          # 0 = muscle group excluded
                          
desired_time = 25 # this is an approximate MINIMUM time.
                  # your workout is guaranteed to be LONGER than this time, likely by 3-10 minutes...
                  # If you want more specific workout lengths... have fun updating this code

repeats = [3,2]   # number of times circuits repeat
                  # e.g. [number of times circuit 1 repeats,
                  #       number of times circuit 2 repeats.. etc.]
                  # to add circuits simply increase the length of this list... 
                  # i.e. three circuits that are each repeated twie => repeats = [2,2,2]

x = 10            # units in seconds
                  # decides length of each exercise;
                  # exrecise times range from x to 4x
''' x allows exercises to be long or short relative to each other, without all being the same length
                  the default time for an exercise is 4*x, but more difficult/strenuous exercises are scaled down
                  (i.e. the exercise object is created with time = 2*x)

                  To scale the difficulty of an exercise, scroll down to the exercise object initializations'''
                  #note: you will run into problems if you set x to some ridiculously small value such that you 
                  #      run out of unique exercises to fill up your time... 
                  #      i.e. either (1) make sure there's enough exercises to fill your desired time with unique
                  #                      options OR
                  #                  (2) comment out the uniqueness check (repeat_check) 

resttime = 0      # units in seconds
                  # length of rest between exercises
stretchtime = 0#.5  # units in minutes
                  # length of time designated for stretching in the beginning of the workout
operating_system = 'Mac' #if this isn't 'Mac', make sure you import pyttsx3

global substitutionON
substitutionON = True   #On = a separate thread will listen for a keypress, keypresses will swap out the current exercise
                      #     for another exercise of the same type. It listens in all windows!
                      #     --> Use the ESC key to toggle the substitution functionality on/off mid-program 
                      # Off = you live your life at the mercy of robo trainer. The generated workout is written in stone
     
''' ------------------------------------------ Exercise object initializations--------------------------------------------'''    

class exercise():
    ''' exercises are stored as objects; create your own exercise by
        exercise('What RoboTrainer Will Call Your Exercise', time = x*intensity_scale_fator) '''
    def __init__(self,word,time=4*x,switch=0,jump=0,pulse=0,tapmix=0,fastfeet=0):
        self.word = word            # string that the robot will voice when the exercise comes up
        self.time = time            # length that you'll have to do the exercise each time it comes up

        #bool (or binary) atributes that control commands given halfway through the exercise 
        self.switch = switch        # True if an exercise that requires you to switch sides (do on the Left, then on the Right)
        self.jump = jump            # True if an exercise can have a jump added (e.g. squat)
        self.pulse = pulse          # True if an exercise can be "pulsed" (e.g squat)
        self.tapmix = tapmix        # True if an exercise can have hand taps/shoulder taps/hip taps etc. (e.g. high plank) 
        self.fastfeet = fastfeet    # True if an exercise can have fastfeet added to it (e.g. shaddowboxing)

#Cardio
cardio_options = [exercise('jumping jacks'), exercise('toe touches on the bag'),
                  exercise('high knees'), exercise('butt kickers'),exercise('jog in place'),
                  exercise('burpees',jump=1), exercise('tuck jumps'), exercise('shaddowboxing',fastfeet=1, pulse = 1),
                  exercise('froggies',jump=1),exercise('jump rope'), exercise('Skip in place'),
                  exercise('plank jacks',3*x), exercise('lateral hops'),
                  exercise('Forward backward hop'), exercise('in and out fast feet'),
                  exercise('sprinter skip. runners lunge into a skip',switch=1), exercise('jumping mountain climbers'),
                  exercise('low box step ups. Keep it speedy!!',switch=1)]

#abs
ab_options = [exercise('jack knives',2*x), exercise('bicycle crunches',2*x), exercise('elbow plank',2*x),
              exercise('hollow hold',2*x),exercise('side planks',switch=1), exercise('standing knee to opposite elbow'),
              exercise('oblique crunches. bend your leg and put ankle on opposite knee. twist to get elbow to bent knee',switch=1),
              exercise('leg raises'), exercise('v ups'), exercise('russian twists'), exercise('superman'),
              exercise('knee raises. get on the floor basically half a jack knife'), exercise('flutter kicks'),
              exercise('x ups. from the floor, arm to opposite leg lift'),  exercise('windshield wipers'), 
              exercise('twisting mountain climbers',2*x),exercise('giant mountain climbers'),
              exercise('scissor crossover kick'), exercise('mountain climbers',2*x)]#,
              #exercises that require TRX
              #exercise('TRX suspended side plank',4*x,switch=1),
              #exercise('TRX crunch. feet in straps. lie on your back. lift your hips off the ground'),]

#Legs          
leg_options = [exercise('courtsey squats',jump=1),exercise('lunges',jump=1,pulse=1),exercise('air squats',jump=1,pulse=1),
               exercise('wall sit'), exercise('step ups',switch=1),exercise('hip bridges',pulse=1),
               exercise('bird dog. arm leg simultaneous extension',pulse=1), exercise('yoga squat'),
               exercise('in and out squats',jump =1), exercise('single leg lateral hop',switch=1),
               exercise('lateral lunges or squats'),exercise('calf raises',2*x),exercise('front kicks'),exercise('side kicks'),
               exercise('Lying leg lifts, on your side. Add resistance bands for a challenge',switch=1),
               exercise('super skaters. don\'t touch down back foot, then raise it to chest', jump=1),
               exercise('single leg deadlift',3*x), 
               #exercises that require resistance bands
               exercise('resistance bands standing kick back',switch=1), exercise('Resistance bands hamstring curl', switch=1),
               exercise('Resistance bands standing lateral leg raise',switch = 1), exercise('Resistance Bands lateral walk'),
               #exercises that require TRX
               exercise('TRX suspended lunge',4*x,switch=1),exercise('TRX pistol squat',switch = 1)]

arm_options = [exercise('wide arm pushups',3*x), exercise('tricep dips',2*x), exercise('walkout pushups'),
               exercise('tricep pushups',2*x), exercise('tin soldier pushups',x), exercise('shoulder tap pushups',x), 
               exercise('rotation push up'), exercise('high plank',2*x), exercise('plank with alternating hand taps',tapmix=1),
               #exercises that require resitance bands
               exercise('Resistance bands arm pull apart',3*x),exercise('Resistance bands hammer curl up',3*x),
               exercise('Resistnace bands tricep overhead extension',3*x,switch=1),               
               exercise('resistance bands bent over row'), exercise('Resistance bands lateral plank walk'),
               exercise('Resistance bands kneeling one arm row',switch =1),exercise('Resistance bands. Arm pull down'),
               #exercises that requrie TRX
               exercise('TRX deltoid or chest fly. Face away from door',3*x), exercise('TRX bicep curls',2*x),
               exercise('TRX chest presses or pushups'),exercise('TRX tricep extension'), exercise('TRX rowers'), 
               #exercise('TRX reverse crunch',3*x), exercise('TRX plank')]
               #exercise that require dumbells
               exercise('shoulder presses with dumbells')]

'''---------------------------------------------end user variables---------------------------------------------'''
#global variables initialized for substitution functionality 
#  these variables are used to swap out the current exercise for a different UNIQUE exercise
global c_index, current_index,interlude, cardio_inds, ab_inds, leg_inds, arm_inds 

#initialize the py text to speach robot voice
if operating_system != 'Mac':
    print('initializing pyttsx3')
    voice = pyttsx3.init()
    voice.setProperty('volume',.8)

def speak(voicestr):
    ''' uses the operating system voice to give command (text to speach)
    input:
        voicestr: string that you want the robot to say
    '''
    if operating_system == 'Mac':
        subprocess.call(["say", voicestr])
    else:
        voice.say(voicestr)
        voice.runAndWait()
    return


def circuit(ex):
    ''' plays/runs through the circuit one time (timer + robot voice);
        here is where the spice gets added during the workout (added bonus commands)
        no output, just timed calls to robot voice
        
       input: ex = LIST of exercise objects for ONE circuit (repeats happen outside this function)   
    '''
    global current_index
    t1 = 0 #time 
    current_index = -1
    while current_index < len(ex):

        #say keep pushing if it's at least the first exercise AND
        # you're allowing time for a rest between exercises OR it's the last exercies of the circuit 
        # AND  you're 9 seconds away from the end (it takes him ~9 seconds to say this phrase)
        if current_index>0 and (resttime>0 or current_index==(len(ex)-1)) and (time.time()-t1> ex[current_index].time-9):
            speak('Keep pushing. Three. -. -. -. Two. -. -. -. One. -. -. -. Done')

        #if it's the first exercise OR it's time for a new exercise announcment, 
        # 7 is the length of time between him starting to say "Get Ready..." and "Ready. Set. Go"
        # i.e. 7 should ideally be the time it actually takes him to say the exercise, but that's impossible to do right now. 
        if current_index<0 or (time.time()-t1> ex[current_index].time-7):
            if current_index==(len(ex)-1):
                break

            #reset all the variables we're using to keep track of where we are in the workout
            halfway = 0
            #started = 0
            current_index +=1
            speak('Get ready for '+ex[current_index].word)
            print(ex[current_index].word)
            while (time.time()-t1)< ex[current_index-1].time:
              pass
            speak('Ready. -. -.  Set. -. -.   Go')
            t1 = time.time()
        
        #if the exrcise is more than halfway over, add spice
        if time.time()-t1 >ex[current_index].time/2+resttime and not halfway:
            halfway = 1            
            if ex[current_index].switch:
                #this is an exercise that requires the athlete to switch side
                speak('Switch sides!')
            elif ex[current_index].time<=30:
                #when the exercise time is long, it's discouraging to hear that you're only halfway
                #only say this when the exercise time is short
                speak('Halfway. Keep going')

            #for added difficulty, there are additional options
            #that can be added halfway through the exercise
            
            if ex[current_index].fastfeet:
                if random.randint(0,1):#50/50 chance of adding a jump
                    speak('Add in fast feet.')
                
            if ex[current_index].jump:
                #this is an exercise that can have a jump added
                if random.randint(0,1): #50/50 chance of adding a jump
                    speak('Add a jump!')
                    
            if ex[current_index].pulse:
                #this is an exercise that can be "pulsed"
                if random.randint(0,1):#50/50 chance of adding a pulse
                    speak('For extra burn, Pulse it out!!')
                    
            if ex[current_index].tapmix:
                opt = ['elbows', 'shoulders', 'hips', 'knees', 'toes']
                speak('Mix it up with taps on ' +opt[random.randint(0,4)])       


def choose(exercises,inds,split):
    ''' splits the full list of exercises in the workout into the given # of circuits (m+1)
    input:
        exercises = LSIT of exercise objects (1xn),
        inds = LIST of indices of all selected exercises (1xn)
        split = LIST of indices where you're cutting these lists (1 x m where m=# of circuits-1)
    output:
        exercise_list_of_lists = list of circuit lists (1xnxm)
    '''
    split.append(len(inds)) #last split ends at end of indices
    words_chosen = [exercises[i] for i in inds]
    start = 0
    end = split[0]
    exercise_list_of_lists=[] #initialize
    for s in range(len(split)):
        exercise_list_of_lists.append(words_chosen[start:split[s]])
        start = split[s]
    return exercise_list_of_lists

def add_unique_index(len_options,indices):
    ''' selects a new index that hasn't already been chosen, adds it to the list of selected indices
    input:
        len_options: INT; the length of the list of options (i.e. the number of possible integers)
        indices: LIST of INTs; list of already selected indices
    output:
        indices: LIST of INTS with newly selected (ALL UNIQUE) index appended
    '''
    x = random.randint(1,len_options) 
    while x in indices:
        x = random.randint(1,len_options)#x = random.sample(range(len_options),1)
    indices.append(x)
    return indices
 
def substitute():
    #figure out where in the workout you are

    #we don't anticipate having to skip a lot, so just look for where that exercise occurs
    if c_index == -1:
      #in cardio_chosen
      current_circuit = cardio_chosen
      options = cardio_options
      inds = cardio_inds
    else:
      #in a regular circuit... need to figure out the details
      if interlude_Flag:
        current_circuit = interlude[c_index]
        options = cardio_options
        inds = cardio_inds
      else:
        current_circuit = circuits[c_index]

        #the current exercise:
        ex = current_circuit[current_index]
        if ex in leg_options:
          options = leg_options
          inds = leg_inds
        elif ex in arm_options:
          options = arm_options
          inds = arm_inds
        else:
          options= ab_options
          inds = ab_inds

    ex = current_circuit[current_index]
    print('Replacing %s' %ex.word)
    new_inds = add_unique_index(len(options)-1, inds)
    new_ex = options[new_inds[-1]]
    
    #swap this new exercise into the current circuit
    current_circuit[current_index] = new_ex

    #substitute current exercise with something else from that category
    speak('OK. Instead, do %s' %new_ex.word)
    print('\t-->%s' %new_ex.word)
    return

def on_press(key):
    global substitutionON
    if c_index <-1:
        return

    #this allows you to turn listning off so you can type while the workout is going
    #without skipping a million exercises
    if key == keyboard.Key.esc:
      substitutionON =  not substitutionON 
      print('SubstitutionON: %s' %substitutionON)
      return
    if substitutionON == False:
      return

    substitute()
    ''' #you can use this to see what a key is called 
    #if you want to implement a new keypress functionality
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))'''

if substitutionON:
  listener = keyboard.Listener(on_press=on_press)
  listener.start()  # start to listen on a separate thread
  #listener.join()  # remove if main thread is polling self.keys
  c_index = -2
  interlude_Flag = False

#initialize the random seed with today's date
# to reduce day-to-day similarities
random.seed(datetime.now())


#beginning sequence
speak('I am proud of you for showing up today! Let\'s get ready to SWEAT!')
speak('Take '+ str(stretchtime) +' minutes to stretch what you need')

#compute exercises
total_time = 0
cardio_inds = []
ab_inds = []
leg_inds = []
arm_inds = []

while total_time < desired_time:
    #print('\n\n\n\n')
    if muscle_groups[0]:
        ab_inds = add_unique_index(len(ab_options)-1, ab_inds)
    if muscle_groups[1]:
        leg_inds = add_unique_index(len(leg_options)-1, leg_inds)
    if muscle_groups[2]:
        arm_inds = add_unique_index(len(arm_options)-1, arm_inds)
    if muscle_groups[3]:
        cardio_inds = add_unique_index(len(cardio_options)-1, cardio_inds)

    
    if len(leg_inds)<2:
        split = [0]
        #technically this might be inefficient but if you're actually
        #DOING a circuit with only 3 exercises in it you deserve inefficiency
    else:
        # we want to make a list that tells us where to break the big list into circuits
        split = []
        for r in range(1,len(repeats)):
            split.append(math.ceil(len(ab_inds)*r/len(repeats)))
    
    #build circuits
    cardio_chosen = [cardio_options[i] for i in cardio_inds]
    l_ls= choose(leg_options,leg_inds,split)
    ab_ls = choose(ab_options,ab_inds,split)
    a_ls = choose(arm_options,arm_inds,split)

    #start summing the time,
    rests = resttime
    old_time = total_time
    total_time =30 #this is how long the motivational stuff takes to say out loud. 
    cardio_times = [x.time for x in cardio_chosen]
    total_time = sum(cardio_times) #time it takes for cardio intro
    
    #re-initialize --
    circuits = []
    interlude = []
    for c in range(len(repeats)): #for each circuit
        #put legs, abs and arms in the circuit
        c1 = l_ls[c]
        [c1.append(i) for i in ab_ls[c]]
        [c1.append(i) for i in a_ls[c]]
        circuits.append(c1)

        #put together a cardio interlude of 2 random exercises
        i1 =random.randint(0, len(cardio_options)-1)
        i2 = random.randint(0, len(cardio_options)-1)
        interlude.append([cardio_options[i1], cardio_options[i2]])
        
        #compute the time for the circuit
        c1_time =0
        c1_times =[x.time for x in c1]        
        interlude_time =0
        interlude_times=[x.time for x in interlude[c]]
        
        # time for the circuit * # of times circuit repeats + time for the interlude cardio + time for rests between exercises
        total_time += sum(c1_times)*repeats[c] +              sum(interlude_times)          + rests*(len(c1)*repeats[c]+2)

    total_time = total_time/60
    if total_time == old_time: #no change, break loop
        break

#this should never happen. if it does the add unique is broken. 
repeat_check = int(len(set(cardio_inds)) != len(cardio_inds)) + int(len(set(leg_inds)) != len(leg_inds)) +int(len(set(ab_inds)) != len(ab_inds)) +int(len(set(arm_inds)) != len(arm_inds))
if repeat_check:
    speak('Hope you are ok with repeating an exercise, because you gotta.')


print('Made a workout', total_time, 'minutes long')
speak('Made a workout approximately %d minutes long' %math.ceil(total_time))

time.sleep(60*stretchtime)

speak('Get ready to rumble!')
speak('Let\'s do this thang!!')

#every workout has cardio
#warmup
if len(cardio_chosen)>0:
    c_index = -1
    circuit(cardio_chosen)

#main circuits
start_time = time.time()
for c_index in range(len(repeats)): #for each circuit
    this_circuit_exercises = circuits[c_index]
    if len(this_circuit_exercises)>0:
      for r in range(repeats[c_index]): #repeat the circuit
          circuit(this_circuit_exercises)


    if len(interlude[c_index])>0:
      if c_index == len(circuits)-1:
          speak('Last two exercises! Almost there! push through.')
      elif (time.time()-start_time)/60 > total_time/2:
          speak('More than halfway through the workout!')
      
      #do the interlude cardio exercises
      interlude_Flag=True     #handle the interlude flag for substitution purposes     
      circuit(interlude[c_index]) 
      interlude_Flag=False 

      if c_index != len(circuits)-1:
          speak('Onto the next circuit! ')
    
real_elapsed_time = (time.time()-start_time)/60
            
speak('Workout Complete! You did it.')
speak('Workout was  %.02f minutes ' %real_elapsed_time)


print('Predicted a workout %.02f minutes long' %total_time)
print('Workout Time: %.02f minutes ' %real_elapsed_time)

#TODO: 
# - substitution voice in separate thread currently just screams over the main thread's voice
