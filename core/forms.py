from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, DietaFeedback, AlimentoPersonalizado

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['idade', 'genero', 'altura', 'peso', 'nivel_atividade', 'objetivo']
        widgets = {
            'idade': forms.NumberInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nivel_atividade': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.Select(attrs={'class': 'form-control'}),
        }

class DietaFeedbackForm(forms.ModelForm):
    class Meta:
        model = DietaFeedback
        fields = ['satisfacao', 'aderencia', 'comentarios']
        widgets = {
            'satisfacao': forms.Select(attrs={'class': 'form-control'}),
            'aderencia': forms.Select(attrs={'class': 'form-control'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AlimentoPersonalizadoForm(forms.ModelForm):
    class Meta:
        model = AlimentoPersonalizado
        fields = ['nome', 'tipo', 'motivo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 