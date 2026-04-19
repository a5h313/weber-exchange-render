from django import forms
from .models import Feedback, Product, ProductImage, UserProfile, Tag
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        labels = {
            'username': 'Name',
            'email': 'Email',
            'subject': 'Subject',
            'message': 'Message',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Enter a subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Write your message here'}),
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=50, required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'display_name',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        allowed_domains = ('@weber.edu', '@mail.weber.edu')
        if not email.endswith(allowed_domains):
            raise forms.ValidationError("Only Weber email addresses are allowed.")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use.")

        return email

    def clean_display_name(self):
        display_name = self.cleaned_data['display_name'].strip()

        if UserProfile.objects.filter(display_name__iexact=display_name).exists():
            raise forms.ValidationError("This display name is already taken.")

        return display_name

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].lower()

        user.username = email
        user.email = email
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()

        if commit:
            user.save()

        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProductForm(forms.ModelForm):
    existing_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Select Existing Tags",
    )
    new_tags = forms.CharField(
        required=False,
        label="Add New Tags",
        help_text="Enter tags separated by commas",
    )

    class Meta:
        model = Product
        fields = [
            "title",
            "price",
            "category",
            "condition",
            "location",
            "description",
        ]
        labels = {
            "title": "Product Name",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["existing_tags"].queryset = Tag.objects.order_by("name")


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        labels = {
            "image": "Image",
        }


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=1,
    can_delete=False,
)