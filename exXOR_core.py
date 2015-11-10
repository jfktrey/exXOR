#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|                     `YMM'   `MP' .g8""8q. `7MM"""Mq.                                              |#
#|                       VMb.  ,P .dP'    `YM. MM   `MM.                                             |#
#|   .gP"Ya `7M'   `MF'   `MM.M'  dM'      `MM MM   ,M9            ,p6"bo   ,pW"Wq.`7Mb,od8 .gP"Ya   |#
#|  ,M'   Yb  `VA ,V'       MMb   MM        MM MMmmdM9            6M'  OO  6W'   `Wb MM' "',M'   Yb  |#
#|  8M""""""    XMX       ,M'`Mb. MM.      ,MP MM  YM.            8M       8M     M8 MM    8M""""""  |#
#|  YM.    ,  ,V' VA.    ,P   `MM.`Mb.    ,dP' MM   `Mb.          YM.    , YA.   ,A9 MM    YM.    ,  |#
#|   `Mbmmd'.AM.   .MA..MM:.  .:MMa.`"bmmd"' .JMML. .JMM. mmmmmmm  YMbmd'   `Ybmd9'.JMML.   `Mbmmd'  |#
#|___________________________________________________________________________________________________|#
#######################################################################################################

import re

Z_FUNCTION_SIGNATURE	= ".method static private z : ([C)Ljava/lang/String;"
Z_FUNCTION_CALL			= re.compile("\tinvokestatic .* z \(Ljava/lang/String;\)\[C")
Z_FUNCTION_MAGIC_LINES	= [14, 16, 18, 20, 22]


####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	DECRYPTION FUNCTIONS														  |#
#|________________________________________________________________________________|#
####################################################################################

def xorString (encryptedString, magicNumbers):
	if (len(encryptedString) < 2):
		return chr(ord(encryptedString[0]) ^ magicNumbers[4])
	else:
		newString = []
		for index, character in enumerate(encryptedString):
			newString.append(unichr(ord(encryptedString[index]) ^ magicNumbers[index % 5]))
		return ''.join(newString)

def magicFromZFunction (zFunctionLines):
	magic = []

	for lineNumber in Z_FUNCTION_MAGIC_LINES:
		magic.append(processZFunctionLine(zFunctionLines[lineNumber]))

	return magic

def processZFunctionLine (lineString):
	return int(lineString.strip().split(' ').pop().split('iconst_').pop())


####################################################################################
#|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|#
#|	STRING MANAGER																  |#
#|________________________________________________________________________________|#
####################################################################################

class StringManager:
	def __init__ (self):
		self.list = {}
		self.originals = {}
		self.unassembled = []

	def load (self, newList, newOriginals):
		self.list = newList
		self.originals = newOriginals

	def beginFile (self, fileName):
		self.currentFileName	= fileName
		self.inZFunction		= False
		self.zFunctionLines		= []
		self.justLoggedString	= False

		self.list[fileName] = {"magic": None, "strings": []}

	def logString (self, text):
		self.list[self.currentFileName]["strings"].append({"isEncrypted": False, "original": unicode(text)})
		self.justLoggedString = True

	def encryptedOrPlain (self, text):
		self.justLoggedString = False
		if Z_FUNCTION_CALL.match(text):
			self.list[self.currentFileName]["strings"][-1]["isEncrypted"] = True

	def currentStringIndex (self):
		return len(self.list[self.currentFileName]["strings"]) - 1

	def logZFunctionLine (self, line):
		self.zFunctionLines.append(line)

	def beginMethod (self, methodText):
		self.inZFunction = (methodText == Z_FUNCTION_SIGNATURE)

	def endMethod (self, methodText):
		if self.inZFunction:
			self.list[self.currentFileName]["magic"] = magicFromZFunction(self.zFunctionLines)
			self.zFunctionLines = []
			self.inZFunction = False

	def replaceString (self, fileName, stringIndex, newString):
		if not fileName in self.unassembled:
			self.unassembled.append(fileName)
		if not fileName in self.originals:
			self.originals[fileName] = {}
		if not stringIndex in self.originals[fileName]:
			self.originals[fileName][stringIndex] = dict(self.list[fileName]["strings"][stringIndex])
		
		if self.list[fileName]["strings"][stringIndex]["isEncrypted"]:
			sourceCodeString = xorString(newString, self.list[fileName]["magic"])
			self.list[fileName]["strings"][stringIndex]["decrypted"] = newString
			self.list[fileName]["strings"][stringIndex]["original"] = sourceCodeString
		else:
			sourceCodeString = newString
			self.list[fileName]["strings"][stringIndex]["original"] = newString

		return sourceCodeString

	def stringValue (self, fileName, stringIndex, original = False):
		if original:
			if "decrypted" in self.originals[fileName][stringIndex]:
				return self.originals[fileName][stringIndex]["decrypted"]
			return self.originals[fileName][stringIndex]["original"]
		else:
			if "decrypted" in self.list[fileName]["strings"][stringIndex]:
				return self.list[fileName]["strings"][stringIndex]["decrypted"]
			return self.list[fileName]["strings"][stringIndex]["original"]

	def decryptAllStrings (self):
		for fileName, fileData in self.list.iteritems():
			for stringIndex, loggedString in enumerate(fileData["strings"]):
				if loggedString["isEncrypted"]:
					self.list[fileName]["strings"][stringIndex]["decrypted"] = xorString(loggedString["original"], fileData["magic"])