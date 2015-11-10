#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|                     `YMM'   `MP' .g8""8q. `7MM"""Mq.             db            |#
#|                       VMb.  ,P .dP'    `YM. MM   `MM.                          |#
#|   .gP"Ya `7M'   `MF'   `MM.M'  dM'      `MM MM   ,M9           `7MM  ,pW"Wq.   |#
#|  ,M'   Yb  `VA ,V'       MMb   MM        MM MMmmdM9              MM 6W'   `Wb  |#
#|  8M""""""    XMX       ,M'`Mb. MM.      ,MP MM  YM.              MM 8M     M8  |#
#|  YM.    ,  ,V' VA.    ,P   `MM.`Mb.    ,dP' MM   `Mb.            MM YA.   ,A9  |#
#|   `Mbmmd'.AM.   .MA..MM:.  .:MMa.`"bmmd"' .JMML. .JMM. mmmmmmm .JMML.`Ybmd9'   |#
#|________________________________________________________________________________|#
####################################################################################

import sys, re, readline, ast, traceback, platform, string
from blessings import Terminal

if platform.system() == "Windows":
	from colorama import init
	init()

####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	PROMPT																		  |#
#|________________________________________________________________________________|#
####################################################################################

class Prompt:
	def __init__ (self, project, printer):
		self.project = project
		self.printer = printer
		self.terminal = self.printer.terminal
		self.prompt = "exXOR: "

	def begin (self):
		while True:
			with self.terminal.location(0, self.terminal.height - 1):
				userInput = self.getInput(self.prompt).strip()
			if userInput in ["exit()", "quit()", "exunt()"]:
				break
			elif userInput == "debug()":
				import pdb
				pdb.set_trace()
			elif userInput == "help()":
				print "Figure it out."
			else:
				self.inputParser(userInput)
			print ""

	def updatePrompt (self, newPrompt = None):
		self.prompt = self.prompt[:-2].split("@")[0]
		if newPrompt:
			self.prompt = self.prompt + "@" + newPrompt + ": "

	def inputParser (self, userInput):
		inputItems = userInput.split("(", 1)
		inputFunction = inputItems[0]

		if len(inputItems) > 1:
			inputArguments = ast.literal_eval("[" + inputItems[1].split(")")[0] + "]")
		else:
			inputArguments = []

		if inputFunction == "replace" and len(inputArguments) < 3:
			inputArguments = [inputArguments[0], None, None, int(inputArguments[1].split("R")[1])]

		try:
			projectFunction = getattr(self.project, inputFunction)
		except:
			self.printer.log("error", "Function does not exist.")
			return

		try:
			self.handleResult(inputFunction, projectFunction(*inputArguments))
		except:
			self.printer.log("error", "Error during function:\n" + traceback.format_exc())
			import pdb
			pdb.set_trace()
			return

	def handleResult (self, functionName, functionResult):
		if functionName in ["load", "create"]:
			self.updatePrompt(functionResult)

	def getInput (self, prompt):
		sys.stdout.write(prompt)
		sys.stdout.flush()

		characters = []
		while True:
			inputCharacter = getch()

			if inputCharacter == "\r":
				self.printer.printAtBeginningOfLine("")
				sys.stdout.write(self.printer.printFullLine(self.prompt, doPrint=False))
				sys.stdout.flush()
				return "".join(characters)
			elif inputCharacter in string.printable[:-5]:
				characters.append(inputCharacter)
				sys.stdout.write(inputCharacter)
				sys.stdout.flush()
			elif inputCharacter == "\x7f" and characters:
				characters.pop()
				sys.stdout.write(self.terminal.move_left + " " + self.terminal.move_left)
				sys.stdout.flush()
			elif inputCharacter in ["\x1a", "\x03"]:
				sys.exit()



####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	SINGLE-CHAR INPUT FOR PROMPT												  |#
#|________________________________________________________________________________|#
####################################################################################

if platform.system() == "Windows":
	import msvcrt
	def getch():
		return msvcrt.getch()
else:
	import tty, termios, sys
	def getch():
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch


####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	PRINTING FUNCTIONS															  |#
#|________________________________________________________________________________|#
####################################################################################

