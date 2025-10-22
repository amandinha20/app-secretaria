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
from .views_advertencia import gerar_advertencia_pdf
from . import views_relatorio
from . import views

# Lista de padrões de URL do app
urlpatterns = [
    # Rotas para gerar e exibir o contrato e o boletim em PDF de um aluno
    path('gerar-contrato/<int:aluno_id>/', gerar_contrato_pdf, name='gerar_contrato_pdf'),
    path('boletim/<int:aluno_id>/', boletim_aluno, name='boletim_aluno'),
    path('boletim/<int:aluno_id>/pdf/', boletim_aluno_pdf, name='boletim_aluno_pdf'),
    # Rota para exibir o gráfico de desempenho de um aluno, disciplica e turma
    path('grafico/aluno/<int:aluno_id>/', grafico_desempenho_aluno, name='grafico_desempenho_aluno'),
    path('relatorio/turma/<int:turma_id>/', relatorio_turma, name='relatorio_turma'),
    path('grafico/disciplina/<int:materia_id>/', grafico_disciplina, name='grafico_disciplina'),
    # Rota para a página inicial de desempenho
    path('desempenho/', desempenho_index, name='desempenho_index'),
    # Rota para seleção de aluno, turma ou disciplina para desempenho
    path('desempenho/aluno/', desempenho_aluno_select, name='desempenho_aluno_select'),
    path('desempenho/turma/', desempenho_turma_select, name='desempenho_turma_select'),
    path('desempenho/disciplina/', desempenho_disciplina_select, name='desempenho_disciplina_select'),
    path('advertencia/<int:advertencia_id>/pdf/', gerar_advertencia_pdf, name='gerar_advertencia_pdf'),
    path('relatorio/excel/', views_relatorio.gerar_relatorio_presenca_excel, name='relatorio_excel'),
    path('relatorio/pdf/', views_relatorio.gerar_relatorio_presenca_pdf, name='relatorio_pdf'),
    # Seleção de turma e relatórios por turma
    path('relatorio/select/', views_relatorio.relatorio_select, name='relatorio_select'),
    path('relatorio/excel/<int:turma_id>/', views_relatorio.gerar_relatorio_presenca_excel_turma, name='relatorio_excel_turma'),
    path('relatorio/pdf/<int:turma_id>/', views_relatorio.gerar_relatorio_presenca_pdf_turma, name='relatorio_pdf_turma'),
    # Rotas para suspensões
    path('suspensao/select/turma/', views.suspensao_select_turma, name='suspensao_select_turma'),
    path('suspensao/select/aluno/<int:turma_id>/', views.suspensao_select_aluno, name='suspensao_select_aluno'),
    path('suspensao/create/<int:turma_id>/<int:aluno_id>/', views.suspensao_create, name='suspensao_create'),
    path('suspensao/create/<int:turma_id>/', views.suspensao_create, name='suspensao_create_no_aluno'),
]