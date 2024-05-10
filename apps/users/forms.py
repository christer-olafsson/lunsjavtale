from django import forms

# local imports
from .models import Agreement, Company, Coupon, User, Vendor


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            'gender',
            'address',
            'about',
            'post_code',
            'photo_url',
            'url_field',
            'date_of_birth',
            'allergies',
        ]


class UserCreationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'phone',
            'email',
            'gender',
            'date_of_birth',
            'role',
            'photo_url',
            'url_field',
            'allergies',
        ]


class UserCreateForm(forms.ModelForm):
    # password = forms.CharField(required=False)
    id = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'phone',
            'email',
            'gender',
            'date_of_birth',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password") and not self.cleaned_data.get('id'):
            user.set_password(self.cleaned_data["password"])
            user.is_verified = True
            user.is_email_verified = True
        if commit:
            user.save()
        return user


class UserAccountForm(forms.ModelForm):
    current_password = forms.CharField(required=False)
    password = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
        ]


class UserRegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("email", "phone", 'role')


class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("email", "phone", 'role', 'password')


class AdminRegistrationForm(forms.ModelForm):
    super_user = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password")


class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ("name", "description", "email", "working_email", 'contact', 'post_code')


class CompanyUpdateForm(forms.ModelForm):

    class Meta:
        model = Company
        exclude = ("is_blocked", "is_contacted", "note")


class ValidCompanyForm(forms.ModelForm):
    first_name = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = Company
        fields = ("name", "description", "email", "working_email", 'contact', 'post_code')


class VendorForm(forms.ModelForm):
    first_name = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = Vendor
        fields = ("name", "email", 'contact', 'post_code')


class VendorUpdateForm(forms.ModelForm):
    id = forms.CharField(required=True)

    class Meta:
        model = Vendor
        fields = (
            "name", "email", 'contact', 'post_code', 'logo_url', 'url_field', 'formation_date', 'social_media_links'
        )


class AgreementForm(forms.ModelForm):
    object_id = forms.IntegerField(required=False)

    class Meta:
        model = Agreement
        fields = '__all__'


class CouponForm(forms.ModelForm):

    class Meta:
        model = Coupon
        fields = '__all__'
