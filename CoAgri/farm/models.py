# farm/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from datetime import timedelta


# -- Core Location and Structure Models --

class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    district = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.district})"


class Farmland(models.Model):
    name = models.CharField(max_length=150)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="in acres")
    location = models.CharField(max_length=255)
    infrastructure = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    parent_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='farmlands')

    def __str__(self):
        return f"{self.name} in {self.parent_zone.name}"


class Plot(models.Model):
    parent_farm = models.ForeignKey(Farmland, on_delete=models.CASCADE, related_name='plots')
    plot_id = models.CharField(max_length=50)  # e.g., "P001", "P002"
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="in acres")
    infrastructure = models.TextField(blank=True, null=True)

    def clean(self):
        super().clean()
        if self.parent_farm and self.size:
            # Get sum of all other plots in the same farmland (excluding current plot if updating)
            existing_plots = Plot.objects.filter(parent_farm=self.parent_farm)
            if self.pk:  # If updating existing plot, exclude it from calculation
                existing_plots = existing_plots.exclude(pk=self.pk)
            
            total_existing_size = existing_plots.aggregate(Sum('size'))['size__sum'] or 0
            total_size_with_new = total_existing_size + self.size
            
            if total_size_with_new > self.parent_farm.size:
                raise ValidationError({
                    'size': f'Total plot size ({total_size_with_new} acres) cannot exceed farmland size ({self.parent_farm.size} acres). Available space: {self.parent_farm.size - total_existing_size} acres.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # This will call clean() method
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Plot {self.plot_id} in {self.parent_farm.name}"

    class Meta:
        unique_together = ('parent_farm', 'plot_id')  # Ensure unique plot IDs within a farm


# -- Staff and Roles Models --

class Role(models.Model):
    # These roles are defined based on your requirements.
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('OPERATION_DIRECTOR', 'Operation Director'),
        ('ZONE_MANAGER', 'Zone Manager'),
        ('FARM_MANAGER', 'Farm Manager'),
        ('SUPERVISOR', 'Supervisor'),
        ('AUDITOR', 'Auditor'),
    ]
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    education = models.CharField(max_length=100, blank=True)

    # For role-based access control
    assigned_zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True,
                                      help_text="For Zone Managers")
    assigned_farm = models.ForeignKey(Farmland, on_delete=models.SET_NULL, null=True, blank=True,
                                      help_text="For Farm Managers")
    assigned_plot = models.ForeignKey(Plot, on_delete=models.SET_NULL, null=True, blank=True,
                                      help_text="For Supervisors")

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# -- Crop and Planning Models --

class Crop(models.Model):
    name = models.CharField(max_length=100)
    seed_variety = models.CharField(max_length=100)
    harvesting_days = models.PositiveIntegerField(help_text="Average days from sowing to harvest")
    expected_yield = models.DecimalField(max_digits=10, decimal_places=2, help_text="in tons per acre")
    features = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.seed_variety})"


class FarmPlan(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='farm_plans')
    date_of_start = models.DateField()
    expected_harvest_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    actual_harvest_date = models.DateField(blank=True, null=True)
    actual_yield = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="in tons")

    def save(self, *args, **kwargs):
        # Auto-calculate expected harvest date if not set
        if self.date_of_start and self.crop and not self.expected_harvest_date:
            self.expected_harvest_date = self.date_of_start + timedelta(days=self.crop.harvesting_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Plan for {self.crop.name} on {self.plot} starting {self.date_of_start}"


# -- Activity and Category Models --

class Category(models.Model):
    TYPE_CHOICES = [
        ('ACTIVITY', 'Activity'),
        ('ITEM', 'Item'),
        ('EXPENSE', 'Expense'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    expected_efficiency = models.CharField(max_length=100, blank=True, help_text="e.g., '1 acre/hour'")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        verbose_name_plural = "Categories"


class Activity(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, limit_choices_to={'type': 'ACTIVITY'})
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Activities"


# -- Farm Plan Execution & Tracking --

class FarmPlanStep(models.Model):
    parent_plan = models.ForeignKey(FarmPlan, on_delete=models.CASCADE, related_name='steps')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    start_day_offset = models.PositiveIntegerField(help_text="Days from plan start date")
    duration_days = models.PositiveIntegerField(default=1)

    # Budgeting per step (per acre)
    budgeted_cost_per_acre = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Cost per acre in ₹")
    
    def get_total_budgeted_cost(self, acres=None):
        """Calculate total budgeted cost for given acres. If no acres provided, use plot size."""
        if acres is None:
            acres = self.parent_plan.plot.size
        return self.budgeted_cost_per_acre * acres

    def get_start_date(self):
        return self.parent_plan.date_of_start + timedelta(days=self.start_day_offset)

    def get_end_date(self):
        return self.get_start_date() + timedelta(days=self.duration_days - 1)

    def __str__(self):
        return f"{self.activity.name} for {self.parent_plan}"


class DailyActivity(models.Model):
    date = models.DateField()
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='daily_activities')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    parent_plan_step = models.ForeignKey(FarmPlanStep, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='daily_entries')
    quantity_done = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The numerical amount of work done."
    )
    unit_of_measure = models.CharField(
        max_length=50,
        help_text="e.g., 'acres', 'liters', 'hours', 'units'"
    )
    
    # Machine costs
    machine_used = models.BooleanField(default=False, help_text="Is machine used?")
    machine_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Labor costs
    labor_count = models.PositiveIntegerField(default=0, help_text="Number of laborers")
    labor_cost_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    labor_names = models.TextField(blank=True, help_text="Names of laborers used, separated by commas")
    
    vendor_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of vendor/contractor to whom payment will be made"
    )
    time_taken = models.DurationField(help_text="e.g., '4 hours 30 minutes'")
    notes = models.TextField(blank=True)

    @property
    def machine_cost(self):
        if self.machine_used:
            return self.quantity_done * self.machine_cost_per_unit
        return 0
    
    @property
    def labor_cost(self):
        return self.labor_count * self.labor_cost_per_person
    
    @property
    def item_cost(self):
        return sum(usage.total_cost for usage in self.item_usages.all())
    
    @property
    def total_cost(self):
        """Calculates the total cost for this activity instance."""
        return self.machine_cost + self.labor_cost + self.item_cost

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create expense after item usages are created (called from view)
        if not is_new and self.total_cost > 0:
            from .models import Expense, Category
            
            # Delete existing expense for this activity to avoid duplicates
            Expense.objects.filter(
                farm=self.plot.parent_farm,
                date=self.date,
                description__contains=f"Plot {self.plot.plot_id}"
            ).delete()
            
            # Get or create category with activity name
            activity_category, created = Category.objects.get_or_create(
                name=self.activity.name,
                type="EXPENSE"
            )
            
            # Create expense record with total cost including items
            Expense.objects.create(
                farm=self.plot.parent_farm,
                date=self.date,
                category=activity_category,
                description=f"Plot {self.plot.plot_id}" + 
                           (f" - Vendor: {self.vendor_name}" if self.vendor_name else ""),
                amount=self.total_cost
            )

    def __str__(self):
        return f"{self.quantity_done} {self.unit_of_measure} of {self.activity.name} on {self.plot}"

    class Meta:
        verbose_name_plural = "Daily Activities"


