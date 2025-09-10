
from django import forms
import re
from .models import User

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=50,widget=forms.PasswordInput,label='Confirm Password')
    password = forms.CharField(max_length=50,widget=forms.PasswordInput,label='Password')

    class Meta:
        model = User
        fields = ('email','username','password')
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.keys():
            self.fields[field].widget.attrs.update({
                'class':'form-control',
                'placeholder':self.fields[field].label,
            })
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        invalid_characters = re.findall('[^\w ]',username)
        if len(invalid_characters) > 0:
            raise forms.ValidationError(f"Username Invalid characters: {invalid_characters}")
        match_ = re.match('[\w ]{3,15}',username)
        if match_ == None or match_.group(0) != username:
             raise forms.ValidationError("Invalid username.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        #if password != confirm_password:
        #    raise forms.ValidationError("Passwords don't match.")

        return password


class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput,max_length=50)
    username = forms.CharField(max_length=50)
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field_name in self.fields.keys():
            self.fields[field_name].widget.attrs.update({
                'class':'form-control',
                'placeholder':self.fields[field_name].label
            })
    