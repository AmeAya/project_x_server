from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import *

admin.site.register(CodeModel)


@admin.register(CustomUserModel)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUserModel
    list_display = ('id', 'last_name', 'first_name', 'mail', 'phone', 'position', 'head_of_object', 'group')
    list_filter = ('position', 'id', )

    fieldsets = (
        (
            'Main', {
                'fields': ('phone', 'mail', 'first_name', 'last_name', 'iin', 'position')
            }
        ),
        (
            'Additional information', {
                'fields': ()
            }
        ),
        (
            'Permissions', {
                'fields': ('is_staff', 'is_active', 'groups')  # 'user_permissions')
            }
        )
    )
    add_fieldsets = (
        (
            'Main', {
                'classes': ('wide',),
                'fields': ('phone', 'mail', 'first_name', 'last_name', 'iin', 'position')
            }
        ),
        (
            'Permissions', {
                'fields': ('is_staff', 'is_active')
            }
        )
    )
    search_fields = ('phone',)
    ordering = ('phone', 'id')

    def head_of_object(self, obj):
        try:
            try:
                query = ObjectModel.objects.get(head_of_object=obj)
                return query.name
            except:
                query = ObjectModel.objects.get(staff=obj)
                return query.name
        except:
            return ' '

    def group(self, obj):
        try:
            if obj.is_superuser:
                query = obj.groups.all()
                return f'{query[0]}, {query[1]}, {query[2]}, {query[3]}'
            elif obj.groups.all()[0]:
                queri = obj.groups.all()
                return queri[0]
            else:
                return ' '
        except:
            return ' '

@admin.register(MaterialModel)
class MaterialNameAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")


@admin.register(PositionModel)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")


@admin.register(MarkModel)
class MarkAdmin(admin.ModelAdmin):
    list_display = ("name", "material", "author", "created_at", "updated_at")


@admin.register(ObjectModel)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "head_of_object", "created_at", "updated_at")
    filter_horizontal = ('staff', )


@admin.register(BlockModel)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "object", "author", "created_at", "updated_at")


# @admin.register(FloorModel)
# class FloorAdmin(admin.ModelAdmin):
#     list_display = ("name", "author", "created_at", "updated_at")
admin.site.register(FloorModel)


@admin.register(ConstructiveModel)
class ConstructiveNameAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "created_at", "updated_at")


@admin.register(UnitModel)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "created_at", "updated_at")


@admin.register(ProviderModel)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "created_at", "updated_at")


@admin.register(RecordsModel)
class RecordsAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "material", "mark", "object",
                    "get_block_name", "get_floor_name", "constructive",
                    "unit", "count", "user", "provider", "comments",
                    "created_at", "updated_at")
    filter_horizontal = ('block', "floor")

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field=from_field)
        request.report_obj = obj
        return obj

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'block' and getattr(self, 'obj', None):
            kwargs['queryset'] = BlockModel.objects.filter(name_object=request.report_obj.object)
        return super(RecordsAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(RecordsDeleteModel)


@admin.register(RecordsLogModel)
class LogRecords(admin.ModelAdmin):
    list_display = ("old_record", "new_record", "user")
