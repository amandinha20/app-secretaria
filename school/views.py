from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import Avg
from .models import Aluno, Nota, Materia, Turmas  
from .utils.graphs import gerar_grafico_barras

def gerar_contrato_pdf(request, aluno_id):
    # Busca o aluno pelo ID ou retorna 404 se não existir
    aluno = get_object_or_404(Aluno, id=aluno_id)
    # Obtém o responsável do aluno
    responsavel = aluno.responsavel

    # Monta o contexto com dados do aluno e do responsável
    context = {
        'aluno': {
            'nome': aluno.complet_name_aluno,
            'data_nascimento': aluno.birthday_aluno.strftime('%d/%m/%Y'),
            'cpf': aluno.cpf_aluno,
            'telefone': aluno.phone_number_aluno,
            'email': aluno.email_aluno,
        },
        'responsavel': {
            'nome': responsavel.complet_name,
            'data_nascimento': responsavel.birthday.strftime('%d/%m/%Y'),
            'cpf': responsavel.cpf,
            'telefone': responsavel.phone_number,
            'email': responsavel.email,
        }
    }

    # Renderiza o template HTML do contrato com o contexto preenchido
    html_string = render_to_string('contrato.html', context)
    # Gera o PDF a partir do HTML renderizado
    pdf = HTML(string=html_string).write_pdf()

    # Cria a resposta HTTP com o PDF gerado
    response = HttpResponse(pdf, content_type='application/pdf')
    # Define o nome do arquivo PDF no cabeçalho da resposta
    response['Content-Disposition'] = f'inline; filename="contrato_{aluno.complet_name_aluno}.pdf"'
    return response

def boletim_aluno(request, aluno_id):
    # Busca o aluno pelo ID
    aluno = get_object_or_404(Aluno, id=aluno_id)
    # Busca as notas do aluno, otimizando com select_related para evitar múltiplas queries
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    # Verifica se existe alguma nota abaixo de 70 para alerta
    tem_alerta = any(nota.nota < 70 for nota in notas)
    # Renderiza o boletim do aluno com as notas e alerta
    return render(request, 'boletim.html', {'aluno': aluno, 'notas': notas, 'tem_alerta': tem_alerta})

def boletim_aluno_pdf(request, aluno_id):
    # Busca o aluno pelo ID
    aluno = get_object_or_404(Aluno, id=aluno_id)
    # Busca as notas do aluno
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    # Monta o contexto para o template
    context = {'aluno': aluno, 'notas': notas}
    # Renderiza o HTML do boletim
    html_string = render_to_string('boletim.html', context)
    # Gera o PDF do boletim (sem recursos externos)
    pdf = HTML(string=html_string, base_url=None).write_pdf(stylesheets=None)
    # Cria a resposta HTTP com o PDF gerado
    response = HttpResponse(pdf, content_type='application/pdf')
    # Define o nome do arquivo PDF no cabeçalho da resposta
    response['Content-Disposition'] = f'inline; filename="boletim_{aluno.complet_name_aluno}.pdf"'
    return response

def grafico_desempenho_aluno(request, aluno_id):
    # Busca o aluno pelo ID
    aluno = Aluno.objects.get(id=aluno_id)
    # Busca as notas do aluno
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    # Monta listas para labels (nomes das matérias), valores (notas) e alerta (notas < 70)
    labels = [n.materia.name_subject for n in notas]
    values = [float(n.nota) for n in notas]
    atencao = [n.nota < 70 for n in notas]
    tem_alerta = any(atencao)
    # Define cores para as barras do gráfico (vermelho para notas baixas)
    cores = ['red' if a else 'skyblue' for a in atencao]
    # Gera o gráfico em base64
    image_base64 = gerar_grafico_barras(labels, values, cores, f'Desempenho de {aluno.complet_name_aluno}', 'Nota')
    # Renderiza o template com o gráfico, notas e alerta
    return render(request, 'grafico_aluno.html', {
        'aluno': aluno,
        'grafico': image_base64,
        'notas': notas,
        'tem_alerta': tem_alerta,
    })

def relatorio_turma(request, turma_id):
    # Busca a turma pelo ID
    turma = Turmas.objects.get(id=turma_id)
    # Busca todos os alunos da turma
    alunos = Aluno.objects.filter(class_choices=turma)
    relatorio = []
    nomes = []
    medias = []
    cores = []
    # Para cada aluno, calcula a média e verifica se há alerta
    for aluno in alunos:
        # Busca as notas do aluno
        notas = Nota.objects.filter(aluno=aluno)
        # Calcula a média das notas
        media = aluno.media_notas()
        # Verifica se há alguma nota abaixo de 70
        atencao = any(n.nota < 70 for n in notas)
        # Adiciona os dados ao relatório
        relatorio.append({'aluno': aluno, 'media': media, 'atencao': atencao})
        nomes.append(aluno.complet_name_aluno)
        medias.append(float(media) if media is not None else 0)
        cores.append('red' if atencao else 'skyblue')
    grafico = None
    # Gera o gráfico se houver alunos
    if nomes:
        from .utils.graphs import gerar_grafico_barras
        grafico = gerar_grafico_barras(nomes, medias, cores, f'Desempenho da Turma {turma.class_name}', 'Média')
    # Renderiza o relatório da turma com gráfico
    return render(request, 'relatorio_turma.html', {
        'turma': turma,
        'relatorio': relatorio,
        'grafico': grafico,
    })