# -- Inventory and Financial Models --

class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, limit_choices_to={'type': 'ITEM'})
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, help_text="e.g., 'kg', 'liter', 'unit'")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class ActivityItemUsage(models.Model):
    """Track items used in daily activities"""
    daily_activity = models.ForeignKey(DailyActivity, on_delete=models.CASCADE, related_name='item_usages')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def total_cost(self):
        return self.quantity_used * self.cost_per_unit

    def __str__(self):
        return f"{self.quantity_used} {self.item.unit} of {self.item.name} for {self.daily_activity}"

class Stock(models.Model):
    farm = models.ForeignKey(Farmland, on_delete=models.CASCADE, related_name='stock')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('farm', 'item')

    def __str__(self):
        return f"{self.quantity} {self.item.unit} of {self.item.name} at {self.farm.name}"


class Asset(models.Model):
    farm = models.ForeignKey(Farmland, on_delete=models.CASCADE, related_name='assets')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, help_text="e.g., Tractor, Sprayer")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} at {self.farm.name}"


class InventoryMovement(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),  # Purchase or transfer in
        ('OUT', 'Stock Out'),  # Usage in activity
        ('ADJUST', 'Adjustment'),  # Physical count correction
    ]
    farm = models.ForeignKey(Farmland, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price per unit for stock in")
    date = models.DateField()
    related_activity = models.ForeignKey(DailyActivity, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def total_value(self):
        return self.quantity * self.price_per_unit

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} of {self.item.name} on {self.date}"


class CashAccountHead(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Expense(models.Model):
    farm = models.ForeignKey(Farmland, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, limit_choices_to={'type': 'EXPENSE'})
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Expense of {self.amount} for {self.category.name} at {self.farm.name}"


class CropProduce(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    farm = models.ForeignKey(Farmland, on_delete=models.CASCADE)
    harvest_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="in tons")
    storage_location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.quantity} tons of {self.crop.name} from {self.plot}"


class Sale(models.Model):
    crop_produce = models.ForeignKey(CropProduce, on_delete=models.CASCADE, related_name='sales')
    sale_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="in tons")
    price_per_ton = models.DecimalField(max_digits=10, decimal_places=2)
    buyer = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    @property
    def total_amount(self):
        return self.quantity * self.price_per_ton

    def __str__(self):
        return f"Sale of {self.quantity} tons of {self.crop_produce.crop.name} to {self.buyer}"


class CashIn(models.Model):
    farm = models.ForeignKey(Farmland, on_delete=models.CASCADE, related_name='cash_inflows')
    given_by = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    head = models.ForeignKey(CashAccountHead, on_delete=models.PROTECT, limit_choices_to={'type': 'INCOME'})

    def __str__(self):
        return f"Cash In: {self.amount} from {self.given_by} for {self.head.name}"


class Attendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    farm = models.ForeignKey(Farmland, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=True)

    class Meta:
        unique_together = ('staff', 'date')

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.staff.user.username} - {status} on {self.date}"