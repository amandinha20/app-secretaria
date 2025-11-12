from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse
def faltas_aluno_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    faltas = Falta.objects.filter(aluno=aluno, status='F')
    total_faltas = faltas.count()
    turma = aluno.class_choices
    total_aulas = Falta.objects.filter(turma=turma).values('data').distinct().count()
    percentual = (total_faltas / total_aulas * 100) if total_aulas > 0 else 0
    passou_limite = percentual > 25
    html_string = render_to_string('faltas_aluno_pdf.html', {
        'aluno': aluno,
        'faltas': faltas,
        'total_faltas': total_faltas,
        'total_aulas': total_aulas,
        'percentual': round(percentual, 2),
        'passou_limite': passou_limite
    })
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=faltas_{aluno.complet_name_aluno}.pdf'
    return response
from django.shortcuts import render, get_object_or_404
from .models import Falta, Aluno, Turmas

def faltas_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    faltas = Falta.objects.filter(aluno=aluno, status='F')
    total_faltas = faltas.count()
    turma = aluno.class_choices
    total_aulas = Falta.objects.filter(turma=turma).values('data').distinct().count()
    percentual = (total_faltas / total_aulas * 100) if total_aulas > 0 else 0
    passou_limite = percentual > 25
    return render(request, 'faltas_aluno.html', {
        'aluno': aluno,
        'faltas': faltas,
        'total_faltas': total_faltas,
        'total_aulas': total_aulas,
        'percentual': round(percentual, 2),
        'passou_limite': passou_limite
    })
from django.shortcuts import get_object_or_404, render
from django import template

# Filtro customizado para acessar dicionário por chave dinâmica
def dict_get(d, key):
    return d.get(key)

register = template.Library()
register.filter('dict_get', dict_get)
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import Aluno, Advertencia, Contrato
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DocumentoAdvertencia
import os

# View para gerar o PDF da advertência
def gerar_documentoadvertencia_pdf(request, advertencia_id):
    advertencia = get_object_or_404(Advertencia, id=advertencia_id)
    html_string = render_to_string('admin/app/documento_advertencia.html', {'advertencia': advertencia})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="documento_advertencia_{advertencia.id}.pdf"'
    pdf = weasyprint.HTML(string=html_string).write_pdf()
    response.write(pdf)
    return response

# View para gerar o PDF do contrato (exemplo de view existente)from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import FileResponse
from .models import Falta

def relatorio_faltas_pdf(request, turma_id):
    turma = Turmas.objects.get(id=turma_id)
    faltas = Falta.objects.filter(turma=turma, status='F')
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    data = [['Data', 'Aluno', 'Professor', 'Observação']]
    for falta in faltas:
        data.append([falta.data, falta.aluno.complet_name_aluno, falta.professor.username if falta.professor else '', falta.observacao or ''])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'relatorio_faltas_{turma.class_name}.pdf')

def gerar_contrato_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    html_string = render_to_string('admin/app/contrato.html', {'aluno': aluno})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contrato_{aluno.id}.pdf"'
    pdf = weasyprint.HTML(string=html_string).write_pdf()
    response.write(pdf)
    return response

# View para exibir o boletim do aluno
def boletim_aluno(request, aluno_id):
    # Busca o aluno pelo ID
    aluno = get_object_or_404(Aluno, id=aluno_id)
    notas = aluno.notas.all()
    faltas = aluno.faltas.filter(status='F').count()
    media = aluno.media_notas() or 0
    context = {'aluno': aluno, 'notas': notas, 'faltas': faltas, 'media': media}
    return render(request, 'school/boletim.html', context)

