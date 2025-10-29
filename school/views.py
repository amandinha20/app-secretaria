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
    html_string = render_to_string('boletim.html', context)
    t1 = time.time()
    pdf = HTML(string=html_string, base_url=None).write_pdf(stylesheets=None)
    t2 = time.time()
    print(f"Tempo render_to_string: {t1-t0:.2f}s | Tempo write_pdf: {t2-t1:.2f}s | Total: {t2-t0:.2f}s")
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


from .forms import SuspensaoForm
from django.shortcuts import redirect


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