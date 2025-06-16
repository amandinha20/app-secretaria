"""
Arquivo de rotas do app school.
- Define as URLs para geração de contrato, boletim, gráficos, relatórios e seleção de desempenho.
- Cada rota aponta para uma view correspondente em views.py.
"""

from django.urls import path
# Importa as views que serão usadas nas rotas
from .views import (
    gerar_contrato_pdf, boletim_aluno, boletim_aluno_pdf, grafico_desempenho_aluno,
    relatorio_turma, grafico_disciplina, desempenho_index,
    desempenho_aluno_select, desempenho_turma_select, desempenho_disciplina_select
)

# Lista de padrões de URL do app
urlpatterns = [
    # Rota para gerar o contrato em PDF de um aluno
    path('gerar-contrato/<int:aluno_id>/', gerar_contrato_pdf, name='gerar_contrato_pdf'),
    # Rota para exibir o boletim de um aluno
    path('boletim/<int:aluno_id>/', boletim_aluno, name='boletim_aluno'),
    # Rota para gerar o boletim em PDF de um aluno
    path('boletim/<int:aluno_id>/pdf/', boletim_aluno_pdf, name='boletim_aluno_pdf'),
    # Rota para exibir o gráfico de desempenho de um aluno
    path('grafico/aluno/<int:aluno_id>/', grafico_desempenho_aluno, name='grafico_desempenho_aluno'),
    # Rota para exibir o relatório de uma turma
    path('relatorio/turma/<int:turma_id>/', relatorio_turma, name='relatorio_turma'),
    # Rota para exibir o gráfico de desempenho em uma disciplina
    path('grafico/disciplina/<int:materia_id>/', grafico_disciplina, name='grafico_disciplina'),
    # Rota para a página inicial de desempenho
    path('desempenho/', desempenho_index, name='desempenho_index'),
    # Rota para seleção de aluno para desempenho
    path('desempenho/aluno/', desempenho_aluno_select, name='desempenho_aluno_select'),
    # Rota para seleção de turma para desempenho
    path('desempenho/turma/', desempenho_turma_select, name='desempenho_turma_select'),
    # Rota para seleção de disciplina para desempenho
    path('desempenho/disciplina/', desempenho_disciplina_select, name='desempenho_disciplina_select'),
]