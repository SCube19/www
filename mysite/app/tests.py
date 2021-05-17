from django import setup
from django.test import TestCase, Client, client
from .models import Status, User, Directory, File, SectionCategory, StatusData, Status, FileSection
import pytz
import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import FileForm, DirectoryForm, LoginForm, acceptedProvers
from django.urls import reverse
from .helpers import parseSections
import json

utc = pytz.UTC

class ModelTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create(
            name = 'Konrad',
            login = 'knrd',
            password = '12344'
        )
        parDirectory = Directory.objects.create(
            name = 'TestParent',
            description = 'descript',
            owner = user,
            level = 0
        )
        childDir1 = Directory.objects.create(
            name = 'TestChild1',
            description = 'descript',
            owner = user,
            level = 1,
            parentDirectory = parDirectory
        )
        childDir2= Directory.objects.create(
            name = 'TestChild2',
            description = 'descript',
            owner = user,
            level = 1,
            parentDirectory = parDirectory
        )

        file1 = File.objects.create(
            name = 'testfile1',
            description = 'descr',
            owner = user,
            directory = parDirectory,
            fileField = SimpleUploadedFile('testfile.txt', b'somet')
        )
        file2 = File.objects.create(
            name = 'testfile2',
            description = 'descr',
            owner = user,
            directory = parDirectory,
            fileField = SimpleUploadedFile('testfile.txt', b'some')
        )

        sCategory = SectionCategory.objects.create(
            category = 'requires'
        )

        status = Status.objects.create(
            status = 'Valid'
        )
        sData = StatusData.objects.create(
            statusData = 'somedata',
            user = user
        )

        sCategory1 = SectionCategory.objects.create(
            category = 'ensures'
        )

        status1 = Status.objects.create(
            status = 'Invalid'
        )
        sData1 = StatusData.objects.create(
            statusData = 'somedata1',
            user = user
        )

        fileSection1 = FileSection.objects.create(
            name = 'somename1',
            description = 'desc',
            category = sCategory,
            status = status,
            statusData = sData,
            fileKey = file1,
            sectionEnd = 8
        )
        fileSection2 = FileSection.objects.create(
            name = 'somename2',
            description = 'desc',
            category = sCategory1,
            status = status1,
            statusData = sData1,
            fileKey = file1,
            sectionBegin = 2
        )
    
    def testUser(self):
        test = User.objects.get(login = 'knrd')
        self.assertEqual(test.name, 'Konrad')
        self.assertEqual(test.password, '12344')

    def testDirectory(self):
        test = Directory.objects.get(name = 'TestParent')
        self.assertEqual(test.description, 'descript')
        self.assertEqual(test.level, 0)
        self.assertEqual(test.available, True)
        self.assertEqual(test.parentDirectory, None)

    def testFile(self):
        test = File.objects.get(name = 'testfile1')
        self.assertEqual(test.description, 'descr')
        self.assertEqual(getattr(test.directory, 'name'), 'TestParent')
        self.assertEqual(getattr(test.fileField, 'size'), 5)
        self.assertEqual(test.available, True)

    def testSectionCategory(self):
        test = SectionCategory.objects.filter(category = 'requires')
        counter = 0
        for entry in test:
            if entry.lastUpdated >= utc.localize(datetime.datetime.now() - datetime.timedelta(seconds = 5)):
                counter += 1
        self.assertEqual(counter > 0, True)

    def testStatus(self):
        test = Status.objects.filter(status = 'Valid')
        counter = 0
        for entry in test:
            if entry.lastUpdated >= utc.localize(datetime.datetime.now() - datetime.timedelta(seconds = 5)):
                counter += 1
        self.assertEqual(counter > 0, True)

    def testStatusData(self):
        test = StatusData.objects.filter(statusData = 'somedata').order_by('lastUpdated')[0]
        self.assertEqual(getattr(test.user, 'login'), 'knrd')

    def testFileSection(self):   
        test = FileSection.objects.filter(name = 'somename1').order_by('creationDate')[0]
        self.assertEqual(test.description, 'desc')
        self.assertEqual(test.sectionBegin, -1)
        self.assertEqual(test.sectionEnd, 8)
    
    def testUserDirectory(self):
        test = Directory.objects.get(name = 'TestParent')
        self.assertEqual(getattr(test.owner, 'login'), 'knrd')

    def testDirectoryDirectory(self):
        test = Directory.objects.get(name = 'TestParent')
        children = test.child.all().order_by('name')
        self.assertEqual(children.count(), 2)
        self.assertEqual(children[0].name, 'TestChild1')
        self.assertEqual(children[1].name, 'TestChild2')

    def testDirectoryFile(self):
        test = Directory.objects.get(name = 'TestParent')
        children = test.file.all().order_by('name')
        self.assertEqual(children.count(), 2)
        self.assertEqual(children[0].name, 'testfile1')
        self.assertEqual(children[1].name, 'testfile2')

    def testUserFile(self):
        test = File.objects.get(name = 'testfile1')
        self.assertEqual(getattr(test.owner, 'login'), 'knrd')

    def testFileSectionFile(self):
        test = File.objects.get(name = 'testfile1')
        children = test.fsection.all().order_by('name')
        self.assertEqual(children.count(), 2)
        self.assertEqual(children[0].name, 'somename1')
        self.assertEqual(children[1].name, 'somename2')
        self.assertEqual(getattr(children[0].fileKey, 'description'), 'descr')

    def testFileSectionSmaller(self): 
        test = FileSection.objects.filter(name = 'somename1').order_by('creationDate')[0]
        self.assertEqual(getattr(test.category, 'category'), 'requires')
        self.assertEqual(getattr(test.status, 'status'), 'Valid')
        self.assertEqual(getattr(test.statusData, 'statusData'), 'somedata')



class ViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.session = self.client.session
        self.session['loggedUser'] = 'testUser'
        self.session.save()

        self.testUser = User.objects.create(
            login = 'testUser',
            password = '123'
        )
        self.testDir = Directory.objects.create(
            name = "testDir",
            description = 'desc',
            parentDirectory = None,
            owner = self.testUser,
            level = 0
        )
        self.testFile = File.objects.create(
            name = 'testFile',
            description = 'desc',
            fileField = SimpleUploadedFile('testShow.txt', b'something\n something else'),
            directory = self.testDir,
            owner = self.testUser
        )
        self.maxDiff = None

    def testIndex(self):
        response = self.client.get('/index/')
        self.assertEqual(response.context['provers'] == acceptedProvers, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def testShowFile(self):
        response = self.client.get('/showFile/', data = {'pk' : self.testFile.pk})
        content = json.loads(response.content)
        self.assertEqual(content['code'], [["something\n", 1], [" something else", 2]])

    def testAddFile(self):
        response = self.client.get('/addFile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addFile.html')

    def testAddDirectory(self):
        response = self.client.get('/addDirectory/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addDirectory.html')

    def testDeleteDirectory(self):
        child = Directory.objects.create(
            name = "testDi1r",
            description = 'desc',
            parentDirectory = self.testDir,
            owner = self.testUser,
            level = 1
        )
        response = self.client.get('/deleteDirectory/', data = {'pk' : self.testDir.pk})
        content = json.loads(response.content)
        self.assertEqual('testDir' == content['directories'][0][0], True)
        self.assertEqual('testFile' == content['files'][0][0], True)
        self.assertEqual('testDi1r' == content['directories'][1][0], True)
        self.assertEqual(content['directories'][0][1], False)
        self.assertEqual(content['directories'][1][1], False)
        self.assertEqual(content['files'][0][1], False)

    def testDeleteFile(self):
        self.testFile.available = True
        response = self.client.get('/deleteFile/', data = {'pk' : self.testFile.pk})
        content = json.loads(response.content)
        self.assertEqual('testFile' == content['file'][0], True)
        self.assertEqual(content['file'][1], False)
        
    def testRunFramaAdv(self):
        response = self.client.get('/runFrama/', data = {'pk' : self.testFile.pk, 'prover' : 'CVC4', 'VCs' : 'cos niedobrego', 'enableRte' : True})
        content = json.loads(response.content)
        self.assertEqual(content['framaStringList'], [])

    def testLogin(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def testLogout(self):
        response = self.client.get('/logout/')
        self.assertEqual(self.client.session['loggedUser'], None)
        self.assertEqual(response.status_code, 302)
        self.session = self.client.session
        self.session['loggedUser'] = 'testUser'
        self.session.save()

    def testResultAction(self):
        response = self.client.get('/resultAction/', data = {'pk' : self.testFile.pk})
        content = json.loads(response.content)
        self.assertEqual(content['result'], '[wp] Proved goals:    0 / 0\n')

    def testMakeFiles(self):
        response = self.client.get('/makeFiles/')
        content = json.loads(response.content)
        self.assertEqual(content['directories'], [[[1, 'testDir', 0], [[1, 'testFile']]]])

class FormTest(TestCase):
    def setUp(self) -> None:
        self.testUser = User.objects.create(
            login = 'testUser',
            password = '123'
        )
        self.testDir = Directory.objects.create(
            name = "testDir",
            description = 'desc',
            parentDirectory = None,
            owner = self.testUser
        )
        self.testFile = File.objects.create(
            name = 'testFile',
            description = 'desc',
            fileField = SimpleUploadedFile('testfile.txt', b'xxxxx'),
            directory = self.testDir,
            owner = self.testUser
        )

    def testLoginForm(self):
        form = LoginForm(data = {'login' : self.testUser.login, 'password' : self.testUser.password})
        self.assertEqual(form.data['login'], 'testUser')
        self.assertEqual(form.data['password'], '123')

    def testFileForm(self):
        form = FileForm(data = {'name' : self.testFile.name, 'description' : self.testFile.description, 'fileField' : self.testFile.fileField, 'directory' : self.testFile.directory})
        self.assertEqual(form.data['name'], 'testFile')
        self.assertEqual(form.data['description'], 'desc')
        self.assertEqual(getattr(form.data['fileField'], 'size'), 5)
        self.assertEqual(getattr(form.data['directory'], 'name'), 'testDir')

    def testDirectoryForm(self):
        form = FileForm(data = {'name' : self.testDir.name, 'description' : self.testDir.description, 'parentDirectory' : self.testDir.parentDirectory})
        self.assertEqual(form.data['name'], 'testDir')
        self.assertEqual(form.data['description'], 'desc')
        self.assertEqual(form.data['parentDirectory'], None)

