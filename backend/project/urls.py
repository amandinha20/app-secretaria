from django.urls import path
from .views import lista_alunos, contrato_detalhe
urlpatterns= [
    path('alunos/', lista_alunos, name= 'lista_alunos'),
    path('contrato/<int:aluno_id>/', contrato_detalhe, name='contrato_detalhe'),
]