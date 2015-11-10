#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|                     `YMM'   `MP' .g8""8q. `7MM"""Mq.    |#
#|                       VMb.  ,P .dP'    `YM. MM   `MM.   |#
#|   .gP"Ya `7M'   `MF'   `MM.M'  dM'      `MM MM   ,M9    |#
#|  ,M'   Yb  `VA ,V'       MMb   MM        MM MMmmdM9     |#
#|  8M""""""    XMX       ,M'`Mb. MM.      ,MP MM  YM.     |#
#|  YM.    ,  ,V' VA.    ,P   `MM.`Mb.    ,dP' MM   `Mb.   |#
#|   `Mbmmd'.AM.   .MA..MM:.  .:MMa.`"bmmd"' .JMML. .JMM.  |#
#|_________________________________________________________|#
#############################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|                       VERSION 1.0                       |#
#|                COPYRIGHT 2014 TREY KEOWN                |#
#|                                                         |#
#|  exXOR is a program which aims to make it easy to work  |#
#|  with disassembled jGrasp code. All strings in jGrasp   |#
#|  are encrypted using a simple XOR scheme with a unique  |#
#|  key for each file. This key is only five characters.   |#
#|---------------------------------------------------------|#
#|	Nonstandard Modules Used							   |#
#|		* All			ply, blessings					   |#
#|		* Windows		colorama (optional)				   |#
#|_________________________________________________________|#
#############################################################

import os, sys, json, zipfile, shutil, time
import exXOR_io, exXOR_core

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "krakatau"))
from krakatau.disassemble import disassembleClass as Krakatau_disassembleClass
from krakatau.assemble import assembleClass as Krakatau_assembleClass
from krakatau.Krakatau import script_util as Krakatau_scriptUtil

EXXOR_STRING_SIGNATURE		= "\t;exXOR "
EXXOR_FOLDER				= os.path.join(os.path.expanduser("~"), ".exXOR")
VALID_FILENAME_CHARACTERS	= "-_.()abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	PROJECT CLASS																  |#
#|________________________________________________________________________________|#
####################################################################################

