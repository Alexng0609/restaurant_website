from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomerProfile


class CustomSignupForm(UserCreationForm):
    """Custom signup form with additional fields for name and phone"""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Tên",
        widget=forms.TextInput(
            attrs={"placeholder": "Nhập tên của bạn", "class": "form-control"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Họ",
        widget=forms.TextInput(
            attrs={"placeholder": "Nhập họ của bạn", "class": "form-control"}
        ),
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        label="Số Điện Thoại",
        widget=forms.TextInput(
            attrs={"placeholder": "Nhập số điện thoại", "class": "form-control"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password1", "password2")
        labels = {
            "username": "Tên Đăng Nhập",
        }
        widgets = {
            "username": forms.TextInput(
                attrs={"placeholder": "Chọn tên đăng nhập", "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update password field labels and placeholders
        self.fields["password1"].label = "Mật Khẩu"
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Nhập mật khẩu", "class": "form-control"}
        )
        self.fields["password2"].label = "Xác Nhận Mật Khẩu"
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Nhập lại mật khẩu", "class": "form-control"}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            # Update or create the customer profile with phone number
            if hasattr(user, "profile"):
                user.profile.phone = self.cleaned_data["phone"]
                user.profile.save()
            else:
                CustomerProfile.objects.create(
                    user=user, phone=self.cleaned_data["phone"]
                )

        return user