# View para gerar o PDF do boletim
    # Busca as notas do aluno, otimizando com select_related para evitar múltiplas queries
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    faltas_bimestre = 0
    meses_bimestre = {
        1: [1, 2, 3],        # Janeiro, Fevereiro, Março
        2: [4, 5, 6],        # Abril, Maio, Junho
        3: [8, 9],           # Agosto, Setembro
        4: [10, 11],         # Outubro, Novembro
    }
    if bimestre:
        try:
            bimestre_int = int(bimestre)
            notas = notas.filter(bimestre=bimestre_int)
            bimestre = bimestre_int
            # Contar faltas e presenças do aluno no bimestre selecionado
            from .models import Falta
            meses = meses_bimestre.get(bimestre_int, [])
            faltas_bimestre = Falta.objects.filter(aluno=aluno, status='F', data__month__in=meses).count()
            presencas_bimestre = Falta.objects.filter(aluno=aluno, status='P', data__month__in=meses).count()
            total_chamadas = faltas_bimestre + presencas_bimestre
            if total_chamadas > 0:
                porcentagem_presenca = round((presencas_bimestre / total_chamadas) * 100, 1)
            else:
                porcentagem_presenca = None
        except ValueError:
            bimestre = ''
            porcentagem_presenca = None
        tem_alerta = any(nota.nota < 70 for nota in notas)
        # Filtra apenas matérias que possuem nota lançada neste bimestre
        materias = [nota.materia for nota in notas]
        # Remove duplicatas mantendo a ordem
        materias = list(dict.fromkeys(materias))
        for materia in materias:
            materia.nota_bimestre = notas.filter(materia=materia).first()
        return render(request, 'boletim_select_bimestre.html', {
            'aluno': aluno,
            'notas': notas,
            'tem_alerta': tem_alerta,
            'bimestre': bimestre,
            'bimestre_choices': BIMESTRE_CHOICES,
            'faltas_bimestre': faltas_bimestre,
            'materias': materias,
            'porcentagem_presenca': porcentagem_presenca,
        })
    else:
        # Organiza as notas por matéria e bimestre
        materias = list(Materia.objects.all())
        notas_dict = {m.id: {} for m in materias}
        for nota in notas:
            notas_dict[nota.materia.id][nota.bimestre] = nota
        materias_com_nota = []
        for materia in materias:
            materia.notas_por_bimestre = notas_dict.get(materia.id, {})
            if materia.notas_por_bimestre:
                materias_com_nota.append(materia)
        tem_alerta = any(nota.nota < 70 for nota in notas)
        # Calcular o total de faltas em todos os bimestres
        from .models import Falta
        total_faltas = aluno.faltas.filter(status='F').count()
        return render(request, 'boletim_select_bimestre.html', {
            'aluno': aluno,
            'materias': materias_com_nota,
            'tem_alerta': tem_alerta,
            'bimestre': bimestre,
            'bimestre_choices': BIMESTRE_CHOICES,
            'faltas_bimestre': total_faltas,
        })
    # Verifica se existe alguma nota abaixo de 70 para alerta
    tem_alerta = any(nota.nota < 70 for nota in notas)
    # Renderiza o boletim do aluno com as notas e alerta
    return render(request, 'boletim.html', {'aluno': aluno, 'notas': notas, 'tem_alerta': tem_alerta})

