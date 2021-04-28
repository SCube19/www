from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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