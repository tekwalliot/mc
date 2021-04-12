from django.contrib import admin


from .models import SiteDetails, SiteData


from import_export.admin import ImportExportModelAdmin

#admin.site.register(pumpInstData)

# Register your models here.



@admin.register(SiteDetails)
@admin.register(SiteData)





class SiteDetailsAdmin(ImportExportModelAdmin):
	pass

class SiteDataAdmin(ImportExportModelAdmin):
	pass