def boletim_aluno_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno.objects.prefetch_related('notas__materia'), id=aluno_id)
    bimestre = request.GET.get('bimestre')
    # Carrega todas as matérias e notas do aluno de uma vez
    materias = list(Materia.objects.all().only('id', 'name_subject'))
    notas = list(aluno.notas.select_related('materia').all())
    faltas_bimestre = 0
    meses_bimestre = {
        1: [1, 2, 3],        # Janeiro, Fevereiro, Março
        2: [4, 5, 6],        # Abril, Maio, Junho
        3: [8, 9],           # Agosto, Setembro
        4: [10, 11],         # Outubro, Novembro
    }
    BIMESTRE_CHOICES = [
        (1, '1º Bimestre'),
        (2, '2º Bimestre'),
        (3, '3º Bimestre'),
        (4, '4º Bimestre'),
    ]
    if bimestre:
        try:
            bimestre_int = int(bimestre)
            notas_bim = [n for n in notas if n.bimestre == bimestre_int]
            from .models import Falta
            meses = meses_bimestre.get(bimestre_int, [])
            faltas_bimestre = aluno.faltas.filter(status='F', data__month__in=meses).count()
            presencas_bimestre = aluno.faltas.filter(status='P', data__month__in=meses).count()
            total_chamadas = faltas_bimestre + presencas_bimestre
            if total_chamadas > 0:
                porcentagem_presenca = round((presencas_bimestre / total_chamadas) * 100, 1)
            else:
                porcentagem_presenca = None
        except Exception:
            notas_bim = []
            porcentagem_presenca = None
        tem_alerta = any(nota.nota < 70 for nota in notas_bim)
        for materia in materias:
            materia.nota_bimestre = next((n for n in notas_bim if n.materia_id == materia.id), None)
        context = {
            'aluno': aluno,
            'notas': notas_bim,
            'faltas_bimestre': faltas_bimestre,
            'bimestre': bimestre,
            'bimestre_choices': BIMESTRE_CHOICES,
            'tem_alerta': tem_alerta,
            'materias': materias,
            'porcentagem_presenca': porcentagem_presenca,
        }
    else:
        # Organiza as notas por matéria e bimestre sem queries extras
        materias = list(materias)
        notas_dict = {m.id: {} for m in materias}
        for nota in notas:
            notas_dict[nota.materia_id][nota.bimestre] = nota
        materias_com_nota = []
        for materia in materias:
            materia.notas_por_bimestre = notas_dict.get(materia.id, {})
            if materia.notas_por_bimestre:
                materias_com_nota.append(materia)
        tem_alerta = any(nota.nota < 70 for nota in notas)
        # Calcular o total de faltas em todos os bimestres
        from .models import Falta
        total_faltas = aluno.faltas.filter(status='F').count()
        context = {
            'aluno': aluno,
            'materias': materias_com_nota,
            'tem_alerta': tem_alerta,
            'bimestre': bimestre,
            'bimestre_choices': BIMESTRE_CHOICES,
            'faltas_bimestre': total_faltas,
        }
    import time
    t0 = time.time()
    # Busca o aluno pelo ID
    aluno = get_object_or_404(Aluno, id=aluno_id)
    # Busca as notas do aluno
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    # Monta o contexto para o template
    context = {'aluno': aluno, 'notas': notas}
    # Renderiza o HTML do boletim
    html_string = render_to_string('boletim.html', context)
    t1 = time.time()
    # Gera o PDF do boletim (sem recursos externos)
    pdf = HTML(string=html_string, base_url=None).write_pdf(stylesheets=None)
    t2 = time.time()
    print(f"Tempo render_to_string: {t1-t0:.2f}s | Tempo write_pdf: {t2-t1:.2f}s | Total: {t2-t0:.2f}s")
    # Cria a resposta HTTP com o PDF gerado
    response = HttpResponse(pdf, content_type='application/pdf')
    # Define o nome do arquivo PDF no cabeçalho da resposta
    response['Content-Disposition'] = f'inline; filename="boletim_{aluno.complet_name_aluno}.pdf"'
    notas = aluno.notas.all()
    faltas = aluno.faltas.filter(status='F').count()
    media = aluno.media_notas() or 0
    html_string = render_to_string('school/boletim.html', {'aluno': aluno, 'notas': notas, 'faltas': faltas, 'media': media})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boletim_{aluno.id}.pdf"'
    pdf = weasyprint.HTML(string=html_string).write_pdf()
    response.write(pdf)
    return response

# View para gráfico de desempenho do aluno (exemplo placeholder)
def grafico_desempenho_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    notas = aluno.notas.all()
    context = {'aluno': aluno, 'notas': notas}
    return render(request, 'school/grafico_desempenho.html', context)

# View para relatório da turma (exemplo placeholder)
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
def relatorio_faltas_excedidas(request):
    alunos_excedentes = []
    turmas = Turmas.objects.all()
    for turma in turmas:
        alunos = Aluno.objects.filter(class_choices=turma)
        total_aulas = Falta.objects.filter(turma=turma).values('data').distinct().count()
        for aluno in alunos:
            faltas = Falta.objects.filter(aluno=aluno, turma=turma, status='F').count()
            if total_aulas > 0 and faltas / total_aulas > 0.25:
                alunos_excedentes.append({
                    'aluno': aluno.complet_name_aluno,
                    'turma': turma,
                    'faltas': faltas,
                    'percentual': round(faltas / total_aulas * 100, 2)
                })
    return render(request, 'relatorio_faltas.html', {'alunos_excedentes': alunos_excedentes})

    from .models import Turmas
    turma = get_object_or_404(Turmas, id=turma_id)
    alunos = turma.aluno_set.all()
    context = {'turma': turma, 'alunos': alunos}
    return render(request, 'school/relatorio_turma.html', context)

