from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Shop, Pandesal

# Naval, Biliran Barangays constant
BARANGAY_CHOICES = [
    ('', '-- Select Barangay --'),
    ('agpangi', 'Agpangi'),
    ('anislagan', 'Anislagan'),
    ('atipolo', 'Atipolo'),
    ('borac', 'Borac'),
    ('cabungaan', 'Cabungaan'),
    ('calumpang', 'Calumpang'),
    ('capiñahan', 'Capiñahan'),
    ('caraycaray', 'Caraycaray'),
    ('catmon', 'Catmon'),
    ('haguikhikan', 'Haguikhikan'),
    ('imelda', 'Imelda'),
    ('larrazabal', 'Larrazabal'),
    ('libtong', 'Libtong'),
    ('libertad', 'Libertad'),
    ('lico', 'Lico'),
    ('lucsoon', 'Lucsoon'),
    ('mabini', 'Mabini'),
    ('padre_inocentes_garcia', 'Padre Inocentes Garcia (Pob.)'),
    ('padre_sergio_eamiguel', 'Padre Sergio Eamiguel'),
    ('sabang', 'Sabang'),
    ('san_pablo', 'San Pablo'),
    ('santo_nino', 'Santo Niño'),
    ('santissimo_rosario', 'Santissimo Rosario Pob. (Santo Rosa)'),
    ('talustusan', 'Talustusan'),
    ('villa_caneja', 'Villa Caneja'),
    ('villa_consuelo', 'Villa Consuelo'),
]


class ReservationForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label="Quantity")
    reserve_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Single Date & Time")
    reservation_start = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Start")
    reservation_end = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="End")
    payment_method = forms.ChoiceField(choices=[('gcash','GCash'),('bank_transfer','Bank Transfer'),('cod','Cash on Delivery'),('pickup_payment','Pickup Payment')], required=False)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('reservation_start')
        end = cleaned.get('reservation_end')
        single = cleaned.get('reserve_date')
        if not single and not (start and end):
            raise forms.ValidationError("Provide either a single date/time or a start and end window.")
        if start and end and end <= start:
            raise forms.ValidationError("Reservation end must be after start.")
        return cleaned


class BuyNowForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label="Quantity")
    payment_method = forms.ChoiceField(choices=[('cod','Cash on Delivery'),('gcash','GCash'),('bank_transfer','Bank Transfer')])
    delivery_option = forms.ChoiceField(choices=[('pickup','Pickup'),('delivery','Home Delivery')])
    pickup_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    delivery_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))

    def clean(self):
        cleaned = super().clean()
        option = cleaned.get('delivery_option')
        if option == 'pickup' and not cleaned.get('pickup_time'):
            # Optional: allow blank, but we can hint
            pass
        if option == 'delivery' and not cleaned.get('delivery_time'):
            # Optional: allow blank, but we can hint
            pass
        return cleaned

# Step 1: Personal information (no account yet)
class PersonalInfoForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False, label="First name")
    last_name = forms.CharField(max_length=30, required=False, label="Last name")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=20, required=True, label="Phone number", 
                           widget=forms.TextInput(attrs={"placeholder": "e.g., 09123456789"}))
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Birthdate")
    
    # Naval, Biliran Address Fields
    barangay = forms.ChoiceField(choices=BARANGAY_CHOICES, required=True, label="Barangay",
                                 widget=forms.Select(attrs={"class": "form-select"}))
    zone = forms.CharField(max_length=50, required=True, label="Zone / Purok",
                          widget=forms.TextInput(attrs={"placeholder": "e.g., Zone 1, Purok 3"}))
    additional_notes = forms.CharField(required=False, label="Additional Notes / Nearest Landmark",
                                      widget=forms.Textarea(attrs={"rows": 3, "placeholder": "e.g., Near church, beside barangay hall, yellow gate"}))