def grafico_disciplina(request, materia_id):
    # Busca a matéria pelo ID
    materia = Materia.objects.get(id=materia_id)
    # Busca as notas da matéria, incluindo dados do aluno
    notas = Nota.objects.filter(materia=materia).select_related('aluno')
    # Monta listas de alunos, valores e alerta
    alunos = [n.aluno.complet_name_aluno for n in notas]
    values = [float(n.nota) for n in notas]
    atencao = [n.nota < 70 for n in notas]
    # Define cores para as barras (vermelho para notas baixas)
    cores = ['red' if a else 'orange' for a in atencao]
    # Gera o gráfico em base64
    image_base64 = gerar_grafico_barras(alunos, values, cores, f'Desempenho em {materia.name_subject}', 'Nota')
    # Renderiza o template com o gráfico e notas
    return render(request, 'grafico_disciplina.html', {
        'materia': materia,
        'grafico': image_base64,
        'notas': notas,
    })

def desempenho_index(request):
    # Renderiza a página inicial de desempenho
    return render(request, 'desempenho_index.html')

def desempenho_aluno_select(request):
    # Busca todos os alunos para seleção
    alunos = Aluno.objects.all()
    # Renderiza a página de seleção de aluno
    return render(request, 'desempenho_aluno_select.html', {'alunos': alunos})

def desempenho_turma_select(request):
    # Busca todas as turmas para seleção
    turmas = Turmas.objects.all()
    # Renderiza a página de seleção de turma
    return render(request, 'desempenho_turma_select.html', {'turmas': turmas})

def desempenho_disciplina_select(request):
    # Busca todas as matérias para seleção
    materias = Materia.objects.all()
    # Renderiza a página de seleção de disciplina
    return render(request, 'desempenho_disciplina_select.html', {'materias': materias})

# Views para Calendário Acadêmico
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import CalendarioAcademico
from django.views.generic import ListView
from datetime import datetime, date

def calendario_academico(request):
    """View para exibir o calendário acadêmico"""
    eventos = CalendarioAcademico.objects.all().order_by('data_inicio')
    
    # Separar eventos por mês para melhor organização
    eventos_por_mes = {}
    for evento in eventos:
        mes_ano = evento.data_inicio.strftime('%Y-%m')
        if mes_ano not in eventos_por_mes:
            eventos_por_mes[mes_ano] = []
        eventos_por_mes[mes_ano].append(evento)
    
    context = {
        'eventos': eventos,
        'eventos_por_mes': eventos_por_mes,
        'hoje': date.today(),
    }
    return render(request, 'calendario_academico.html', context)

