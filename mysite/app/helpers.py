from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
import logging
import os

#coloring of sections later change to css variables
statusColorConv = {
    'Neutral' : '',
    'Unknown' : '#999999',
    'Valid' : '#34ca84',
    'Timeout' : '#347aca',
    'Failed' : '#cc1423'
}

#recursively adds directories to returnDirs to make filetree structure later
def nextLevel(parent, returnDirs):
    children = parent.child.filter(available = True).order_by('name')
    for child in children:
        returnDirs.append([child.pk, child.name, child.level])
        nextLevel(child, returnDirs)


#finds level 0 directories and then recursively makes list out of their children to make file tree structure
def makeDirectoryTree():
    directories = Directory.objects.filter(available = True).order_by('name')

    #find 0 level directories
    zeroDirs = []
    for directory in directories:
        if directory.level == 0:
            zeroDirs.append(directory)

    #add their children in good order
    returnDirs = []
    for zeroDir in zeroDirs:
        returnDirs.append([zeroDir.pk, zeroDir.name, zeroDir.level])
        nextLevel(zeroDir, returnDirs)

    return returnDirs


#recursively sets directory and its children and files to unavailable and returns changed fields
def setUnavailable(directory):
    #set yourself to unavailable
    directory.available = False
    returnDirs = [directory]
    returnFiles = []

    #set your files to unavailable
    for file in directory.file.filter(available = True):
        file.available = False
        returnFiles.append(file)

    #set your children to unavailable recursively
    for child in directory.child.filter(available = True):
        recDirs, recFiles = setUnavailable(child)
        returnDirs += recDirs
        returnFiles += recFiles

    return returnDirs, returnFiles

#runs frama for RESULT tab
def getResult(filePath):
    resultPath = filePath[:filePath.rfind('/')] + '/result.txt'
    os.system(f'frama-c -wp -wp-log="r:{resultPath}" {filePath}') 
    return os.popen(f'cat {resultPath}').read()

#saves Category, Status, StatusData objects in bulks (used in makeSection and parseSections)
def makeSectionRelatives(bulks, lineSplit, owner):
    #if section starts with loop keyword we choose second
    cat = SectionCategory(category = lineSplit[2] if lineSplit[1] == 'loop' else lineSplit[1])
    stat = Status()
    statData = StatusData(user = owner)
    bulks[1].append(cat)
    bulks[2].append(stat)
    bulks[3].append(statData)

#makes one section and saves it in bulks (used in parseSections)
def makeSection(bulks, content, lineNum, file):
    #end comment found 
    if content[lineNum].find('@*/') != -1:
        return lineNum, True

    begNum = lineNum
    makeSectionRelatives(bulks, content[lineNum].split(), file.owner)
    
    #skip lines to next section
    #as section is undefined in assigment i defined start of section as [@(space)something ....]
    #it checks if end of comment or new section is present
    lineNum += 1
    if content[lineNum - 1].find("*/") == -1:
        atIndex = content[lineNum].find('@')
        while lineNum < len(content) and content[lineNum].find("*/") == -1 and\
             (len(content[lineNum]) - atIndex < 2 or content[lineNum][atIndex + 1] != ' ' or not content[lineNum][atIndex + 2].isalpha()) :
            lineNum += 1
            atIndex = content[lineNum].find('@')

    #save new fileSection in bulks
    fileSection = FileSection(name = '', description = '', fileKey = file, sectionBegin = begNum, sectionEnd = lineNum - 1)
    bulks[0].append(fileSection)

    #lineNum changed and if end indicator
    return lineNum, content[lineNum - 1].find("*/") != -1


def parseSections(file):
    with open(file.fileField.path, 'r') as opened:
        content = list(opened)
    #bulks for new objects
    bulks = [[],[],[],[]]

    #iterating through file 
    for lineNum in range(len(content)):
        #find start of frama comment
        if content[lineNum].find("/*@") == -1:
            continue
        
        #make sections until end of the comment
        while True:
            lineNum, end = makeSection(bulks, content, lineNum, file)
            if end:
                break
    
    #//@ comments handler
    for lineNum in range(len(content)):
        if content[lineNum].find("//@") == -1:
            continue

        makeSectionRelatives(bulks, content[lineNum].split(), file.owner)
        fileSection = FileSection(name = '', description = '', statusData = statData, fileKey = file, sectionBegin = lineNum, sectionEnd = lineNum)
        bulks[0].append(fileSection)

    #save data (unoptimal later change to bulk_create with custom pk)
    for cat in bulks[1]:
        cat.save()
    for stat in bulks[2]:
        stat.save()
    for statData in bulks[3]:
        statData.save()

    for i in range(len(bulks[1])):
        bulks[0][i].category = bulks[1][i]
        bulks[0][i].status = bulks[2][i]
        bulks[0][i].statusData = bulks[3][i]
        bulks[0][i].save()

#runs frama and return status, statusData and stringStructure for display
def frama(file, flags):
    #run frama with given flags
    print(f'frama-c -wp -wp-print {flags} {file.fileField.path}')
    #frama uses it as delimeter to print sections
    framaDelimeter = "------------------------------------------------------------\n"
    framaOutput = os.popen(f'frama-c -wp -wp-print {flags} {file.fileField.path}').read().split(framaDelimeter)

    #return values
    stringStructure = []
    returnStats = []
    returnStatData = []
    
    #split makes empty string at the end and first log section is also in a list 
    #so if we have 2 elements in a list then we have only log section so nothing was scheduled
    if len(framaOutput) < 3 :
        stringStructure.append([framaOutput[0], statusColorConv.get('Neutral'), 'Nothing provided'])
        #update statuses to none
        for fileSection in file.fsection.all():
            fileSection.statusData.statusData = ""
            fileSection.status.status = ""
            returnStatData.append(fileSection.statusData)
            returnStats.append(fileSection.status)
        return returnStats, returnStatData, stringStructure
    
    #as frama prints same line info multiple times we choose first output to save in database
    alreadyParsedLines = set()


    #ignore log section
    startFound = False
    for out in framaOutput[1:]:
        #find Function keyword
        if out.find("Function") != -1:
            stringStructure.append([out, statusColorConv.get('Neutral'), out.split()[1]])
            startFound = True
            continue
        elif not startFound:
            continue
        #try to find line keyword 
        try:
            lineNum = out[(out.find('line') + 4):].split()[0]
            lineNum = int(lineNum[:lineNum.find(")")]) - 1
        except:
            continue
        
        #find returned status 
        status = out[(out.rfind('returns') + 7):].split()[0]

        #if we parsed that line we only append section string to stringStructure
        if lineNum not in alreadyParsedLines:
            #try to find correspoding filesection
            try:
                fileSection = file.fsection.all().get(sectionBegin = lineNum)
            except:
                continue
            #update data and append lists
            fileSection.statusData.statusData = out
            fileSection.status.status = status
            returnStats.append(fileSection.status)
            returnStatData.append(fileSection.statusData)
            alreadyParsedLines.add(lineNum)
            stringStructure.append([out, statusColorConv.get(status), f"{fileSection.category.category}->({fileSection.sectionBegin + 1}-{fileSection.sectionEnd + 1})"])
        else:
            stringStructure.append([out, statusColorConv.get(status), f'line {lineNum + 1}'])

    return returnStats, returnStatData, stringStructure