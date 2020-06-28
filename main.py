import math
import time
import pickle

# Used for infection calculations
population = 4676000

# Has the game been lost
gameEnd = False

# Used for display purposes
daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# Game variables to be saved
class SimulationVars:
    def __init__(self):
        self.cases = 0 # Total number of cases
        
        # Active cases for each past week. First element is current week, second is 1 week ago, etc.
        # After 6 weeks all cases will recover
        self.activeCases = [10,0,0,0,0,0,0]
        
        # Total number of deaths
        self.deaths = 0
        
        # Number of recovered cases
        self.recoveredCases = 0
        
        # The people's happiness
        self.happiness = 100.0
        
        # Current alert level
        self.alertLevel = 1
        
        # The current date
        self.dayOfMonth = 1
        self.month = 0
        self.year = 2020
        
        # Used for the display at the end of the game.
        self.weeksAtLevel = [0,0,0,0]

# Base rates for infection calculations.
baseDeathRate = 2
baseRecoveryRate = 20


# Return the total number of active cases.
def getActiveCases():
    global simVars
    
    cases = 0
    for num in simVars.activeCases:
        cases += num
    return cases

# Return the total number of cases there have been.
def getTotalCases():
    global simVars
    
    return getActiveCases() + simVars.deaths + simVars.recoveredCases

# For a specific number of cases, determine how many people die, recover, or stay ill.
def handleActiveCases(amount, weeksOld):
    global simVars

    deathRate = baseDeathRate - 0.3*weeksOld # From 2% for new cases to 0.5% for 5 week old cases
    recoveryRate = baseRecoveryRate + 12*weeksOld # From 20% for new cases to 80% for 5 week old cases
    
    # Calculate number of deaths
    newDeaths = math.floor(amount * (deathRate / 100.0))
    simVars.deaths += newDeaths
    amount -= newDeaths
    
    # Calculate number of recoveries
    recoveries = math.floor(amount * (recoveryRate / 100.0))
    simVars.recoveredCases += recoveries
    return amount - recoveries # Return remaining number of active cases

# Update the stack of active cases sorted by age.
def updateActiveCases(newAmount): 
    global simVars
    
    for i in range(6,-1,-1): # Iterate from 6 to 0 inclusive
        if i == 6:
            simVars.recoveredCases += simVars.activeCases[i] # All cases that are 6 weeks old will recover
        else:
            remainingCases = handleActiveCases(simVars.activeCases[i], i) # Calculate deaths and recoveries
            simVars.activeCases[i+1] = remainingCases # Move remaining cases further up the list as they are older
            
    simVars.activeCases[0] = newAmount # Add current cases


# Find the number of new cases in a week.
def getNewInfected():
    global simVars
    
    activeCases = simVars.activeCases[0] + simVars.activeCases[1]
    # Exponential model, proportional to total infected and total susceptible.
    # Because COVID-19 can be gotten multiple times, people who have recovered are still susceptible.
    newInfected = (activeCases/population) * ((population - activeCases)/population) * population
    
    # Adjust new cases based on the current alert level.
    if simVars.alertLevel == 2:
        newInfected *= 0.5
    elif simVars.alertLevel == 3:
        newInfected *= 0.2
    elif simVars.alertLevel == 4:
        newInfected *= 0.05
    
    return math.floor(newInfected)

# Increment the time tracker by a week.
def changeWeek():
    global simVars
    
    simVars.dayOfMonth += 7
    
    if simVars.dayOfMonth > daysInMonths[simVars.month]: # Gone past end of month
        simVars.dayOfMonth -= daysInMonths[simVars.month]
        simVars.month += 1

        if simVars.month > 11: # Gone past end of year
            simVars.month = 0
            simVars.year += 1

# Turn the date variables into a formatted string displaying the date.
def getDateDisplay():
    global simVars
    
    # Determine suffix for ordinal number.
    if simVars.dayOfMonth in (1,21,31):
        suffix = "st"
    elif simVars.dayOfMonth in (2,22):
        suffix = "nd"
    elif simVars.dayOfMonth in (3,23):
        suffix = "rd"
    else:
        suffix = "th"
        
    return "%d%s %s %d" % (simVars.dayOfMonth, suffix, months[simVars.month], simVars.year)

# Print the header at the start of every week, including case info
def printWeekHeader(newCases, newDeaths):
    global simVars
    
    print()
    print('========= %s =========' % getDateDisplay())
    print("--- ALERT LEVEL %d ---" % simVars.alertLevel)
    if newCases is not None: print("In the past week, there have been %d new cases and %d deaths." % (newCases, newDeaths))
    print()
    print("Total cases: %d" % getTotalCases())
    print("Total active cases: %d" % getActiveCases())
    print("Total deaths: %d" % simVars.deaths)
    print("People's happiness: %.1f%%" % simVars.happiness)

# Fetch an integer with a check for other data types.
def getInt(string):
    loop = True
    while loop:
        answer = input(string)
        try:
            return int(answer)
        except ValueError:
            print("Please enter an integer.")