def adicionar_evento_calendario(request):
    """View para adicionar um novo evento ao calendário"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        tipo_evento = request.POST.get('tipo_evento')
        turma_id = request.POST.get('turma')
        
        # Validação básica
        if not titulo or not data_inicio or not tipo_evento:
            messages.error(request, 'Título, data de início e tipo de evento são obrigatórios.')
            return render(request, 'calendario_form.html', {
                'turmas': Turmas.objects.all(),
                'tipos_evento': CalendarioAcademico.TIPO_EVENTO_CHOICES
            })
        
        # Criar o evento
        evento = CalendarioAcademico(
            titulo=titulo,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim if data_fim else None,
            tipo_evento=tipo_evento,
            turma_id=turma_id if turma_id else None
        )
        evento.save()
        
        messages.success(request, 'Evento adicionado com sucesso!')
        return redirect('calendario_academico')
    
    context = {
        'turmas': Turmas.objects.all(),
        'tipos_evento': CalendarioAcademico.TIPO_EVENTO_CHOICES
    }
    return render(request, 'calendario_form.html', context)

def editar_evento_calendario(request, evento_id):
    """View para editar um evento do calendário"""
    evento = get_object_or_404(CalendarioAcademico, id=evento_id)
    
    if request.method == 'POST':
        evento.titulo = request.POST.get('titulo')
        evento.descricao = request.POST.get('descricao')
        evento.data_inicio = request.POST.get('data_inicio')
        evento.data_fim = request.POST.get('data_fim') if request.POST.get('data_fim') else None
        evento.tipo_evento = request.POST.get('tipo_evento')
        turma_id = request.POST.get('turma')
        evento.turma_id = turma_id if turma_id else None
        
        evento.save()
        messages.success(request, 'Evento atualizado com sucesso!')
        return redirect('calendario_academico')
    
    context = {
        'evento': evento,
        'turmas': Turmas.objects.all(),
        'tipos_evento': CalendarioAcademico.TIPO_EVENTO_CHOICES
    }
    return render(request, 'calendario_form.html', context)

def excluir_evento_calendario(request, evento_id):
    """View para excluir um evento do calendário"""
    evento = get_object_or_404(CalendarioAcademico, id=evento_id)
    
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('calendario_academico')
    
    context = {'evento': evento}
    return render(request, 'confirmar_exclusao.html', context)



# Views para Agenda de Professores
from .models import AgendaProfessor, Professor

def agenda_professor(request, professor_id):
    """View para exibir a agenda de um professor específico"""
    professor = get_object_or_404(Professor, id=professor_id)
    atividades = AgendaProfessor.objects.filter(professor=professor).order_by('data', 'hora_inicio')
    
    # Separar atividades por data para melhor organização
    atividades_por_data = {}
    for atividade in atividades:
        data_str = atividade.data.strftime('%Y-%m-%d')
        if data_str not in atividades_por_data:
            atividades_por_data[data_str] = []
        atividades_por_data[data_str].append(atividade)
    
    context = {
        'professor': professor,
        'atividades': atividades,
        'atividades_por_data': atividades_por_data,
        'hoje': date.today(),
    }
    return render(request, 'agenda_professor.html', context)

def adicionar_atividade_agenda(request, professor_id):
    """View para adicionar uma nova atividade à agenda do professor"""
    professor = get_object_or_404(Professor, id=professor_id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        tipo_atividade = request.POST.get('tipo_atividade')
        
        # Validação básica
        if not titulo or not data or not hora_inicio or not tipo_atividade:
            messages.error(request, 'Título, data, hora de início e tipo de atividade são obrigatórios.')
            return render(request, 'agenda_professor_form.html', {
                'professor': professor,
                'tipos_atividade': AgendaProfessor.TIPO_ATIVIDADE_CHOICES
            })
        
        # Criar a atividade
        atividade = AgendaProfessor(
            professor=professor,
            titulo=titulo,
            descricao=descricao,
            data=data,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim if hora_fim else None,
            tipo_atividade=tipo_atividade
        )
        atividade.save()
        
        messages.success(request, 'Atividade adicionada com sucesso!')
        return redirect('agenda_professor', professor_id=professor.id)
    
    context = {
        'professor': professor,
        'tipos_atividade': AgendaProfessor.TIPO_ATIVIDADE_CHOICES
    }
    return render(request, 'agenda_professor_form.html', context)

def editar_atividade_agenda(request, atividade_id):
    """View para editar uma atividade da agenda"""
    atividade = get_object_or_404(AgendaProfessor, id=atividade_id)
    
    if request.method == 'POST':
        atividade.titulo = request.POST.get('titulo')
        atividade.descricao = request.POST.get('descricao')
        atividade.data = request.POST.get('data')
        atividade.hora_inicio = request.POST.get('hora_inicio')
        atividade.hora_fim = request.POST.get('hora_fim') if request.POST.get('hora_fim') else None
        atividade.tipo_atividade = request.POST.get('tipo_atividade')
        
        atividade.save()
        messages.success(request, 'Atividade atualizada com sucesso!')
        return redirect('agenda_professor', professor_id=atividade.professor.id)
    
    context = {
        'atividade': atividade,
        'professor': atividade.professor,
        'tipos_atividade': AgendaProfessor.TIPO_ATIVIDADE_CHOICES
    }
    return render(request, 'agenda_professor_form.html', context)

def excluir_atividade_agenda(request, atividade_id):
    """View para excluir uma atividade da agenda"""
    atividade = get_object_or_404(AgendaProfessor, id=atividade_id)
    professor_id = atividade.professor.id
    
    if request.method == 'POST':
        atividade.delete()
        messages.success(request, 'Atividade excluída com sucesso!')
        return redirect('agenda_professor', professor_id=professor_id)
    
    context = {'atividade': atividade}
    return render(request, 'confirmar_exclusao_atividade.html', context)

def lista_professores_agenda(request):
    """View para listar todos os professores para acesso às suas agendas"""
    professores = Professor.objects.all().order_by('complet_name_prof')
    
    context = {'professores': professores}
    return render(request, 'lista_professores_agenda.html', context)


# Views para Notificações
from .models import Notificacao

def listar_notificacoes(request):
    """View para listar todas as notificações"""
    notificacoes = Notificacao.objects.all().order_by('-data_criacao')
    
    context = {
        'notificacoes': notificacoes,
        'total_notificacoes': notificacoes.count(),
        'notificacoes_nao_enviadas': notificacoes.filter(enviada=False).count(),
    }
    return render(request, 'notificacoes.html', context)

def marcar_notificacao_enviada(request, notificacao_id):
    """View para marcar uma notificação como enviada"""
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    
    if request.method == 'POST':
        notificacao.enviada = True
        notificacao.data_envio = timezone.now()
        notificacao.save()
        messages.success(request, 'Notificação marcada como enviada!')
    
    return redirect('listar_notificacoes')

def excluir_notificacao(request, notificacao_id):
    """View para excluir uma notificação"""
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    
    if request.method == 'POST':
        notificacao.delete()
        messages.success(request, 'Notificação excluída com sucesso!')
        return redirect('listar_notificacoes')
    
    context = {'notificacao': notificacao}
    return render(request, 'confirmar_exclusao_notificacao.html', context)

