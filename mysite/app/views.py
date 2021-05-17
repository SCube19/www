from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import User, File, Directory, Status, StatusData
from .forms import DirectoryForm, FileForm, acceptedProvers, acceptedFlags, LoginForm
from django.http import HttpResponseRedirect
from .helpers import makeDirectoryTree, setUnavailable, getResult, frama, parseSections, loggedCheck

# Create your views here.

#MAIN INDEX VIEW
def indexView(req):
    #these cant be non
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')
  
    context = {'provers': acceptedProvers}
    return render(req, "index.html", context)


#SHOW FILE ACTION VIEW
def showFile(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')
    #open file
    file = get_object_or_404(File, pk = req.GET.get('pk'))
    with open(file.fileField.path, 'r') as openedFile:
        code = list(openedFile)

    #make [(line, lineNum)] array for display
    code = [(code[i], i + 1) for i in range(len(code))]
    #run default frama-c and update status objects
    stats, statData, framaStringList = frama(File.objects.get(pk = req.GET.get('pk')), '')
    Status.objects.bulk_update(stats, ['status', 'lastUpdated'])
    StatusData.objects.bulk_update(statData, ['statusData', 'lastUpdated'])

    #dont ask for refresh
    data = {'code' : code, 'framaStringList' : framaStringList}
    return JsonResponse(data)

#ADD FILE VIEW
def addFileView(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')
    #getting input from POST
    form = FileForm(req.POST or None, req.FILES or None)
    form.fields["directory"].queryset = Directory.objects.filter(available = True, owner__login = req.session.get('loggedUser'))
    if form.is_valid():
        #produce sections and save to database
        file = form.save(commit = False)
        file.owner = User.objects.filter(login = req.session.get('loggedUser'))[0]
        file.save()
        parseSections(file)
        #ask for refresh
        return HttpResponseRedirect('/index/')

    context = {'form': form}
    return render(req, "addFile.html", context)  

#ADD DIRECTORY VIEW
def addDirectoryView(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')
    
    #getting input from form POST
    form = DirectoryForm(req.POST or None)
    form.fields["parentDirectory"].queryset = Directory.objects.filter(available = True, owner__login = req.session.get('loggedUser'))
    if form.is_valid():
        newDir = form.save(commit = False)
        newDir.owner = User.objects.filter(login = req.session.get('loggedUser'))[0]
        #assign appropriate level to new directory
        if newDir.parentDirectory == None:
            newDir.level = 0
        else:
            newDir.level = newDir.parentDirectory.level + 1
        newDir.save()
        #ask for refresh
        return HttpResponseRedirect('/index/')

    context = {'form': form}
    return render(req, "addDirectory.html", context)   

#DELETE DIRECTORY ACTION VIEW
def deleteDirectory(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')
    #set directories and files to unavailable
    directory = get_object_or_404(Directory, pk = req.GET.get('pk'))
    directories, files = setUnavailable(directory)
    #update them in database
    Directory.objects.bulk_update(directories, ['available'])
    File.objects.bulk_update(files, ['available'])

    return JsonResponse({})

#DELETE FILE ACTION VIEW
def deleteFile(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')
        
    #set to unavailable
    file = get_object_or_404(File, pk = req.GET.get('pk'))
    file.available = False
    file.save()

    return JsonResponse({})

#RUN FRAMA ADVANCED ACTION VIEW
def runFramaAdv(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')

    if req.GET.get('prover') not in acceptedProvers:
        return JsonResponse({'framaStringList': []})

    #accepted flags are stored as @flag and we check for either @flag or -@flag
    VCs = str(req.GET.get('flags')).split()
    for flag in VCs:
        if flag not in acceptedFlags and (len(flag) <= 1 or flag[0] != '-' or flag[1:] not in acceptedFlags):
            return JsonResponse({'framaStringList': []})

    try:
        flags = ''
        if req.GET.get('prover') != 'Default':
            flags = f"-wp-prover {req.GET.get('prover')}"
        if req.GET.get('enableRte') == True:
            flags = f'{flags} -wp-rte'
        if req.GET.get('flags') != '':
            flags = f"{flags} -wp-prop=\"{req.GET.get('flags')}\""      
    except:
        return JsonResponse({'framaStringList': []})

    #run frama with those flags and update new status data
    stats, statData, framaStringList = frama(File.objects.get(pk = req.GET.get('pk')), flags)
    Status.objects.bulk_update(stats, ['status', 'lastUpdated'])
    StatusData.objects.bulk_update(statData, ['statusData', 'lastUpdated'])

    return JsonResponse({'framaStringList' : framaStringList})
    

#ASSIGMENT 3 ========================================================================

def loginView(req):
    username = req.POST.get('login')
    password = req.POST.get('password')

    if username != None and password != None:
        if User.objects.filter(login = username, password = password).count() == 1:
            req.session['loggedUser'] = username
            return HttpResponseRedirect('/index/')
    else:
        form = LoginForm(req.POST or None)
        context = {'form' : form}
        return render(req, 'login.html', context)

def logout(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')

    req.session['loggedUser'] = None
    return HttpResponseRedirect('/login/')

def resultAction(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')

    result = getResult(File.objects.get(pk = req.GET.get('pk')).fileField.path)
    data = {'result' : result}
    return JsonResponse(data)

def makeFiles(req):
    if loggedCheck(req):
        return HttpResponseRedirect('/logout/')

    directories = makeDirectoryTree(req.session.get('loggedUser'))
    #[directory(pk, name, level), [files(pk, name)]] list
    directories = [[directory, [(file.pk, file.name) for file in Directory.objects.get(pk = directory[0]).file.filter(available = True).order_by('name')]]\
        for directory in directories]
    data = {'directories' : directories}
    return JsonResponse(data)