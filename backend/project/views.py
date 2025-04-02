from django.shortcuts import render
from .models import Aluno, Contrato

def lista_alunos(request):
    alunos= Aluno.objects.all()
    return render(request, 'core/alunos.html', {'alunos', alunos})

def contrato_detalhe(request, aluno_id):
    contrato= Contrato.objects.get(aluno_id=aluno_id)
    return render(request, 'core/contrato.html', {'contrato': contrato})
# Create your views here.