# View para gráfico de disciplina (exemplo placeholder)
def grafico_disciplina(request, materia_id):
    from .models import Materia
    materia = get_object_or_404(Materia, id=materia_id)
    notas = materia.notas.all()
    context = {'materia': materia, 'notas': notas}
    return render(request, 'school/grafico_disciplina.html', context)

# Views de seleção (exemplos placeholder)
def desempenho_index(request):
    return render(request, 'school/desempenho_index.html')

def desempenho_aluno_select(request):
    return render(request, 'school/desempenho_aluno_select.html')

def desempenho_turma_select(request):
    return render(request, 'school/desempenho_turma_select.html')

def desempenho_disciplina_select(request):
    return render(request, 'school/desempenho_disciplina_select.html')

# View para datas de faltas (exemplo placeholder)
def faltas_datas(request):
    return render(request, 'school/faltas_datas.html')

# View para gerar PDF da advertência, com dados do aluno, motivo e data.
def gerar_documentoadvertencia_pdf(request, documentoadvertencia_id):
    doc = DocumentoAdvertencia.objects.select_related('advertencia', 'advertencia__aluno').get(id=documentoadvertencia_id)
    aluno = doc.advertencia.aluno
    motivo = doc.advertencia.motivo
    data = doc.advertencia.data
    context = {
        'aluno': aluno,
        'motivo': motivo,
        'data': data,
    }
    html_string = render_to_string('documentoadvertencia_pdf.html', context)
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="advertencia_{aluno.complet_name_aluno}.pdf"'
    return response

@receiver(post_save, sender=Advertencia)
def gerar_documento_advertencia_automatico(sender, instance, created, **kwargs):
    if created:
        # Cria o DocumentoAdvertencia vinculado
        doc = DocumentoAdvertencia.objects.create(advertencia=instance)
        # Gera o PDF automaticamente
        context = {
            'aluno': instance.aluno,
            'motivo': instance.motivo,
            'data': instance.data,
        }
        from django.template.loader import render_to_string
        html_string = render_to_string('documentoadvertencia_pdf.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        # Salva o PDF em media/documentos_advertencia/
        pasta = os.path.join(settings.MEDIA_ROOT, 'documentos_advertencia')
        os.makedirs(pasta, exist_ok=True)
        nome_arquivo = f"advertencia_{instance.aluno.id}_{instance.id}.pdf"
        caminho_arquivo = os.path.join(pasta, nome_arquivo)
        with open(caminho_arquivo, 'wb') as f:
            f.write(pdf_file)
        # Opcional: salvar o caminho do PDF no DocumentoAdvertencia (se tiver campo FileField)
        # doc.arquivo_pdf = f"documentos_advertencia/{nome_arquivo}"
        # doc.save()

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

def suspensao_select_turma(request):
    turmas = Turmas.objects.all()
    return render(request, 'suspensao_select_turma.html', {'turmas': turmas})


def suspensao_select_aluno(request, turma_id):
    alunos = Aluno.objects.filter(class_choices_id=turma_id)
    turma = Turmas.objects.get(id=turma_id)
    return render(request, 'suspensao_select_aluno.html', {'alunos': alunos, 'turma': turma})

def suspensao_create(request, turma_id, aluno_id=None):
    # Se aluno_id for fornecido, pré-seleciona; caso contrário, permite escolher no formulário
    if request.method == 'POST':
        form = SuspensaoForm(request.POST)
        if form.is_valid():
            susp = form.save(commit=False)
            if not susp.criado_por:
                susp.criado_por = request.user
            susp.save()
            return render(request, 'suspensao_success.html', {'suspensao': susp})
    else:
        initial = {}
        if aluno_id:
            initial['aluno'] = aluno_id
        if turma_id:
            initial['turma'] = turma_id
        form = SuspensaoForm(initial=initial)
    return render(request, 'suspensao_form.html', {'form': form})