class Printer:
	def __init__ (self, loggingEnabled, colorsEnabled, passableOutput):
		self.loggingEnabled = loggingEnabled
		self.colorsEnabled = colorsEnabled
		self.passableOutput = passableOutput
		self.lastPrintedLength = 0
		self.terminal = Terminal()
		self.enterFullscreen = self.terminal.fullscreen

####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	COLORING AND LOGGING WITH OVERRIDES											  |#
#|________________________________________________________________________________|#
####################################################################################

	def styled (self, message, color = None, background = "", attrs = []):
		if not color:
			color = "bright_white"

		if self.colorsEnabled:
			return getattr(self.terminal, color) + \
				   getattr(self.terminal, background) + \
				   "".join([getattr(self.terminal, attr) for attr in attrs]) + \
				   message + \
				   self.terminal.normal
		else:
			return message

	def cprint (self, message, color = None, background = None, attrs = [], end = "\n"):
		if self.colorsEnabled:
			sys.stdout.write(self.styled(message, color, background, attrs) + end)
			sys.stdout.flush()
		else:
			sys.stdout.write(message + end)
			sys.stdout.flush()

	def log (self, infoType, message):
		if self.loggingEnabled:
			if infoType == "info":
				bgColor = "on_blue"
				self.cprint(" i      ", "white", bgColor, attrs=["bold"], end="")
			elif infoType == "warn":
				bgColor = "on_yellow"
				self.cprint(" !      ", "white", bgColor, attrs=["bold"], end="")
			elif infoType == "error":
				bgColor = "on_red"
				self.cprint(" X      ", "white", bgColor, attrs=["bold"], end="")
			elif infoType == "success":
				bgColor = "on_green"
				self.cprint(u" \u2713      ", "bright_white", bgColor, attrs=["bold"], end="")
			elif infoType == "command":
				bgColor = "on_white"
				self.cprint(u" >      ", "black", bgColor, attrs=["bold"], end="")
			else:
				self.cprint("error", "Incorrect infoType passed to prettyPrint.")
				return
	
			print " " + (self.styled("\n        ", background=bgColor) + " ").join(message.split("\n"))

	def searchResultsFormatter (self, results):
		outputLines = []
		for index, result in enumerate(results):
			currentGroup = []
			currentGroup.append(self.styled("(R%d) Result %d in %s" %(index, index, result["fileName"]), attrs=["bold", "underline"]))
			resultString = result["stringDescription"]["decrypted"] or result["stringDescription"]["original"]
			for resultLine in resultString.split("\n"):
				currentGroup.append(self.styled(resultLine, "white"))
			outputLines.append("\n".join(currentGroup))
		return outputLines