# Command: Progress the simulation one week.
def progressWeek():
    global simVars, gameEnd
    
    changeWeek()
    newCases = getNewInfected()
    oldDeaths = simVars.deaths
    updateActiveCases(newCases)
   
    # Update people's happiness based on the alert level they are staying at.
    if simVars.alertLevel == 2:
        simVars.happiness -= 1
    elif simVars.alertLevel == 3:
        simVars.happiness -= 5
    elif simVars.alertLevel == 4:
        simVars.happiness -= 10
        
    # Cap happiness at 100%
    if simVars.happiness > 100:
        simVars.happiness = 100
    
    # Check if the game has been lost.
    if simVars.happiness <= 0:
        gameEnd = True
    elif simVars.deaths >= 1000:
        gameEnd = True
    else:
        newDeaths = simVars.deaths - oldDeaths
        simVars.weeksAtLevel[simVars.alertLevel - 1] += 1
        printWeekHeader(newCases, newDeaths)

# Command: Save the game's progress.
def saveProgress():
    global simVars
    
    # Use a Pickle object to save the entire class to a file for easy retrieval.
    p = pickle.Pickler(open("progress.dat", "wb"))
    p.dump(simVars)
    print("Progress saved.")

# Command: Check details of cases.
def checkDetails():
    global simVars
    
    print('New cases: %d' % simVars.activeCases[0])
    for i in range(1,6):
        print('%d week old cases: %d' % (i, simVars.activeCases[i]))
    print('Recovered cases: %d' % simVars.recoveredCases)
    print('Deaths: %d' % simVars.deaths)

# Command: Change the current alert level.
def changeAlertLevel():
    global simVars
    print("Switch to which alert level? (1 - 4)")
    
    while 1: 
        ans = getInt(">>> ")
        if ans < 1 or ans > 4: # If answer is out of range, ask again.
            print("Answer out of range.")
        else:
            # Check if the conditions are met for switching to higher alert levels.
            if ans == 3 and getTotalCases() < 100:
                print("Too early to switch to Level 3! (Cases should be over 100)")
            elif ans == 4 and getTotalCases() < 200:
                print("Too early to switch to Level 4! (Cases should be over 200)")
            elif ans == simVars.alertLevel:
                print("You were already at alert level %d." % ans)
            else:
                print("Switched to alert level %d." % ans)
                simVars.alertLevel = ans
            return

# The main loop of the program.
def mainLoop():
    # Print options
    print('''
A - Change alert level
S - Save progress
C - Check details on active cases
P - Progress to the next week''')
    
    # Check options
    cmd = input(">>> ")
    if cmd.upper() == "A":
        changeAlertLevel()
    elif cmd.upper() == "S":
        saveProgress()
    elif cmd.upper() == "C":
        checkDetails()
    elif cmd.upper() == "P":
        progressWeek()
    else:
        print("Invalid command.")

# Intro text
print('''
===== Welcome to CoronaSim! =====

The country of New Zealand has just had its first few recorded cases of COVID-19
coming in from the border. As the Director General of Health, you must guide the
country to make sure the pandemic doesn't get out of hand!

You lose when happiness hits 0% or deaths rise above 1,000.
You win when there are no active cases.

Important info:
* You cannot raise the alert level too high when cases are too low.
* At alert level 1, happiness will increase, so it is worth using alert level 1 sometimes.
* Happiness will decrease faster the higher the alert level is.

DISCLAIMER: This program is for entertainment purposes only. It is not meant
to provide an accurate simulation of COVID-19. The values and algorithms used in this
program are not representative of statistics in the real world.

Would you like to load a previous game? (y/n)''')

# Check to load a game
ans = input('>>> ')
if ans.upper() == 'Y':
    try:
        # Load the saved game
        up = pickle.Unpickler(open("progress.dat", "rb"))
        simVars = up.load()
        print("Loading game...")
    except FileNotFoundError:
        # No save data found
        print("No sava data found! Starting a new game...")
        simVars = SimulationVars()
else:
    # Don't load, start a new game
    print("Starting a new game...")
    simVars = SimulationVars()

printWeekHeader(None, None) # None makes it not print the new case information

# Main loop
while 1:
    mainLoop()
    # Check if the game has been lost.
    if gameEnd:
        print()
        if simVars.happiness <= 0:
            print("Happiness has reached 0%!")
        elif simVars.deaths >= 1000:
            print("Deaths have gone over 1,000!")
        print("You've failed to handle the COVID-19 pandemic well, and your reputation is ruined.")
        print("YOU LOSE!")
        break
    # Check if the game has been won.
    if getActiveCases() == 0:
        print()
        print("There are no active cases in the entire country.")
        print("New Zealand has successfully controlled the COVID-19 pandemic.")
        print()
        print("YOU WIN!")
        print()
        # Print final stats.
        print("Final happiness: %.1f%%" % simVars.happiness)
        print("Total cases: %d" % getTotalCases())
        print("Recovered cases: %d" % simVars.recoveredCases)
        print("Total deaths: %d" % simVars.deaths)
        print("You spent: %d weeks at level 1, %d weeks at level 2, %d weeks at level 3, %d weeks at level 4." % (simVars.weeksAtLevel[0],simVars.weeksAtLevel[1],simVars.weeksAtLevel[2],simVars.weeksAtLevel[3]))
        break