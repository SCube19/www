from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length = 50)
    login = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 30)
    lastUpdated = models.DateTimeField(auto_now = True)
    validity = models.BooleanField(default = True)

    def __str__(self):
        return self.login
    

class Directory(models.Model):
    name = models.CharField(unique = True, max_length = 50)
    description = models.CharField(max_length = 1000, blank = True)
    creationDate = models.DateTimeField(auto_now = True)
    owner = models.ForeignKey(User, on_delete = models.CASCADE)
    available = models.BooleanField(default = True)
    parentDirectory = models.ForeignKey('self', on_delete = models.CASCADE, null = True, blank = True, related_name = 'child')
    lastUpdated = models.DateTimeField(auto_now = True)
    validity = models.BooleanField(default = True)

    level = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return self.name
    

class File(models.Model):
    name = models.CharField(unique = True, max_length = 50)
    description = models.CharField(max_length = 1000, blank = True)
    creationDate = models.DateTimeField(auto_now = True)
    owner = models.ForeignKey(User, on_delete = models.CASCADE)
    available = models.BooleanField(default = True)
    directory = models.ForeignKey(Directory, on_delete = models.CASCADE, related_name = 'file')
    fileField = models.FileField()
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SectionCategory(models.Model):
    category = models.CharField(max_length = 50)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return self.category
    
class Status(models.Model):
    status = models.CharField(default="", max_length = 30, blank = True)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)
    
class StatusData(models.Model):
    statusData = models.CharField(default = "", max_length = 1000, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    
class FileSection(models.Model):
    name = models.CharField(blank = True, default = "", max_length = 50)
    description = models.CharField(max_length = 1000, blank = True, default = "")
    creationDate = models.DateTimeField(auto_now = True)
    category = models.OneToOneField(SectionCategory, on_delete = models.CASCADE, null = True, blank = True)
    status = models.OneToOneField(Status, on_delete = models.CASCADE, null = True, blank = True)
    statusData = models.OneToOneField(StatusData, on_delete = models.CASCADE, null = True, blank = True)
    fileKey = models.ForeignKey(File, on_delete = models.CASCADE, related_name = 'fsection')
    sectionBegin = models.IntegerField(default = -1)
    sectionEnd = models.IntegerField(default = -1)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return self.category.category

