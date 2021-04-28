from django.shortcuts import render, get_object_or_404
from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
from .forms import DirectoryForm, FileForm, acceptedProvers, acceptedFlags
from django.http import HttpResponse, HttpResponseRedirect
from .helpers import makeDirectoryTree, setUnavailable, getResult

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Create your views here.
def indexView(req, refresh = 0):
    if req.session.get('enableRte') == None:
        req.session['enableRte'] = False
    if req.session.get('flags') == None:
        req.session['flags'] = ""

    #if someone changed database we should update display stucture to avoid unnecesary computation
    if refresh != 0 or req.session.get('directories') == None:
        directories = makeDirectoryTree()
        #[directory(pk, name, level), [files(pk, name)]] list
        directories = [[directory, [(file.pk, file.name) for file in Directory.objects.get(pk = directory[0]).file.filter(available = True).order_by('name')]]\
             for directory in directories]
        req.session['directories'] = directories
        logger.warn(directories)
    else:
        directories = req.session.get('directories')

    #get active tab
    active = [False, False, False]
    if req.session.get('tabNum') == None:
        req.session['tabNum'] = 0
        active[0] = True
    else:
        active[req.session.get('tabNum')] = True
    
    #make context out of directories, opened file, active tabs
    context = {'directories' : directories, 'code': req.session.get('code'), 'active'\
         : active, 'provers': acceptedProvers, 'result': req.session.get('result'), \
             'currProver': "Default" if req.session.get('prover') == None else req.session.get('prover'), 'rte': req.session['enableRte'],\
             'currFlags': req.session['flags']}
    return render(req, "index.html", context)

def showFile(req, id):
    #open file
    file = get_object_or_404(File, pk = id)
    with open(file.fileField.path, 'r') as openedFile:
        code = list(openedFile)
    #make [(line, lineNum)] array for display
    code = [(code[i], i + 1) for i in range(len(code))]

    #save it in session to avoid unnecesary computation
    req.session['code'] = code
    req.session['codeId'] = id
    #dont ask for refresh
    return HttpResponseRedirect('/index/0')

def addFileView(req):
    #getting input from form POST
    form = FileForm(req.POST or None, req.FILES or None)
    form.fields["directory"].queryset = Directory.objects.filter(available = True)
    if form.is_valid():
        form.save()
        #ask for refresh
        return HttpResponseRedirect('/index/1')

    context = {'form': form}
    return render(req, "addFile.html", context)  

def addDirectoryView(req):
    #getting input from form POST
    form = DirectoryForm(req.POST or None)
    form.fields["parentDirectory"].queryset = Directory.objects.filter(available = True)
    if form.is_valid():
        newDir = form.save(commit = False)
        #assign appropriate level to new directory
        if newDir.parentDirectory == None:
            newDir.level = 0
        else:
            newDir.level = newDir.parentDirectory.level + 1
        newDir.save()
        #ask for refresh
        return HttpResponseRedirect('/index/1')

    context = {'form': form}
    return render(req, "addDirectory.html", context)   

def deleteView(req):
    #get dirs from session
    context = {'directories' : req.session.get('directories')}
    return render(req, "delete.html", context)

def deleteDirectory(req, id):
    #set directories and files to unavailable
    directory = get_object_or_404(Directory, pk = id)
    directories, files = setUnavailable(directory)
    #update them in database
    Directory.objects.bulk_update(directories, ['available'])
    File.objects.bulk_update(files, ['available'])

    #check if we deleted file stored in session
    if req.session.get('codeId') != None and \
        File.objects.get(pk = req.session.get('codeId')) != None \
        and File.objects.get(pk = req.session.get('codeId')).available == False:
        req.session['codeId'] = None

    return HttpResponseRedirect('/index/1')

def deleteFile(req, id):
    #set to unavailable
    file = get_object_or_404(File, pk = id)
    file.available = False
    file.save()

    #check if we deleted file stored in session
    if req.session.get('codeId') != None and \
        File.objects.get(pk = req.session.get('codeId')) != None \
        and File.objects.get(pk = req.session.get('codeId')).available == False:
        req.session['codeId'] = None

    return HttpResponseRedirect('/index/1')

def changeTab(req, tabNum):
    req.session['tabNum'] = tabNum
    if tabNum == 2:
        if req.session.get('codeId') != None:
            req.session['result'] = getResult(File.objects.get(pk = req.session.get('codeId')).fileField.path)
        else:
            req.session['result'] = ""

    return HttpResponseRedirect('/index/0/')

def resetFile(req):
    req.session['code'] = None
    req.session['codeId'] = None
    return HttpResponseRedirect('/index/0/')

def chooseProver(req):
    if req.method == 'POST':
        chosenProver = req.POST.get('chosenProver')
        logger.warn(chosenProver)
        if chosenProver == 'Default' or chosenProver == None:
            req.session['prover'] = None
        else:
            req.session['prover'] = chosenProver
    return HttpResponseRedirect('/index/0/') 

def setFlags(req):
    if req.method == 'POST':
        req.session['enableRte'] = (req.POST.get('enable') == 'on')

        flags = str(req.POST.get('flags')).split()
        for flag in flags:
            if flag not in acceptedFlags:
                return HttpResponseRedirect('/index/0')

        req.session['flags'] = req.POST.get('flags')

    return HttpResponseRedirect('/index/0')

def runFrama(req, fileId):
    pass
    
