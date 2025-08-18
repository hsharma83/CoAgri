# farm/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Zone, Farmland, Plot, Role, Staff, Crop, FarmPlan, FarmPlanStep,
    Category, Activity, DailyActivity, Item, Stock, Asset, InventoryMovement,
    CashAccountHead, Expense, CropProduce, Sale, CashIn, Attendance
)


# -- Inlines --
# Allow editing related models on the same page

class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'user'


class FarmPlanStepInline(admin.TabularInline):
    model = FarmPlanStep
    extra = 1  # Show one extra blank form


# -- Custom User Admin --

class CustomUserAdmin(BaseUserAdmin):
    inlines = (StaffInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')

    def get_role(self, instance):
        if hasattr(instance, 'staff'):
            return instance.staff.role
        return None

    get_role.short_description = 'Role'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# -- ModelAdmins --

@admin.register(Farmland)
class FarmlandAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_zone', 'size', 'location')
    list_filter = ('parent_zone',)
    search_fields = ('name', 'location')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.staff.role.name in ['ADMIN', 'OPERATION_DIRECTOR', 'AUDITOR']:
            return qs
        if request.user.staff.role.name == 'ZONE_MANAGER':
            return qs.filter(parent_zone=request.user.staff.assigned_zone)
        if request.user.staff.role.name == 'FARM_MANAGER':
            return qs.filter(id=request.user.staff.assigned_farm.id)
        # For supervisors, they might not see any farmlands directly
        return qs.none()


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('plot_id', 'parent_farm', 'size', 'get_remaining_space')
    list_filter = ('parent_farm__parent_zone', 'parent_farm')
    search_fields = ('plot_id', 'parent_farm__name')
    
    def get_remaining_space(self, obj):
        from django.db.models import Sum
        total_used = obj.parent_farm.plots.aggregate(Sum('size'))['size__sum'] or 0
        remaining = obj.parent_farm.size - total_used
        return f"{remaining} acres"
    get_remaining_space.short_description = 'Remaining Space'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.staff.role.name in ['ADMIN', 'OPERATION_DIRECTOR', 'AUDITOR']:
            return qs
        if request.user.staff.role.name == 'ZONE_MANAGER':
            return qs.filter(parent_zone=request.user.staff.assigned_zone)
        if request.user.staff.role.name == 'FARM_MANAGER':
            return qs.filter(id=request.user.staff.assigned_farm.id)
        # For supervisors, they might not see any farmlands directly
        return qs.none()


@admin.register(FarmPlan)
class FarmPlanAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'crop', 'plot', 'date_of_start', 'expected_harvest_date', 'is_active')
    list_filter = ('is_active', 'crop', 'plot__parent_farm')
    inlines = [FarmPlanStepInline]


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'plot', 'activity', 'quantity_done', 'unit_of_measure', 'total_cost')
    list_filter = ('date', 'activity', 'plot__parent_farm')
    search_fields = ['plot', 'activity', 'parent_plan_step', 'labor_used']

    def total_cost(self, obj):
        return obj.total_cost
    total_cost.admin_order_field = 'total_cost'  # Optional: for sorting

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'farm', 'category', 'amount', 'description')
    list_filter = ('date', 'farm', 'category')
    search_fields = ('description',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_date', 'crop_produce', 'quantity', 'price_per_ton', 'total_amount', 'buyer')
    list_filter = ('sale_date', 'buyer')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('farm', 'item', 'quantity')
    list_filter = ('farm',)
    search_fields = ('item__name',)


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Zone)
admin.site.register(Role)
admin.site.register(Crop)
admin.site.register(Category)
admin.site.register(Activity)
admin.site.register(Item)
admin.site.register(Asset)
admin.site.register(InventoryMovement)
admin.site.register(FarmPlanStep)
admin.site.register(Staff)
admin.site.register(CashAccountHead)
admin.site.register(CropProduce)
admin.site.register(CashIn)
admin.site.register(Attendance)