from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Advertencia


def gerar_advertencia_pdf(request, advertencia_id):
    # Busca a advertência pelo ID
    advertencia = get_object_or_404(Advertencia, id=advertencia_id)

    # Contexto passado ao template
    context = {
        'advertencia': advertencia,
        'aluno': advertencia.aluno.complet_name_aluno if hasattr(advertencia.aluno, 'complet_name_aluno') else advertencia.aluno,
        'data': advertencia.data.strftime('%d/%m/%Y') if hasattr(advertencia, 'data') else '',
        'motivo': getattr(advertencia, 'motivo', ''),
    }

    # Template padrão unificado
    html_string = render_to_string('school/documentoadvertencia_pdf.html', context)

    # Gera o PDF
    pdf = HTML(string=html_string).write_pdf()

    # Retorna o PDF como resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="advertencia_{context["aluno"]}.pdf"'

    return response