####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	MAIN FUNCTIONS																  |#
#|________________________________________________________________________________|#
####################################################################################

	def printFileHeading (self, title, hasStrings = False, hasEncryptedStrings = True, multipleSections = False, magicNumbers = None, color = None):
		boldTitle = self.styled(title, attrs=["bold"])

		if hasStrings:
			if multipleSections:
				colorToPrint = color or "cyan"
				leftText = ""
			else:
				colorToPrint = color or "green"
				leftText = self.styled(str(magicNumbers)[1:-1], colorToPrint, attrs=["bold"])

			if not hasEncryptedStrings:
				leftText = self.styled("NO ENCRYPTION", attrs=["bold"])
		else:
			colorToPrint = color or "white"
			leftText = ""

		leftText = self.styled(" " * 2, None, "on_" + colorToPrint) + ((" "+leftText+" " ) if leftText else "")
		leftSide = self.textBeforeTabs(leftText, 4, colorToPrint)
		heading = " " + self.styled(title, attrs=["bold"]) + " "
		padding = self.styled(" ", None, "on_" + colorToPrint)

		print "\n"
		self.printFullLine(leftSide + heading, padding)
		print ""

	def printSectionHeading (self, sectionNumber = None, magicNumbers = None, title = "", color = None):
		endingText = ""
		colorToPrint = color or "yellow"

		if not title:
			title = " " * 4 + \
					self.styled(" " * 4, None, "on_" + colorToPrint) + \
					" SECTION " + \
					str(sectionNumber) + \
					" " + \
					self.styled(" " * 2, None, "on_" + colorToPrint) + \
					" " + \
					self.styled(str(magicNumbers)[1:-1] + " ", "yellow")

		title = self.styled(title, colorToPrint)
		padding = self.styled(" ", None, "on_" + colorToPrint)

		print ""
		self.printFullLine(title, padding)
		print ""

	def printGraphicalString (self, text, wasDecrypted = False, isUnprintable = False, originalString = "", isUnderSection = False):
		if isUnprintable:
			stringType = "UNPRINTABLE"
			foreground = None
			background = "on_red"
		elif wasDecrypted:
			stringType = "DECRYPTED"
			foreground = "grey"
			background = "on_white"
		else:
			stringType = "PLAIN\t"
			foreground = None
			background = "on_blue"

		if isUnprintable:
			if wasDecrypted:
				text =	self.styled("ORIGINAL:\t", background.replace("on_", "")) + \
						self.makeStringSafe(originalString) + \
						"\n" + \
						self.styled("DECRYPTED:\t", background.replace("on_", "")) + \
						self.makeStringSafe(text)
			else:
				text =	self.styled("PLAIN:\t\t", background.replace("on_", "")) + \
						self.makeStringSafe(text)

		splitText = text.split("\n")
		stringType = " " + stringType + "\t"
		coloredPad = ("\t" if isUnderSection else "") + self.styled("\t\t", foreground, background) + "\t"
		stringLabel = ("\t" if isUnderSection else "") + self.styled(stringType, foreground, background, attrs=["bold"])

		print stringLabel + "\t" + ("\n" + coloredPad).join(splitText)
	
	def printFullLine (self, initialText, paddingText = " ", endingText = "", maxEndingTextLength = 0, doPrint = True):
		initialTextLength = self.lengthWithoutColors(initialText)
		paddingTextLength = self.lengthWithoutColors(paddingText)
		endingTextLength = self.lengthWithoutColors(endingText)

		if paddingText == "\t":
			maxTabs = (self.terminal.width / 8)
			padsNeeded = (maxTabs - (initialTextLength / 8) - (1 + (maxEndingTextLength / 8)))
			fractionalPad = 0
		else:
			spaceToFill = self.terminal.width - initialTextLength - endingTextLength
			padsNeeded = spaceToFill / paddingTextLength
			fractionalPad = spaceToFill % paddingTextLength
		
		output = initialText + padsNeeded * paddingText + paddingText[:fractionalPad] + endingText

		if doPrint:
			print output
		else:
			return output

	def printAtBeginningOfLine (self, text):
		sys.stdout.write("\r" + text)
		sys.stdout.flush()

	def clearDisassemblyProcessingLine (self):
		self.printAtBeginningOfLine(" " * self.lastPrintedLength)
		self.printAtBeginningOfLine("")

	def printDisassemblyProcessingLines (self, *items):
		self.clearDisassemblyProcessingLine()

		textItems = []
		for item in items:
			textItems.append(str(item))

		fullText = ' '.join(textItems)
		if fullText.startswith("processing"):
			splitString = fullText.split(", ")
			[currentFile, totalFiles] = splitString[-1].split(" ")[0].split("/")
			filePath = splitString[0][18:]

			stringToPrint = "(%s/%s) %s" %(currentFile.rjust(len(totalFiles)), totalFiles, filePath)
			self.lastPrintedLength = len(stringToPrint)
			self.printAtBeginningOfLine(stringToPrint)

####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	UTILITY FUNCTIONS															  |#
#|________________________________________________________________________________|#
####################################################################################

	def lengthWithoutColors (self, text):
		strippedText = re.sub("\\x1b\[[\d]{1,}m", "", text).replace("\r", "")
		return len(strippedText)

	def textBeforeTabs (self, text, numberOfTabs, tabColor = None):
		colorToPrint = ("on_" + tabColor) if tabColor else None
		spacesNeeded = (numberOfTabs * 8) - self.lengthWithoutColors(text)
		return text + self.styled(spacesNeeded * " ", None, colorToPrint)

	def makeStringSafe (self, funString):
		boringString = repr(funString)

		if boringString[0] == "u":
			return boringString[2:-1]
		else:
			return boringString[1:-1]