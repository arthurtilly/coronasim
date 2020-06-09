import math
import time

population = 4676000
HOSPITAL_CAPACITY = 5000

# Variables
cases = 0 # Total number of cases

# Active cases for each past week. First element is current week, second is 1 week ago, etc.
# After 6 weeks all cases will recover
activeCases = [1,0,0,0,0,0,0]

deaths = 0 # 
recoveredCases = 0
faith = 100.0
happiness = 100.0
alertLevel = 1
baseDeathRate = 1
baseRecoveryRate = 20

# Return the total number of active cases.
def getActiveCases():
    global activeCases
    cases = 0
    for num in activeCases:
        cases += num
    return cases

def getTotalCases():
    global deaths, recoveredCases
    return getActiveCases() + deaths + recoveredCases

def handleActiveCases(amount, weeksOld):
    global population, deaths, recoveredCases
    
    # Todo: when hospitals are overloaded, death rate will increase drastically
    deathRate = baseDeathRate - 0.15*weeksOld # from 1% for new cases to 0.25% for 5 week old cases
    recoveryRate = baseRecoveryRate + 12*weeksOld # from 20% for new cases to 80% for 5 week old cases
    
    newDeaths = math.floor(amount * (deathRate / 100.0))
    deaths += newDeaths
    population -= newDeaths
    amount -= newDeaths
    
    recoveries = math.floor(amount * (recoveryRate / 100.0))
    recoveredCases += recoveries
    return amount - recoveries # Return remaining number of active cases

def updateActiveCases(newAmount): 
    global recoveredCases
    
    for i in range(6,-1,-1): # Iterate from 6 to 0 inclusive
        if i == 6:
            # recovered case count is currently broken
            recoveredCases += activeCases[i] # All cases that are 6 weeks old will recover
        else:
            remainingCases = handleActiveCases(activeCases[i], i) # Calculate deaths and recoveries
            activeCases[i+1] = remainingCases # Move remaining cases further up the list as they are older
            
    activeCases[0] = newAmount # Add current cases

def getNewInfected():
    activeCases = getActiveCases()
    return math.ceil((activeCases * (population - activeCases)) / population)
    
while 1:
    updateActiveCases(getNewInfected())
    print("Active %d deaths %d pop %d" % (getActiveCases(), deaths, population))
    time.sleep(0.5)
    




