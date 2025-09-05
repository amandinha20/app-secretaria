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
]
# Importando as novas views para calendário acadêmico
from .views import (
    calendario_academico, adicionar_evento_calendario, 
    editar_evento_calendario, excluir_evento_calendario
)

# Adicionando as novas rotas para calendário acadêmico
urlpatterns += [
    # Rotas para Calendário Acadêmico
    path('calendario/', calendario_academico, name='calendario_academico'),
    path('calendario/adicionar/', adicionar_evento_calendario, name='adicionar_evento_calendario'),
    path('calendario/<int:evento_id>/editar/', editar_evento_calendario, name='editar_evento_calendario'),
    path('calendario/<int:evento_id>/excluir/', excluir_evento_calendario, name='excluir_evento_calendario'),
]


# Importando as novas views para agenda de professores
from .views import (
    agenda_professor, adicionar_atividade_agenda, 
    editar_atividade_agenda, excluir_atividade_agenda, lista_professores_agenda
)

# Adicionando as novas rotas para agenda de professores
urlpatterns += [
    # Rotas para Agenda de Professores
    path('professores/', lista_professores_agenda, name='lista_professores_agenda'),
    path('agenda/professor/<int:professor_id>/', agenda_professor, name='agenda_professor'),
    path('agenda/professor/<int:professor_id>/adicionar/', adicionar_atividade_agenda, name='adicionar_atividade_agenda'),
    path('agenda/atividade/<int:atividade_id>/editar/', editar_atividade_agenda, name='editar_atividade_agenda'),
    path('agenda/atividade/<int:atividade_id>/excluir/', excluir_atividade_agenda, name='excluir_atividade_agenda'),
]


# Importando as novas views para notificações
from .views import (
    listar_notificacoes, marcar_notificacao_enviada, excluir_notificacao
)

# Adicionando as novas rotas para notificações
urlpatterns += [
    # Rotas para Notificações
    path('notificacoes/', listar_notificacoes, name='listar_notificacoes'),
    path('notificacoes/<int:notificacao_id>/enviada/', marcar_notificacao_enviada, name='marcar_notificacao_enviada'),
    path('notificacoes/<int:notificacao_id>/excluir/', excluir_notificacao, name='excluir_notificacao'),
]

