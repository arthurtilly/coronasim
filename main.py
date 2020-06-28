import math
import time
import pickle

population = 4676000

HOSPITAL_CAPACITY = 5000

daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# Variables
class SimulationVars:
    def __init__(self):
        self.cases = 0 # Total number of cases
        
        # Active cases for each past week. First element is current week, second is 1 week ago, etc.
        # After 6 weeks all cases will recover
        self.activeCases = [1,0,0,0,0,0,0]
        
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

simVars = SimulationVars()

baseDeathRate = 1
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
    deathRate = baseDeathRate - 0.15*weeksOld # from 1% for new cases to 0.25% for 5 week old cases
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
    activeCases = getActiveCases()
    return math.ceil((((activeCases/population) * ((population - activeCases)/population))) * population)

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

def printWeekHeader():
    print()
    print('========= %s =========' % getDateDisplay())
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
    updateActiveCases(getNewInfected())
    printWeekHeader()

def saveProgress():
    global simVars
    p = pickle.Pickler(open("progress.dat", "wb"))
    p.dump(simVars)

def checkDetails():
    pass

def changeAlertLevel():
    pass


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
    


printWeekHeader()
while 1:
    mainLoop()