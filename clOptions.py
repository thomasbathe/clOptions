
# A function that takes a list of inputs (command line arguments)
# and a dictionary with possible options and corresponding default values
# the function parses the list for options
# a single hyphen indicates a single character option with true/false values and its value in the list will be toggled (options can be concatenated)
# a double hyphen indicates a multi character option that may be true or false, but can also have int, float or string values
#   if the option has a value (rather than being a bool) its dictionary entry itself is a dictionary containing its (default) value and its toggle status 
#   if a value is given, option and value are delimited by an equality sign 
#   if option and value are given, the toggle status will be set to True (rather than being toggled) (no concatenation of options possible)

import os
import sys
from pydoc import locate
from ast import literal_eval


class optionHandler:

  def __init__(self, args=None):

    self.__ScriptName = sys.argv[0].rsplit("/",1)[1]
    self.__ScriptPath = os.path.realpath(sys.argv[0]).rsplit("/",1)[0]
    if not args:
      self.__files = list(filter(lambda x: not x[0] == "-", sys.argv[1:]))
      self.__options = list(filter(lambda x: x[0] == "-", sys.argv[1:]))
    else:
      self.__files = list(filter(lambda x: not x[0] == "-", args))
      self.__options = list(filter(lambda x: x[0] == "-", args))

    self.__SettingsPath = "{}/.settings".format(self.__ScriptPath)

    self.__optionFile = "{0}/{1}_clOptions.conf".format(self.__SettingsPath, self.__ScriptName)
    self.__helpFile = "{0}/{1}_clOptions_help.txt".format(self.__SettingsPath, self.__ScriptName)

    self.__optionValues = {}
    self.__optionDescriptions = {}

    self.__readOptionDict()
    self.__getOptions()
    
    return

  def __getOptionList(self):

    optionList = []

    optionHistory = []

    while True:

      option = str(input("Option name?\n  ")).strip(" ") or None

      if not option:
        break

      if " " in option:
        option = option.replace(" ","")
        print('Warning: Given option name contains spaces. Changed to {0} instead!\n'.format(option))

      if option == "-h" or option == "--help" or option == "--init" or option == "--add" or option == "--remove" or option == "--set-default":
        print('Warning: Option "{0}" is reserved!'.format(option))
        continue

      if option in optionHistory or option in self.__optionValues:
        print("Warning: Option {0} already exists! Skipping Option.\n".format(option))
        continue

      if len(option) > 1 and not option[0] == "-":
        print("Warning: No option type indicator given!\n")
        continue



      if len(option) == 1:
        if option[0] == "-":
          print("Warning: No option name given!\n")
        else:
          print("Warning: No option type indicator given!\n")
        continue

      if len(option) > 2 and not option[1] == "-":
        print("Warning: Option name too long for single hyphen option!\n")
        continue


      if option[1] == "-":
        if len(option) == 3:
          print("Warning: Double hyphen option cannot be a single character!\n")
          continue

        status = input('\nDefault status for Option "{0}" (boolean)\n  '.format(option)) or False
        try:
          default_value = str(literal_eval(default_value))
        except:
          default_value = str(True)
        value = str(input('\nDefault value for Option "{0}"\n  '.format(option))) or None


        if value:
          default_value = "{0},{1}".format(status,value)
        else:
          default_value = status

      else:
        default_value = input('\nDefault status for Option "{0}" (boolean)\n  '.format(option)) or False
        try:
          default_value = str(literal_eval(default_value))
        except:
          default_value = str(True)

      description = str(input('\nDescription for Option "{0}"\n  '.format(option)) or "No description given!")

      optionLine = "{:<20}{:<30}          {:<25}\n".format(option, default_value, description)

      optionList.append(optionLine)
      optionHistory.append(option)

    return optionList

  def __setDefault(self, specificOption = None, removeOption = None, addOptions = False):

    if removeOption and not removeOption in self.__optionValues:
      exit('Error: {0} has no option "{1}"'.format(self.__ScriptName,removeOption))

    if os.path.exists(self.__helpFile):
      os.remove(self.__helpFile)


    with open(self.__optionFile,"r") as f:
      optionList = f.readlines()


    for i in range(len(optionList)):

      if addOptions:
        continue

      option, status, description = optionList[i].split(None, 2)

      if specificOption and not option == specificOption:
        continue


      if removeOption and not option == removeOption:
        continue
      elif removeOption and option == removeOption:
        optionList.pop(i)
        break

      description = description[:-1]

      value = None


      if len(status.split(",",1)) == 2:
        status, value = status.split(",",1)


      #if bool(input("Change Default status of {0}? (Current: {1})\n ".format(option,status)) or False):
      try:
        temp = input('New Default status of "{0}"?\n '.format(option))
        
        if temp == "":
          status = bool(literal_eval(status))
        else:
          status = bool(literal_eval(temp))
          
      except:
        status = bool(literal_eval(status))

      if value:

        #if bool(input("Change Default value of {0}? (Current: {1})\n ".format(option, value)) or False):
        value = str(input('New Default value of "{0}"?\n '.format(option))) or value

        status = "{0},{1}".format(status, value)


      #if bool(input("Change description of {0}?\n ".format(option)) or False):
      description = str(input('New description of "{0}"? ("" for no Description)\n '.format(option))) or description

      if description == " ":
        description = "No description given!"


      optionList[i] = "{:<20}{:<30}          {:<25}\n".format(option, str(status), description)

    if addOptions:
      optionList.extend(self.__getOptionList())

    
    optionList.sort()

    i = 0
    
    while optionList[i][1] == "-":
      i = i+1
      if i == len(optionList):
        break

    optionList = optionList[i:]+optionList[:i]


    with open(self.__optionFile, "w") as f:
      f.writelines(optionList)

    return

  def __createHelpFile(self):
    n = 50
    nDescr = 50

    with open(self.__optionFile,"r") as f:
      lines = f.readlines()

    lines.sort()

    i = 0
    
    while lines[i][1] == "-":
      i = i+1
      if i == len(lines):
        break

    lines = lines[i:]+lines[:i]

    helpList = ["{0:>{n}}        {1:<{nDescr}}".format("Option", "Description", n=n, nDescr=nDescr), "\n"]

    for line in lines:
      option, status, description = line.split(None, 2)
      
      if "No description given!" in description:
        description = ""


      if len(status.split(",",1)) == 2:
        status, value = status.split(",",1)
        
        if type(locate(value)) == type:
          valType = locate(value)
          defaultStr = "(Default: Status={0})".format(status)
        else:
          defaultStr = "(Default: Status={0}, Value={1})".format(status, value)

          try:
            valType = literal_eval(value)
          except:
            valType = ""
          valType = type(valType)

        option = "{0}={1}".format(option, valType)

      else:
        defaultStr = "(Default: Status={0})".format(status)

      if not len(description.split()) == 0:
        descrBlock = []
        description = description.split()
        wordLengths = list(map(lambda x: len(x), description))
        temp = []
        
        start = 0
        end = 0

        while True:
          counter = 0
          while True:
            if not end < len(description):
              break
            if counter+wordLengths[end] + (end-start) <= nDescr:
              counter = counter+wordLengths[end]
              end = end + 1
            else:
              break

          descrBlock.append("{0}".format(" ".join(description[start:end])))
          #end = end + 1
          start = end
          if end == len(description):
            break

        

        if len("{0} {1}".format(descrBlock[-1],defaultStr)) <= nDescr:
          descrBlock[-1] = "{0} {1}".format(descrBlock[-1],defaultStr)
        else:
          descrBlock.append(defaultStr)

      else:
        descrBlock = [defaultStr]

      helpList.append("\n{0:>{n}}        {1:<{nDescr}}\n".format(option, descrBlock[0], n=n, nDescr=nDescr))

      for i in range(1,len(descrBlock)):
        helpList.append("{0:>{n}}        {1:<{nDescr}}\n".format("", descrBlock[i], n=n, nDescr=nDescr))

    
    with open(self.__helpFile, "w") as f:
      f.writelines(helpList)

    return
      
  def __readOptionDict(self):
    
    if not os.path.exists(self.__optionFile):
      return


    with open(self.__optionFile, "r") as f:
      optionLines = f.readlines()

    for line in optionLines:
      option, value, description = line.split(None, 2)

      if option[0] == "-" and not option[1] == "-":
        self.__optionValues[option] = literal_eval(value)
        self.__optionDescriptions[option] = description
        continue

      if len(value.split(",",1)) == 1:
        self.__optionValues[option] = literal_eval(value)
        self.__optionDescriptions[option] = description
        continue

      status, val = value.split(",",1)

      if type(locate(val)) == type:
        val = locate(val)
      else:
        try:
          val = literal_eval(val)
        except:
          pass
      self.__optionValues[option] = {}
      self.__optionValues[option]["status"] = literal_eval(status)
      self.__optionValues[option]["value"] = val
      self.__optionDescriptions[option] = description
        
    return 

  def __initializeOptions(self):

    if not os.path.exists(self.__SettingsPath):
      os.mkdir(self.__SettingsPath)

    if os.path.exists(self.__helpFile):
      os.remove(self.__helpFile)

    if os.path.exists(self.__optionFile):
      self.__optionValues = {}
      self.__optionDescriptions = {}
      os.remove(self.__optionFile)

    optionList = self.__getOptionList()

    optionList.sort()

    if not len(optionList) == 0:
      i = 0
      
      while optionList[i][1] == "-":
        i = i+1
        if i == len(optionList):
          break

      optionList = optionList[i:]+optionList[:i]

    with open(self.__optionFile, "w") as f:
      f.writelines(optionList)

    return

  def __getOptions(self):
    #for i in range(1,len(clArguments)):
    # option = clArguments[i]

    if len(self.__options) == 0:
      return

    if self.__options[0] == "--init":
      self.__initializeOptions()
      exit(0)


    if len(self.__optionValues) == 0:
      exit('Error: No options found for {0}! Use "--init" to create an option dictionary!'.format(self.__ScriptName))

    if "--set-default" in self.__options[0]:
      
      if len(self.__options[0].split("=",1)) == 2:
        self.__setDefault(specificOption = self.__options[0].split("=",1)[1])
      else:
        self.__setDefault()
      exit(0)

    if "--remove" in self.__options[0]:
      self.__setDefault(removeOption=self.__options[0].split("=")[1])
      exit(0)

    if "--add" == self.__options[0]:
      if len(self.__options[0].split("=")) > 1:
        exit('Error: Option "--add" takes no arguments!')

      self.__setDefault(addOptions=True)
      exit(0)


    for option in self.__options:
      
      if option == "--help" or option == "-h":

        if not os.path.exists(self.__helpFile):
          self.__createHelpFile()

        with open(self.__helpFile,"r") as f:
          print("".join(f.readlines()))
        exit(0)

      # check if list element is an option
      if option[0] == "-":
        if len(option) == 1:   #list element is an option, but no option name given
          exit("Error: Missing option!")
        
        # check if list element is a single or double hyphen option
        else:
          if option[1] == "-":
            if len(option) == 2:  #list element is an option, but no option name given
              exit("Error: Missing option!")

            #option = option.replace("--","")

            # check if option exists in optionDict
            if not option.split("=")[0] in self.__optionValues:
              exit("Error: {0} has no option {1}!".format(self.__ScriptName, option))


            # check if a value was added to the double hyphen option
            if "=" in option:
              option, value = option.split("=")

              # check if option takes values
              if not type(self.__optionValues[option]) == dict:
                exit("Error: Option {0} takes no input Arguments!".format(option))

              # set toggle status to True
              self.__optionValues[option]["status"] = True
              
              # cast input value to needed type and set the value
              if type(self.__optionValues[option]["value"]) == type:
                self.__optionValues[option]["value"] = self.__optionValues[option]["value"](value)
              else:
                self.__optionValues[option]["value"] = type(self.__optionValues[option]["value"])(value)

            else:

              # check if option has a value
              if type(self.__optionValues[option]) == dict:

                # check if option has a default value set
                if type(self.__optionValues[option]["value"]) == type:
                  exit("Error: Option {0} has no default value!".format(option))
                  
                # toggle status of option with value
                else:
                  self.__optionValues[option]["status"] = not self.__optionValues[option]["status"]

              # toggle status of option without value
              else:
                self.__optionValues[option] = not self.__optionValues[option]

          # list element is a single hyphen option
          else:
            #option = option.replace("-","")

            # for every option in the concatenated option list check if option exists and then toggle its value
            for opt in option[1:]:
              opt = "-{0}".format(opt)
              if not opt in self.__optionValues:
                exit("Error: {0} has no option {1}!".format(self.__ScriptName, opt))
                
              self.__optionValues[opt] =  not self.__optionValues[opt]

    return


# Getter functions to access extracted files, option state, values (and the option dictionary)

  def getFiles(self):
    return self.__files

  def getState(self, option):
    if len(option) == 1:
      tmpOption = "-{}".format(option)
    else:
      tmpOption = "--{}".format(option)

    if not tmpOption in self.__optionValues:
      exit("Error: {0} has no option {1}!".format(self.__ScriptName, tmpOption))

    if len(option) == 1 or not type(self.__optionValues[tmpOption]) == dict:
      return self.__optionValues[tmpOption]
    else:
      return self.__optionValues[tmpOption]["status"]
      
      
  def getValue(self, option):
    if len(option) == 1:
      exit("Error: Single hyphen option cannot have a value!")
    tmpOption = "--{}".format(option)
    
    if not tmpOption in self.__optionValues:
      exit("Error: {0} has no option {1}!".format(self.__ScriptName, tmpOption))

    if not type(self.__optionValues[tmpOption]) == dict:
      exit("Error: {0} has no value".format(tmpOption))

    return self.__optionValues[tmpOption]["value"]    

  # def getOptions(self):
  #   return self.__optionValues
