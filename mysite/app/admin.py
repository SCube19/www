from django.contrib import admin
from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData

# Register your models here.

admin.site.register(User)
admin.site.register(File)
admin.site.register(FileSection)
admin.site.register(Directory)
admin.site.register(SectionCategory)
admin.site.register(Status)
admin.site.register(StatusData)

