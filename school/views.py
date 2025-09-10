from django.shortcuts import render, get_object_or_404
from django import template

# Filtro customizado para acessar dicionário por chave dinâmica
def dict_get(d, key):
    return d.get(key)

register = template.Library()
register.filter('dict_get', dict_get)
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
            # Contar faltas do aluno no bimestre selecionado
            from .models import Falta
            meses = meses_bimestre.get(bimestre_int, [])
            faltas_bimestre = Falta.objects.filter(aluno=aluno, status='F', data__month__in=meses).count()
        except ValueError:
            bimestre = ''
        tem_alerta = any(nota.nota < 70 for nota in notas)
        materias = Materia.objects.all()
        # Para cada matéria, busca a nota do bimestre selecionado
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
        })
    else:
        # Organiza as notas por matéria e bimestre
        materias = Materia.objects.all()
        notas_dict = {}
        for materia in materias:
            notas_dict[materia.id] = {}
        for nota in notas:
            notas_dict[nota.materia.id][nota.bimestre] = nota
        # Adiciona as notas por bimestre em cada matéria
        for materia in materias:
            materia.notas_por_bimestre = notas_dict.get(materia.id, {})
        tem_alerta = any(nota.nota < 70 for nota in notas)
        return render(request, 'boletim_select_bimestre.html', {
            'aluno': aluno,
            'materias': materias,
            'tem_alerta': tem_alerta,
            'bimestre': bimestre,
            'bimestre_choices': BIMESTRE_CHOICES,
            'faltas_bimestre': faltas_bimestre,
        })

def boletim_aluno_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    bimestre = request.GET.get('bimestre')
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
            from .models import Falta
            meses = meses_bimestre.get(bimestre_int, [])
            faltas_bimestre = Falta.objects.filter(aluno=aluno, status='F', data__month__in=meses).count()
        except Exception:
            pass
    context = {'aluno': aluno, 'notas': notas, 'faltas_bimestre': faltas_bimestre, 'bimestre': bimestre}
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