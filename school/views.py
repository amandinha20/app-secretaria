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
from reportlab.lib import colors
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
    from .models import Nota
    aluno = get_object_or_404(Aluno, id=aluno_id)
    BIMESTRE_CHOICES = [
        (1, '1º Bimestre'),
        (2, '2º Bimestre'),
        (3, '3º Bimestre'),
        (4, '4º Bimestre'),
    ]
    bimestre = request.GET.get('bimestre')
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    if bimestre:
        notas = notas.filter(bimestre=bimestre)
        bimestre = int(bimestre)
    else:
        bimestre = ''
    tem_alerta = any(nota.nota < 70 for nota in notas)
    return render(request, 'boletim_select_bimestre.html', {
        'aluno': aluno,
        'notas': notas,
        'tem_alerta': tem_alerta,
        'bimestre': bimestre,
        'bimestre_choices': BIMESTRE_CHOICES,
    })

def boletim_aluno_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    bimestre = request.GET.get('bimestre')
    notas = Nota.objects.filter(aluno=aluno).select_related('materia')
    if bimestre:
        notas = notas.filter(bimestre=bimestre)
    context = {'aluno': aluno, 'notas': notas}
    html_string = render_to_string('boletim.html', context)
    pdf = HTML(string=html_string, base_url=None).write_pdf(stylesheets=None)
    response = HttpResponse(pdf, content_type='application/pdf')
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