from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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


def getResult(filePath):
    resultPath = filePath[:filePath.rfind('/')] + '/result.txt'
    os.system(f'frama-c -wp -wp-log="r:{resultPath}" {filePath}') 
    return os.popen(f'cat {resultPath}').read()


def makeSectionRelatives(bulks, lineSplit, owner):
    cat = SectionCategory(category = lineSplit[2] if lineSplit[1] == 'loop' else lineSplit[1])
    stat = Status()
    statData = StatusData(user = owner)
    bulks[1].append(cat)
    bulks[2].append(stat)
    bulks[3].append(statData)

def makeSection(bulks, content, lineNum, file):
    if content[lineNum].find('@*/') != -1:
        return lineNum, True

    begNum = lineNum
    makeSectionRelatives(bulks, content[lineNum].split(), file.owner)
    
    lineNum += 1
    if content[lineNum - 1].find("*/") == -1:
        atIndex = content[lineNum].find('@')
        while lineNum < len(content) and content[lineNum].find("*/") == -1 and\
             (len(content[lineNum]) - atIndex < 2 or content[lineNum][atIndex + 1] != ' ' or not content[lineNum][atIndex + 2].isalpha()) :
            lineNum += 1
            atIndex = content[lineNum].find('@')

    fileSection = FileSection(name = '', description = '', fileKey = file, sectionBegin = begNum, sectionEnd = lineNum - 1)
    bulks[0].append(fileSection)

    return lineNum, content[lineNum - 1].find("*/") != -1


def parseSections(file):
    with open(file.fileField.path, 'r') as opened:
        content = list(opened)
    bulks = [[],[],[],[]]

    for lineNum in range(len(content)):
        #works
        if content[lineNum].find("/*@") == -1:
            continue

        while True:
            lineNum, end = makeSection(bulks, content, lineNum, file)
            if end:
                break

    for lineNum in range(len(content)):
        if content[lineNum].find("//@") == -1:
            continue

        makeSectionRelatives(bulks, content[lineNum].split(), file.owner)
        fileSection = FileSection(name = '', description = '', statusData = statData, fileKey = file, sectionBegin = lineNum, sectionEnd = lineNum)
        bulks[0].append(fileSection)

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
    
    print(file.fsection.all())

def frama(file, flags):
    print(f'frama-c -wp -wp-print {flags} {file.fileField.path}')
    framaDelimeter = "------------------------------------------------------------\n"
    framaOutput = os.popen(f'frama-c -wp -wp-print {flags} {file.fileField.path}').read().split(framaDelimeter)

    stringStructure = []
    returnStats = []
    returnStatData = []
    print(len(framaOutput))
    if len(framaOutput) < 3 :
        stringStructure.append([framaOutput[0], statusColorConv.get('Neutral'), 'Nothing provided'])
        
        for fileSection in file.fsection.all():
            fileSection.statusData.statusData = ""
            fileSection.status.status = ""
            returnStatData.append(fileSection.statusData)
            returnStats.append(fileSection.status)
        return returnStats, returnStatData, stringStructure
    
    alreadyParsedLines = set()

    for out in framaOutput[1:]:
        if out.find("Function") != -1:
            stringStructure.append([out, statusColorConv.get('Neutral'), out.split()[1]])
            continue
        try:
            lineNum = out[(out.find('line') + 4):].split()[0]
            lineNum = int(lineNum[:lineNum.find(")")]) - 1
        except:
            continue

        status = out[(out.rfind('returns') + 7):].split()[0]

        if lineNum not in alreadyParsedLines:
            try:
                fileSection = file.fsection.all().get(sectionBegin = lineNum)
            except:
                continue

            fileSection.statusData.statusData = out
            fileSection.status.status = status

            returnStats.append(fileSection.status)
            returnStatData.append(fileSection.statusData)
            alreadyParsedLines.add(lineNum)
            stringStructure.append([out, statusColorConv.get(status), f"{fileSection.category.category}->({fileSection.sectionBegin + 1}-{fileSection.sectionEnd + 1})"])
        else:
            stringStructure.append([out, statusColorConv.get(status), f'line {lineNum + 1}'])

    return returnStats, returnStatData, stringStructure