# farm/forms.py
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import FarmPlan, FarmPlanStep, Plot, DailyActivity, CropProduce, Sale, CashIn, Expense, InventoryMovement, ActivityItemUsage, Item, Crop


class FarmPlanForm(forms.ModelForm):
    class Meta:
        model = FarmPlan
        fields = ['crop', 'plot', 'date_of_start']
        widgets = {
            'date_of_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'crop': forms.Select(attrs={'class': 'form-select'}),
            'plot': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter plots based on user role
        if user and not user.is_superuser:
            staff_profile = getattr(user, 'staff', None)
            if staff_profile:
                if staff_profile.role.name == 'ZONE_MANAGER':
                    self.fields['plot'].queryset = Plot.objects.filter(
                        parent_farm__parent_zone=staff_profile.assigned_zone
                    )
                elif staff_profile.role.name == 'FARM_MANAGER':
                     self.fields['plot'].queryset = Plot.objects.filter(
                        parent_farm=staff_profile.assigned_farm
                    )
                # Operation directors and admins will see all plots by default


class FarmPlanStepForm(forms.ModelForm):
    class Meta:
        model = FarmPlanStep
        fields = ['activity', 'start_day_offset', 'duration_days', 'budgeted_cost_per_acre']
        widgets = {
            'activity': forms.Select(attrs={'class': 'form-select'}),
            'start_day_offset': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'budgeted_cost_per_acre': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'budgeted_cost_per_acre': 'Budget per Acre (₹)',
        }

# This factory creates a set of forms for the FarmPlanStep model,
# linked to a parent FarmPlan instance.
FarmPlanStepFormSet = inlineformset_factory(
    FarmPlan,          # Parent model
    FarmPlanStep,      # Child model
    form=FarmPlanStepForm,
    extra=1,           # Number of empty forms to display
    can_delete=True,   # Allow users to delete steps
    can_delete_extra=True,
)

class SingleFarmPlanStepForm(forms.ModelForm):
    """A form for adding a single FarmPlanStep via a modal."""
    class Meta:
        model = FarmPlanStep
        fields = ['activity', 'start_day_offset', 'duration_days', 'budgeted_cost_per_acre']
        widgets = {
            'activity': forms.Select(attrs={'class': 'form-select'}),
            'start_day_offset': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Days from plan start'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control', 'value': 1}),
            'budgeted_cost_per_acre': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ₹500.00 per acre', 'step': '0.01'}),
        }
        labels = {
            'budgeted_cost_per_acre': 'Budget per Acre (₹)',
        }


class DailyActivityForm(forms.ModelForm):
    # Additional fields for input usage
    input_used = forms.BooleanField(required=False, label='Input Used?')
    input_item = forms.ModelChoiceField(queryset=None, required=False, label='Input Item')
    input_quantity = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Input Quantity')
    
    class Meta:
        model = DailyActivity
        fields = ['plot', 'activity', 'parent_plan_step', 'quantity_done', 'unit_of_measure', 'machine_used', 'machine_cost_per_unit', 'labor_count', 'labor_cost_per_person', 'labor_names', 'vendor_name', 'time_taken', 'notes']
        widgets = {
            'plot': forms.Select(attrs={'class': 'form-select plot-selector'}),
            'activity': forms.Select(attrs={'class': 'form-select'}),
            'parent_plan_step': forms.Select(attrs={'class': 'form-select', 'required': False}),
            'quantity_done': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity worked'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., acres, hours'}),
            'machine_used': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'machine_cost_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost per unit (₹)'}),
            'labor_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of laborers'}),
            'labor_cost_per_person': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost per person (₹)'}),
            'labor_names': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John, Mary, David'}),
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor/Contractor name'}),
            'time_taken': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'quantity_done': 'Quantity Done',
            'unit_of_measure': 'Unit of Measure',
            'machine_used': 'Machine Used?',
            'machine_cost_per_unit': 'Machine Cost per Unit (₹)',
            'labor_count': 'Number of Laborers',
            'labor_cost_per_person': 'Labor Cost per Person (₹)',
            'labor_names': 'Labor Names',
            'vendor_name': 'Vendor/Contractor',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Item
        
        # Set field requirements
        self.fields['parent_plan_step'].required = False
        self.fields['labor_names'].required = False
        self.fields['vendor_name'].required = False
        self.fields['machine_cost_per_unit'].required = False
        self.fields['labor_count'].required = False
        self.fields['labor_cost_per_person'].required = False
        
        # Set up input item choices
        self.fields['input_item'].queryset = Item.objects.all()
        self.fields['input_item'].widget = forms.Select(attrs={'class': 'form-select'})
        self.fields['input_quantity'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity used', 'step': '0.01'})
        
        # Start with empty queryset - will be populated via AJAX
        self.fields['parent_plan_step'].queryset = FarmPlanStep.objects.none()
        
        # If editing existing instance, populate plan steps for that plot
        if self.instance.pk and self.instance.plot:
            self.fields['parent_plan_step'].queryset = FarmPlanStep.objects.filter(
                parent_plan__plot=self.instance.plot,
                parent_plan__is_active=True
            ).select_related('parent_plan', 'activity').order_by('-parent_plan__date_of_start')
    
    def clean_parent_plan_step(self):
        parent_plan_step = self.cleaned_data.get('parent_plan_step')
        if parent_plan_step == '' or parent_plan_step is None:
            return None
        return parent_plan_step

# Custom formset class to handle extra fields
class DailyActivityFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all forms have the custom fields properly initialized
        for form in self.forms:
            if hasattr(form, 'fields'):
                if 'input_item' in form.fields:
                    from .models import Item
                    form.fields['input_item'].queryset = Item.objects.all()

# Create a factory for our form
DailyActivityFormSet = modelformset_factory(
    DailyActivity,
    form=DailyActivityForm,
    formset=DailyActivityFormSet,
    extra=1,
    can_delete=True
)

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'description', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CashInForm(forms.ModelForm):
    class Meta:
        model = CashIn
        fields = ['date', 'head', 'given_by', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'head': forms.Select(attrs={'class': 'form-select'}),
            'given_by': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['crop_produce', 'sale_date', 'quantity', 'price_per_ton', 'buyer', 'notes']
        widgets = {
            'crop_produce': forms.Select(attrs={'class': 'form-select'}),
            'sale_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_ton': forms.NumberInput(attrs={'class': 'form-control'}),
            'buyer': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        farm = kwargs.pop('farm', None)
        super().__init__(*args, **kwargs)
        if farm:
            self.fields['crop_produce'].queryset = CropProduce.objects.filter(farm=farm)


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['category', 'name', 'unit', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name', 'seed_variety', 'harvesting_days', 'expected_yield', 'features']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'seed_variety': forms.TextInput(attrs={'class': 'form-control'}),
            'harvesting_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'expected_yield': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'expected_yield': 'Expected Yield (tons per acre)',
        }


class ActivityItemUsageForm(forms.ModelForm):
    class Meta:
        model = ActivityItemUsage
        fields = ['item', 'quantity_used', 'cost_per_unit']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity_used': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'quantity_used': 'Quantity Used',
            'cost_per_unit': 'Cost per Unit (₹)',
        }


class InventoryMovementForm(forms.ModelForm):
    class Meta:
        model = InventoryMovement
        fields = ['item', 'transaction_type', 'quantity', 'price_per_unit', 'date']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'price_per_unit': 'Price per Unit (₹)',
        }