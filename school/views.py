from django.shortcuts import get_object_or_404, render
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

# View para gerar o PDF do contrato (exemplo de view existente)
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
    aluno = get_object_or_404(Aluno, id=aluno_id)
    notas = aluno.notas.all()
    faltas = aluno.faltas.filter(status='F').count()
    media = aluno.media_notas() or 0
    context = {'aluno': aluno, 'notas': notas, 'faltas': faltas, 'media': media}
    return render(request, 'school/boletim.html', context)

# View para gerar o PDF do boletim
def boletim_aluno_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
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