class Project:
	def __init__ (self, printer):
		self.projectName = None
		self.projectFolder = None
		self.disassembledDirectory = None
		self.assembledDirectory = None
		self.projectJar = None
		self.outputJar = None
		self.exportJar = None
		self.configFile = None
		self.lastTrackedModificationTime = None
		self.searchResults = []
		self.printer = printer
		self.strings = exXOR_core.StringManager()

	def load (self, projectName):
		self.printer.log("command", "Loading project: " + projectName)
		self.projectName = projectName
		self.projectFolder = os.path.join(EXXOR_FOLDER, self.projectName)
		self.disassembledDirectory = os.path.join(self.projectFolder, "disassembled")
		self.assembledDirectory = os.path.join(self.projectFolder, "assembled")
		self.projectJar = os.path.join(self.projectFolder, "source.jar")
		self.exportJar = os.path.join(self.projectFolder, "export.jar")
		self.configFile = os.path.join(self.projectFolder, "config.json")

		with open(os.path.join(self.projectFolder, "config.json"), "r") as f:
			projectData = json.load(f)

		self.outputJar = projectData["output"]
		self.strings.load(projectData["strings"], projectData["originals"])
		self.lastTrackedModificationTime = projectData["modifiedTime"]

		self.printer.log("success", "Project loaded.")

		return projectName

	def create (self, projectName, jarPath):
		self.printer.log("command", "Creating project: " + projectName)
		self.projectFolder = os.path.join(EXXOR_FOLDER, projectName)

		isValidFileName = all(characters in VALID_FILENAME_CHARACTERS for characters in projectName)
		isValidSourceJar = os.path.isfile(jarPath)
		isValidProjectFolder = not os.path.exists(self.projectFolder)
		
		if isValidFileName and isValidSourceJar and isValidProjectFolder:
			self.projectName = projectName
			self.disassembledDirectory = os.path.join(self.projectFolder, "disassembled")
			self.assembledDirectory = os.path.join(self.projectFolder, "assembled")
			self.projectJar = os.path.join(self.projectFolder, "source.jar")
			self.exportJar = os.path.join(self.projectFolder, "export.jar")
			self.outputJar = jarPath
			self.configFile = os.path.join(self.projectFolder, "config.json")

			self.printer.log("info", "Creating project structure...")
			os.makedirs(self.projectFolder)
			os.makedirs(self.disassembledDirectory)
			os.makedirs(self.assembledDirectory)
	
			self.printer.log("info", "Copying targeted JAR file...")
			shutil.copy2(self.outputJar, self.projectJar)
	
			self.printer.log("info", "Disassembling class files and building strings database...")
			self._disassembleProjectJar()
			self.printer.clearDisassemblyProcessingLine()
	
			self.printer.log("info", "Done disassembling classes.")
			self.printer.log("info", "Decrypting all encrypted strings...")
			self.strings.decryptAllStrings()

			self.printer.log("info", "Writing strings database...")
			self._updateConfigJson()
	
			self.printer.log("success", "Successfully created project.")
	
		else:
			if not isValidFileName:
				self.printer.log("error", "Invalid project name: " + projectName + "\nStick to alphanumerics.")
			elif not isValidSourceJar:
				self.printer.log("error", "Invalid path for jar file: " + jarPath)
			elif not isValidProjectFolder:
				self.printer.log("error", "Project with same name already exists")
			
			self.projectFolder = None

		return projectName

	def search (self, searchString):
		self.printer.log("command", "Searching for string \"%s\"" %searchString)
		results = []
	
		for fileName, fileData in self.strings.list.iteritems():
			for stringIndex, stringDescription in enumerate(fileData["strings"]):
				shouldAppend = False
	
				if "decrypted" in stringDescription:
					if searchString in stringDescription["decrypted"]:
						shouldAppend = True
				elif searchString in stringDescription["original"]:
					shouldAppend = True
	
				if shouldAppend:
					results.append({	"fileName":				fileName, \
										"stringIndex":			stringIndex, \
										"stringDescription":	stringDescription})
		self.searchResults = results
		for result in self.printer.searchResultsFormatter(results):
			self.printer.log("info", result)
		return results

	def replace (self, newString, fileName = None, stringIndex = None, resultReference = None):
		if resultReference != None:
			stringIndex = self.searchResults[resultReference]["stringIndex"]
			fileName = self.searchResults[resultReference]["fileName"]

		oldString = self.strings.stringValue(fileName, stringIndex)
		stringToInsert = self.strings.replaceString(fileName, stringIndex, newString)
		originalString = self.strings.stringValue(fileName, stringIndex, original=True)

		self.printer.log("command", "Replacing string at index %d in \"%s\"" %(stringIndex, fileName))
		self.printer.log("info", "    " +   self.printer.styled("New", "white") + "\t" + newString + \
								 "\n    " + self.printer.styled("Old", "white") + "\t" + oldString + \
								 "\n    " + self.printer.styled("Inserted", "white") + "\t" + stringToInsert.encode("unicode-escape") + \
								 "\n    " + self.printer.styled("Original", "white") + "\t" + originalString)
	
		jasminFileName = fileName[:-6] + ".j"
		fullFilePath = os.path.join(self.disassembledDirectory, jasminFileName)
	
		with open(fullFilePath, "r+") as f:
			jasminSourceLines = f.read().split("\n")
			f.seek(0)
			f.write(self._sourceWithStringReplaced(jasminSourceLines, stringIndex, stringToInsert))
			f.truncate()
	
		self._updateConfigJson()
		self.printer.log("success", "String updated.")

	def assemble (self, filesModified = None):
		if not filesModified:
			filesModified = self._filesModified()
		
		self.printer.log("command", "Assembling %d changed files." %(len(filesModified)))

		if filesModified:
			for modifiedFile in self._filesModified():
				filePathWithinJar = modifiedFile.replace(self.disassembledDirectory + os.sep, "", 1)
	
				self.printer.log("info", "Assembling " + filePathWithinJar)
				pairs = Krakatau_assembleClass(modifiedFile, False, False)
				if len(pairs) > 1:
					self.printer.log("error", "More than one assembly file was returned from assembleClass for file " + modifiedFile + "\nI'm not sure how to handle this.")
					return
				else:
					neededDirectories = os.path.join(self.assembledDirectory, os.path.split(filePathWithinJar)[0])
					if not os.path.exists(neededDirectories):
						os.makedirs(neededDirectories)
					with open(os.path.join(neededDirectories, pairs[0][0] + ".class"), 'wb') as f:
						f.write(pairs[0][1])
	
			self.lastTrackedModificationTime = int(time.time())
			self._updateConfigJson()
	
			self.printer.log("success", "Successfully assembled changed files.")
		else:
			self.printer.log("warn", "Nothing to assemble.")

	def export (self):
		filesModified = self._filesModified()
		if filesModified != []:
			if self.printer.yesNo("Files have been modified, but not assembled. Assemble now?"):
				self.assemble(filesModified)

		self.printer.log("command", "Exporting changes to target at %s" %(self.outputJar))
		self.printer.log("info", "Generating JAR file...")

		assembledFiles = []
		with zipfile.ZipFile(self.exportJar, "w") as exportJar:
			for directory, subdirectories, files in os.walk(self.assembledDirectory):
				relativeDirectory = directory.replace(self.assembledDirectory, "", 1)
				zipDirectory = os.sep.join(relativeDirectory.split(os.sep)[1:])
				for fileName in files:
					fullPathInZip = os.path.join(zipDirectory, fileName)
					assembledFiles.append(fullPathInZip)
					exportJar.write(os.path.join(directory, fileName), fullPathInZip)

			with zipfile.ZipFile(self.projectJar, "r") as originalJar:
				for fileName in originalJar.namelist():
					if fileName not in assembledFiles:
						with originalJar.open(fileName) as fileToBeWritten:
							exportJar.writestr(fileName, fileToBeWritten.read())

		self.printer.log("info", "Replacing JAR file...")
		shutil.copy2(self.exportJar, self.outputJar)

		self.printer.log("success", "Successfully exported modified JAR file.")

	def _updateConfigJson (self):
		with open(self.configFile, "w") as fileHandle:
			json.dump(	{	"output":		self.outputJar, \
							"modifiedTime":	self.lastTrackedModificationTime, \
							"originals":	self.strings.originals, \
							"strings":		self.strings.list \
						}, fileHandle, sort_keys=True)

	def _disassembleProjectJar (self):
		targets = Krakatau_scriptUtil.findFiles(self.projectJar, None, ".class")
		def readArchive(name):
			with zipfile.ZipFile(self.projectJar, "r") as archive:
				return archive.open(name).read()
		Krakatau_disassembleClass(readArchive, targets, self.disassembledDirectory, self.printer.printDisassemblyProcessingLines, self.strings)
		self.lastTrackedModificationTime = int(time.time())

	def _sourceWithStringReplaced (self, sourceLinesList, stringIndex, newString):
		shouldReplaceLine = False
		instructionName = ""
	
		for sourceLineIndex, lineText in enumerate(sourceLinesList):
			if EXXOR_STRING_SIGNATURE in lineText:
				stringData = lineText[len(EXXOR_STRING_SIGNATURE) - 1:].split(",")
				foundStringIndex = int(stringData[0])
	
				if foundStringIndex == stringIndex:
					shouldReplaceLine = True
					instructionName = stringData[1]
				
			elif shouldReplaceLine:
				sourceLinesList[sourceLineIndex] = "\t%s %s" %(instructionName, repr(str(newString)))
				break
	
		return "\n".join(sourceLinesList)

	def _filesModified (self):
		modified = []
		for path, directoryNames, fileNames in os.walk(self.disassembledDirectory):
			for fileName in fileNames:
				fullFileName = os.path.join(path, fileName)
				if int(os.path.getmtime(fullFileName)) > self.lastTrackedModificationTime:
					modified.append(fullFileName)
		return modified


####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	COMMAND-LINE LAUNCH															  |#
#|________________________________________________________________________________|#
####################################################################################

if __name__== "__main__":
	printer = exXOR_io.Printer(True, True, False)
	with printer.enterFullscreen():
		project = Project(printer)
		prompt = exXOR_io.Prompt(project, printer)
		prompt.begin()

#	import argparse
#	parser = argparse.ArgumentParser(description="exXOR - tool for working with encrypted strings in jGrasp")
#	parser.add_argument("action",			choices=("initialize", "interactive", "list", "pass"))
#	parser.add_argument("target",			help="When initializing, the full path to the jGrasp JAR file. Otherwise, the project name.")
#	parser.add_argument("--plain",			metavar="",	help="Don't try to display any colored output.")
#	parser.add_argument("--inline",			metavar="",	help="For use with \"list\". Fit everything about a string in one line. Won't display colors. Makes output passable to tools like grep.")
#	args = parser.parse_args()

