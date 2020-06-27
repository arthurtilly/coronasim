import math
import time

population = 4676000

HOSPITAL_CAPACITY = 5000

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
        
        # The people's faith in the government
        self.faith = 100.0
        
        # Current alert level
        self.alertLevel = 1

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
    return math.ceil((activeCases * (population - activeCases)) / population)
    
while 1:
    updateActiveCases(getNewInfected())
    print("Active %d deaths %d pop %d" % (getActiveCases(), simVars.deaths, population))
    time.sleep(0.5)
    




