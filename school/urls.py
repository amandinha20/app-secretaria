"""
URLs unificadas - merge de dev e Gestão-de-faltas---Giovana
Inclui rotas de contratos, boletins, faltas, suspensões, advertências, calendário, agenda e notificações.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import (
    gerar_contrato_pdf,
    boletim_aluno,
    boletim_aluno_pdf,
    grafico_desempenho_aluno,
    relatorio_turma,
    grafico_disciplina,
    desempenho_index,
    desempenho_aluno_select,
    desempenho_turma_select,
    desempenho_disciplina_select,
    calendario_academico,
    adicionar_evento_calendario,
    editar_evento_calendario,
    excluir_evento_calendario,
    agenda_professor,
    adicionar_atividade_agenda,
    editar_atividade_agenda,
    excluir_atividade_agenda,
    lista_professores_agenda,
    listar_notificacoes,
    marcar_notificacao_enviada,
    excluir_notificacao,
    faltas_aluno_pdf,
    relatorio_faltas_pdf,
)

# Advertência (de acordo com o padrão mais recente)
from .views_advertencia import gerar_advertencia_pdf

app_name = 'school'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Contratos e boletins
    path('gerar-contrato/<int:aluno_id>/', gerar_contrato_pdf, name='gerar_contrato_pdf'),
    path('boletim/<int:aluno_id>/', boletim_aluno, name='boletim_aluno'),
    path('boletim/<int:aluno_id>/pdf/', boletim_aluno_pdf, name='boletim_aluno_pdf'),

    # Faltas
    path('faltas/pdf/', faltas_aluno_pdf, name='faltas_aluno_pdf'),
    path('relatorio-faltas/<int:turma_id>/', relatorio_faltas_pdf, name='relatorio_faltas_pdf'),

    # Gráficos e desempenho
    path('grafico/aluno/<int:aluno_id>/', grafico_desempenho_aluno, name='grafico_desempenho_aluno'),
    path('relatorio/turma/<int:turma_id>/', relatorio_turma, name='relatorio_turma'),
    path('grafico/disciplina/<int:materia_id>/', grafico_disciplina, name='grafico_disciplina'),
    path('desempenho/', desempenho_index, name='desempenho_index'),
    path('desempenho/aluno/', desempenho_aluno_select, name='desempenho_aluno_select'),
    path('desempenho/turma/', desempenho_turma_select, name='desempenho_turma_select'),
    path('desempenho/disciplina/', desempenho_disciplina_select, name='desempenho_disciplina_select'),

    # Advertências
    path('advertencia/<int:advertencia_id>/pdf/', gerar_advertencia_pdf, name='gerar_advertencia_pdf'),

    # Suspensões
    path('suspensao/select/turma/', views.suspensao_select_turma, name='suspensao_select_turma'),
    path('suspensao/select/aluno/<int:turma_id>/', views.suspensao_select_aluno, name='suspensao_select_aluno'),
    path('suspensao/create/<int:turma_id>/<int:aluno_id>/', views.suspensao_create, name='suspensao_create'),
    path('suspensao/create/<int:turma_id>/', views.suspensao_create, name='suspensao_create_no_aluno'),

    # Calendário acadêmico
    path('calendario/', calendario_academico, name='calendario_academico'),
    path('calendario/adicionar/', adicionar_evento_calendario, name='adicionar_evento_calendario'),
    path('calendario/<int:evento_id>/editar/', editar_evento_calendario, name='editar_evento_calendario'),
    path('calendario/<int:evento_id>/excluir/', excluir_evento_calendario, name='excluir_evento_calendario'),

    # Agenda de professores
    path('professores/', lista_professores_agenda, name='lista_professores_agenda'),
    path('agenda/professor/<int:professor_id>/', agenda_professor, name='agenda_professor'),
    path('agenda/professor/<int:professor_id>/adicionar/', adicionar_atividade_agenda, name='adicionar_atividade_agenda'),
    path('agenda/atividade/<int:atividade_id>/editar/', editar_atividade_agenda, name='editar_atividade_agenda'),
    path('agenda/atividade/<int:atividade_id>/excluir/', excluir_atividade_agenda, name='excluir_atividade_agenda'),

    # Notificações
    path('notificacoes/', listar_notificacoes, name='listar_notificacoes'),
    path('notificacoes/<int:notificacao_id>/enviada/', marcar_notificacao_enviada, name='marcar_notificacao_enviada'),
    path('notificacoes/<int:notificacao_id>/excluir/', excluir_notificacao, name='excluir_notificacao'),
]

# Arquivos estáticos e de mídia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
