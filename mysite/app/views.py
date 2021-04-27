from django.shortcuts import render, get_object_or_404
from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
from .forms import DirectoryForm, FileForm
from django.http import HttpResponse, HttpResponseRedirect
from .helpers import makeDirectoryTree, setUnavailable

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Create your views here.
def indexView(req, refresh = 0):
    if refresh != 0 or req.session.get('directories') == None:
        directories = makeDirectoryTree()
        directories = [[directory, [(file.pk, file.name) for file in Directory.objects.get(pk = directory[0]).file.filter(available = True).order_by('name')]] for directory in directories]
        req.session['directories'] = directories
        logger.warn(directories)
    else:
        directories = req.session.get('directories')

    active = [False, False, False]
    if req.session.get('tabNum') == None:
        req.session['tabNum'] = 0
        active[0] = True
    else:
        active[req.session.get('tabNum')] = True

    context = {'directories' : directories, 'code': req.session.get('code'), 'active' : active}
    return render(req, "index.html", context)

def showFile(req, id):
    file = get_object_or_404(File, pk = id)
    with open(file.fileField.path, 'r') as openedFile:
        code = list(openedFile)
    code = [(code[i], i + 1) for i in range(len(code))]
    req.session['code'] = code
    req.session['codeiD'] = id

    return HttpResponseRedirect('/index/0')

def addFileView(req):
    form = FileForm(req.POST or None, req.FILES or None)
    form.fields["directory"].queryset = Directory.objects.filter(available = True)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/index/1')

    context = {'form': form}
    return render(req, "addFile.html", context)  

def addDirectoryView(req):
    form = DirectoryForm(req.POST or None)
    form.fields["parentDirectory"].queryset = Directory.objects.filter(available = True)
    if form.is_valid():
        newDir = form.save(commit = False)
        if newDir.parentDirectory == None:
            newDir.level = 0
        else:
            newDir.level = newDir.parentDirectory.level + 1
        newDir.save()
        return HttpResponseRedirect('/index/1')

    context = {'form': form}
    return render(req, "addDirectory.html", context)   

def deleteView(req):
    context = {'directories' : req.session.get('directories')}
    return render(req, "delete.html", context)

def deleteDirectory(req, id):
    directory = get_object_or_404(Directory, pk = id)
    directories, files = setUnavailable(directory)
    Directory.objects.bulk_update(directories, ['available'])
    File.objects.bulk_update(files, ['available'])

    if req.session.get('codeid') != None and \
        File.objects.get(pk = req.session.get('codeId')) != None \
        and File.objects.get(pk = req.session.get('codeId')).available == False:
        req.session['codeId'] = None

    return HttpResponseRedirect('/index/1')

def deleteFile(req, id):
    file = get_object_or_404(File, pk = id)
    file.available = False
    file.save()

    if req.session.get('codeid') != None and \
        File.objects.get(pk = req.session.get('codeId')) != None \
        and File.objects.get(pk = req.session.get('codeId')).available == False:
        req.session['codeId'] = None

    return HttpResponseRedirect('/index/1')

def changeTab(req, tabNum):
    req.session['tabNum'] = tabNum
    return HttpResponseRedirect('/index/0/')