# Step 2: Account credentials
class CredentialsForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the label for password2 field
        self.fields['password2'].label = "Confirm Password"
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        # Custom password validation to match UI requirements
        if password:
            # Check length (8-20 characters)
            if len(password) < 8 or len(password) > 20:
                raise forms.ValidationError("Password must be between 8 and 20 characters.")
            
            # Check for at least one uppercase letter
            if not any(c.isupper() for c in password):
                raise forms.ValidationError("Password must contain at least one uppercase letter (A-Z).")
            
            # Check for at least one lowercase letter
            if not any(c.islower() for c in password):
                raise forms.ValidationError("Password must contain at least one lowercase letter (a-z).")
            
            # Check for at least one digit
            if not any(c.isdigit() for c in password):
                raise forms.ValidationError("Password must contain at least one number (0-9).")
            
            # Check for no spaces
            if ' ' in password:
                raise forms.ValidationError("Password must not contain spaces.")
        
        return password
    
    def add_error(self, field, error):
        """Override to change 'Password2:' prefix to 'Password:' in error messages"""
        if field == 'password2' and error:
            # Modify the error message to replace "password2" references
            if hasattr(error, 'message'):
                error.message = error.message.replace('password2', 'password').replace('Password2', 'Password')
            elif isinstance(error, str):
                error = error.replace('password2', 'password').replace('Password2', 'Password')
        super().add_error(field, error)

# Existing single-step form (kept if needed elsewhere)
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, label="First name")
    last_name = forms.CharField(max_length=30, required=False, label="Last name")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=20, required=True, label="Phone number",
                           widget=forms.TextInput(attrs={"placeholder": "e.g., 09123456789"}))
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Birthdate")
    
    # Naval, Biliran Address Fields
    barangay = forms.ChoiceField(choices=BARANGAY_CHOICES, required=True, label="Barangay")
    zone = forms.CharField(max_length=50, required=True, label="Zone / Purok",
                          widget=forms.TextInput(attrs={"placeholder": "e.g., Zone 1, Purok 3"}))
    additional_notes = forms.CharField(required=False, label="Additional Notes / Nearest Landmark",
                                      widget=forms.Textarea(attrs={"rows": 3, "placeholder": "e.g., Near church, beside barangay hall, yellow gate"}))

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone", "")
            profile.birth_date = self.cleaned_data.get("birth_date")
            profile.barangay = self.cleaned_data.get("barangay", "")
            profile.zone = self.cleaned_data.get("zone", "")
            profile.additional_notes = self.cleaned_data.get("additional_notes", "")
            profile.save()
        return user


# User Profile Update Form
class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="First name")
    last_name = forms.CharField(max_length=30, required=False, label="Last name")
    email = forms.EmailField(required=True, label="Email")
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone', 'barangay', 'zone', 'additional_notes', 'birth_date']
        widgets = {
            'phone': forms.TextInput(attrs={"placeholder": "e.g., 09123456789"}),
            'zone': forms.TextInput(attrs={"placeholder": "e.g., Zone 1, Purok 3"}),
            'additional_notes': forms.Textarea(attrs={"rows": 3, "placeholder": "e.g., Near church, beside barangay hall, yellow gate"}),
            'birth_date': forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            'phone': 'Phone Number',
            'barangay': 'Barangay',
            'zone': 'Zone / Purok',
            'additional_notes': 'Additional Notes / Nearest Landmark',
            'birth_date': 'Birthdate',
            'profile_picture': 'Profile Picture',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        # Make barangay and zone required
        self.fields['barangay'].required = True
        self.fields['zone'].required = True
        self.fields['phone'].required = True
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user fields
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()
            profile.save()
        return profile


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['shop_name', 'description', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell customers about your shop...'}),
            'shop_name': forms.TextInput(attrs={'placeholder': 'Your Shop Name'})
        }

class SellerProductForm(forms.ModelForm):
    categories = forms.MultipleChoiceField(
        choices=Pandesal.CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Pandesal
        fields = [
            'name', 'price', 'description', 'location', 'image', 'is_available', 
            'stock', 'preparation_time_hours', 'preparation_days',
            'categories'
        ]
        labels = {
            'location': 'Selling Location',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Zone 2, Brgy. Caraycaray, Naval, Biliran'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if type(field.widget) in (forms.TextInput, forms.NumberInput, forms.Textarea, forms.Select):
                field.widget.attrs['class'] = 'w-full border border-gray-300 rounded-lg p-2 mt-1 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none'
            elif type(field.widget) == forms.CheckboxInput:
                field.widget.attrs['class'] = 'h-4 w-4 text-green-600 rounded border-gray-300 focus:ring-green-500 mt-2'
            elif type(field.widget) == forms.CheckboxSelectMultiple:
                field.widget.attrs['class'] = 'space-y-2 mt-2'
            elif type(field.widget) == forms.FileInput:
                field.widget.attrs['class'] = 'w-full border border-gray-300 rounded-lg p-2 mt-1 focus:outline-none file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100'

    def clean_categories(self):
        return list(self.cleaned_data.get('categories', []))
