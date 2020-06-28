import math
import time
import pickle

population = 4676000

daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# Variables
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

baseDeathRate = 2
baseRecoveryRate = 20

# Return the total number of active cases.
def getActiveCases():
    global simVars
    cases = 0
    for num in simVars.activeCases:
        cases += num
    return cases

def getTotalCases():
    global simVars
    return getActiveCases() + simVars.deaths + simVars.recoveredCases

def handleActiveCases(amount, weeksOld):
    global simVars
    
    # Todo: when hospitals are overloaded, death rate will increase drastically
    deathRate = baseDeathRate - 0.3*weeksOld # from 2% for new cases to 0.5% for 5 week old cases
    recoveryRate = baseRecoveryRate + 12*weeksOld # from 20% for new cases to 80% for 5 week old cases
    
    newDeaths = math.floor(amount * (deathRate / 100.0))
    simVars.deaths += newDeaths
    amount -= newDeaths
    
    recoveries = math.floor(amount * (recoveryRate / 100.0))
    simVars.recoveredCases += recoveries
    return amount - recoveries # Return remaining number of active cases

def updateActiveCases(newAmount): 
    global simVars
    
    for i in range(6,-1,-1): # Iterate from 6 to 0 inclusive
        if i == 6:
            # recovered case count is currently broken
            simVars.recoveredCases += simVars.activeCases[i] # All cases that are 6 weeks old will recover
        else:
            remainingCases = handleActiveCases(simVars.activeCases[i], i) # Calculate deaths and recoveries
            simVars.activeCases[i+1] = remainingCases # Move remaining cases further up the list as they are older
            
    simVars.activeCases[0] = newAmount # Add current cases

def getNewInfected():
    activeCases = simVars.activeCases[0] + simVars.activeCases[1]
    newInfected = math.floor((((activeCases/population) * ((population - activeCases)/population))) * population)
    
    if simVars.alertLevel == 2:
        newInfected *= 0.5
    elif simVars.alertLevel == 3:
        newInfected *= 0.2
    elif simVars.alertLevel == 4:
        newInfected *= 0.05
    
    return newInfected

def changeWeek():
    simVars.dayOfMonth += 7
    if simVars.dayOfMonth > daysInMonths[simVars.month]:
        simVars.dayOfMonth -= daysInMonths[simVars.month]
        simVars.month += 1
        if simVars.month > 11:
            simVars.month = 0
            simVars.year += 1
            
def getDateDisplay():
    if simVars.dayOfMonth in (1,21,31):
        suffix = "st"
    elif simVars.dayOfMonth in (2,22):
        suffix = "nd"
    elif simVars.dayOfMonth in (3,23):
        suffix = "rd"
    else:
        suffix = "th"
        
    return "%d%s %s %d" % (simVars.dayOfMonth, suffix, months[simVars.month], simVars.year)

def printWeekHeader(newCases, newDeaths):
    print()
    print('========= %s =========' % getDateDisplay())
    print("--- ALERT LEVEL %d ---" % simVars.alertLevel)
    if newCases is not None: print("In the past week, there have been %d new cases and %d deaths." % (newCases, newDeaths))
    print()
    print("Total cases: %d" % getTotalCases())
    print("Total active cases: %d" % getActiveCases())
    print("Total deaths: %d" % simVars.deaths)
    print("People's happiness: %.1f%%" % simVars.happiness)

def getInt(string):
    loop = True
    while loop:
        answer = input(string)
        try:
            return int(answer)
        except ValueError:
            print("Please enter an integer.")

def progressWeek():
    changeWeek()
    newCases = getNewInfected()
    oldDeaths = simVars.deaths
    updateActiveCases(newCases)
    
    if simVars.alertLevel == 1:
        simVars.happiness += 5
    if simVars.alertLevel == 2:
        simVars.happiness -= 5
    elif simVars.alertLevel == 3:
        simVars.happiness -= 10
    elif simVars.alertLevel == 4:
        simVars.happiness -= 15
        
    if simVars.happiness > 100:
        simVars.happiness = 100
        
    newDeaths = simVars.deaths - oldDeaths
    
    printWeekHeader(newCases, newDeaths)

def saveProgress():
    global simVars
    p = pickle.Pickler(open("progress.dat", "wb"))
    p.dump(simVars)
    print("Progress saved.")

def checkDetails():
    pass

def changeAlertLevel():
    print("Switch to which alert level? (1 - 4)")
    
    while 1: 
        ans = getInt(">>> ")
        if ans < 1 or ans > 4:
            print("Answer out of range.")
        else:
            if ans == 3 and getTotalCases() < 100:
                print("Too early to switch to Level 3! (Cases should be over 100)")
            elif ans == 4 and getTotalCases() < 500:
                print("Too early to switch to Level 4! (Cases should be over 500)")
            elif ans == simVars.alertLevel:
                print("You were already at alert level %d." % ans)
            else:
                print("Switched to alert level %d." % ans)
                simVars.alertLevel = ans
            return


def mainLoop():
    print()
    print("A - Change alert level")
    print("S - Save progress")
    print("C - Check details on active cases")
    print("P - Progress to the next week")
    
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
    
print('''
===== Welcome to CoronaSim! =====

The country of New Zealand has just had its first few recorded cases of COVID-19
coming in from the border. As the Minister of Health, you must guide the
country to make sure the pandemic doesn't get out of hand!

You lose when happiness hits 0% or deaths rise above 10,000.
You win when there are no active cases.

Important info:
* You cannot raise the alert level too high when cases are too low.

Would you like to load a previous game? (y/n)''')

ans = input('>>> ')
if ans.upper() == 'Y':
    try:
        up = pickle.Unpickler(open("progress.dat", "rb"))
        simVars = up.load()
        print("Loading game...")
    except FileNotFoundError:
        print("No progress found! Starting a new game...")
        simVars = SimulationVars()
else:
    print("Starting a new game...")
    simVars = SimulationVars()

printWeekHeader(None, None)
while 1:
    mainLoop()