from django import forms


class LoginForm(forms.Form):
    host = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Host'}))
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
