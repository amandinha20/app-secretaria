from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Advertencia

def gerar_advertencia_pdf(request, advertencia_id):
    advertencia = get_object_or_404(Advertencia, id=advertencia_id)
    context = {
        'aluno': advertencia.aluno.complet_name_aluno,
        'data': advertencia.data.strftime('%d/%m/%Y'),
        'motivo': advertencia.motivo,
    }
    html_string = render_to_string('advertencia.html', context)
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="advertencia_{advertencia.aluno.complet_name_aluno}.pdf"'
    return response
