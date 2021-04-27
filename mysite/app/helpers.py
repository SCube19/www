from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def nextLevel(parent, returnDirs):
    children = parent.child.filter(available = True).order_by('name')
    for child in children:
        returnDirs.append([child.pk, child.name, child.level])
        nextLevel(child, returnDirs)

def makeDirectoryTree():
    directories = Directory.objects.filter(available = True).order_by('name')

    zeroDirs = []
    for directory in directories:
        if directory.level == 0:
            zeroDirs.append(directory)

    returnDirs = []
    for zeroDir in zeroDirs:
        returnDirs.append([zeroDir.pk, zeroDir.name, zeroDir.level])
        nextLevel(zeroDir, returnDirs)

    return returnDirs


def setUnavailable(directory):
    directory.available = False
    returnDirs = [directory]
    returnFiles = []
    for file in directory.file.filter(available = True):
        file.available = False
        returnFiles.append(file)

    for child in directory.child.filter(available = True):
        recDirs, recFiles = setUnavailable(child)
        returnDirs += recDirs
        returnFiles += recFiles

    return returnDirs, returnFiles