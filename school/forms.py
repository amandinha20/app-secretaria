from django import forms
from .models import Contrato

# Formulário para marcar o contrato como assinado
class ContratoAssinadoForm(forms.ModelForm):
    class Meta:
        # Define o modelo associado ao formulário
        model = Contrato
        # Campos que serão exibidos no formulário
        fields = ['contrato_assinado']