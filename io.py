import os, sys, string, math
from csv import reader as csvReader
from csv import writer as csvWriter

PUZZLESIZE = 9
ROW, COL = 0, 1
EMPTY = 0

# -------------------------------------------------------------
# ------------------- INPUT/OUTPUT FUNCTIONS ------------------
# -------------------------------------------------------------

def csvToList(csvFile):
	integerList = []
	with open(csvFile,'rb') as openFile:
		reader = csvReader(openFile)
		for line in reader:
			integerList.append([int (i) for i in line])
	return integerList

def listToCSV(integerList,filename):
	with open(filename,'wb') as csvfile:
		writer = csvWriter(csvfile,delimiter=',')
		for row in integerList:
			writer.writerow(row)
	return filename

def printPuzzle(puzzle):
	rowNumber = 0
	for row in puzzle:
		cellNumber = 0
		rowToPrint = '|'
		for cell in row:
			if cell == 0: 
	       			rowToPrint += '  '
			else: rowToPrint += str(cell) + ' '
			cellNumber += 1
		       	if cellNumber%3 == 0: rowToPrint += '|'
		if rowNumber%3 == 0:
       			print '-'*21
		rowNumber += 1
		print rowToPrint
	print '-'*21+'\n'

	emptySquares = sum(row.count(EMPTY) for row in puzzle)
	if not emptySquares == 0:
		if emptySquares == 1:
			print 'There is '+str(emptySquares)+' empty square!\n'
		else:
			print 'There are '+str(emptySquares)+' empty squares!\n'
	return

def printCellOptions(unknowns,options):
	# Prints unknown cell options
	unknowns.sort(key=lambda x: x[ROW])

	previous = 0
	print 'R C B Options\n-------------'
	for index,unknown in enumerate(unknowns):
		unknowns[index].append(options[index])
		if whatRow(unknown) != previous: print ''
		print whatRow(unknown),whatCol(unknown),whatBox(unknown),unknown[2]
		previous = unknown[ROW]
	
	previous = 0
	print '\nR C B Options\n-------------'
	unknowns.sort(key=lambda x: x[COL])	
	for unknown in unknowns:
		if whatCol(unknown) != previous: print ''
		print whatRow(unknown),whatCol(unknown),whatBox(unknown),unknown[2]
		previous = unknown[1]

	previous = 0
	print '\nR C B Options\n-------------'
	unknowns.sort(key=lambda x: whatBox(x))
	for unknown in unknowns:
		if whatBox(unknown) != previous: print ''
		print whatRow(unknown),whatCol(unknown),whatBox(unknown),unknown[2]
		previous = whatBox(unknown)
		
	unknowns.sort(key=lambda x: x[ROW])
	return True

def printPuzzleAndOptions(puzzle,unknowns,options):
	unknowns.sort(key=lambda x: x[ROW])
	columnSizes = [0]*PUZZLESIZE

	for index,option in enumerate(options):
		if len(option) > columnSizes[unknowns[index][COL]]:
			columnSizes[unknowns[index][COL]] = len(option)

	rowNumber = 0
	unknown = 0
	for row in puzzle:
		colNumber = 0
		rowToPrint = '|'
		for cell in row:
			if cell == 0: 
				spacing = ' '*((3*(columnSizes[colNumber]))-(3*len(options[unknown]))+1)
	       			rowToPrint += str(list(options[unknown]))+spacing
				unknown += 1
			else: 
				spacing = (3*columnSizes[colNumber])
				rowToPrint += ' '*int((math.floor(spacing/2)))+str(cell)+\
						' '*int(spacing-(math.floor(spacing/2)))
			colNumber += 1
		       	if colNumber%3 == 0: 
				rowToPrint += '|'
		if rowNumber%3 == 0:
       			print '-'*(13+sum(columnSizes)*3)
		rowNumber += 1
		print rowToPrint
       	print '-'*(13+sum(columnSizes)*3)+'\n'
