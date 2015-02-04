import data, io

# -------------------- STRATEGY FUNCTIONS ---------------------
# -------------------------------------------------------------
newArray = object()
PASSLIMIT = 2
ROW,COL = 0,1
TESTS = range(0,3)
MINNUMBEROFSIBLINGS,MAXNUMBEROFSIBLINGS = 2,3
MEMBER, OPTIONS = 0,2

def findSiblings(unknowns,options,number):
	# Determine cells with identical options in same row/col/box in puzzle
	# (Referred to as siblings)
	siblings = []
	for index, unknown in enumerate(unknowns):
		if len(options[index]) == number:
			if options.count(options[index])>1:
				siblings.append([data.whatRow(unknown),data.whatCol(unknown),options[index]])
	return siblings

def checkSiblings(sibling,siblings,functionCall = 0,allSiblings = newArray,familyGroups = newArray):
	# Recursive function to find siblings sharing groups

	functionCall +=1
	index = siblings.index(sibling)+1
	while index < (len(siblings)):
		if sibling[OPTIONS] == siblings[index][OPTIONS]:
			sharedGroups = data.sameGroup(sibling,siblings[index])
			if familyGroups is newArray:
				familyGroups = data.sameGroup(sibling,siblings[index])
			if any([familyGroups[testNumber] and sharedGroups[testNumber] for testNumber in TESTS]):
				familyGroups = [familyGroups[testNumber] and sharedGroups[testNumber] for testNumber in TESTS]
				if allSiblings is newArray:
					allSiblings = [sibling,siblings[index]]
				else:
					if siblings[index] not in allSiblings:
						allSiblings.append(siblings[index])
				if functionCall < (len(sibling[OPTIONS])-1):
					allSiblings = checkSiblings(siblings[index],siblings,
									functionCall,allSiblings,familyGroups)
			else:
				familyGroups = newArray
		index += 1
	if allSiblings is newArray: allSiblings = []
	else: 
		if len(allSiblings) != len(sibling[OPTIONS]): allSiblings = []
	return allSiblings

def eliminateSiblings(unknowns,options,unsolved):
	# Finds cells in same row, col, or box with matching option twins/triplets/'siblings'
	# and eliminates those entries from the other cells in that row, col, or box.
	
	for numOfSiblings in range(MINNUMBEROFSIBLINGS-1,MAXNUMBEROFSIBLINGS+1):
		siblingGroups = findSiblings(unknowns,options,numOfSiblings)
		for siblings in siblingGroups:
			family = checkSiblings(siblings,siblingGroups)
			if type(family) == list and len(family)== numOfSiblings:
				for test in data.whatRowColOrBox:
					allTested = [test(sibling) for sibling in family]
					if len(set(allTested)) == 1:
						for index,unknown in enumerate(unknowns):
							if (test(unknown) == test(family[MEMBER]) \
							and family[MEMBER][OPTIONS] != options[index]):
									options[index] = options[index] - family[MEMBER][OPTIONS]
	return unknowns, options, unsolved

def checkOnlyOptions(unknowns,options,rowsColsBoxs):
	# Checks if there is a cell in a row, col or box that has an unique option 
	# for that whole row, col, box
	for testNumber, groups in enumerate(rowsColsBoxs):
		groupNumber = 0	
		instance = [0,0]
		while (groupNumber < len(groups)):
			group = list(data.SOLVEDSET - groups[groupNumber])
			optionNumber = 0
			while (optionNumber < len(group)):	
				cellNumber, occurs = 0, 0
				while ((cellNumber < len(unknowns)) and (occurs < 2)):
					if data.whatRowColOrBox[testNumber](unknowns[cellNumber]) == groupNumber:
						if group[optionNumber] in options[cellNumber]:		
							instance = [cellNumber, group[optionNumber]]
							occurs += 1
					cellNumber += 1
				if occurs == 1: 
					options[instance[0]] = set([instance[1]])
				optionNumber += 1
			groupNumber += 1	
	return unknowns,options


def implement(unknowns,options,unsolved):
	# Determines cells with only one option for cell by applying strategies and
	# escapes after not reducing unknown cells whether its solved or not
	
	unsuccessfulPasses, trialNumber = 0, 0
	numUnknowns = len(unknowns)
	while (numUnknowns != 0) and (unsuccessfulPasses < PASSLIMIT):
		# Locate unknowns 
		unknowns = data.findZeros(unsolved)

		# Get sets of options for each row, col, box
		sets = data.getSets(unsolved)
	
		# Get cell options
		options = data.getOptions(sets, unknowns)
		
		# Eliminate pairs
		unknowns, options, unsolved = eliminateSiblings(unknowns,options,unsolved)
		
		# Check for only options
		unknowns, options = checkOnlyOptions(unknowns,options,sets)
		
		# Insert the option if there's only one!
		squaresFilled = 0
		for cellNumber, cell in enumerate(unknowns):
			if len(options[cellNumber]) == 1:
				squaresFilled += 1
				mistake, unsolved = data.insertKnown(unsolved,\
								    [data.whatRow(cell),data.whatCol(cell)],\
	            						     options[cellNumber].pop())
	
		if numUnknowns == len(unknowns):
			unsuccessfulPasses +=1 
			print 'Unsuccessful Pass! (Number '+str(unsuccessfulPasses)+')\n'
		else:
			unsuccessfulPasses = 0
	
		if len(options) != squaresFilled and len(unknowns) != 0:
			if trialNumber == 1:
				print 'After '+str(trialNumber)+' pass, the puzzle is:'
			else:
				print 'After '+str(trialNumber)+' passes, the puzzle is:'
			io.printPuzzle(unsolved)
	
		numUnknowns = len(unknowns)
		trialNumber += 1
		
	return  unknowns, options, unsolved
	

