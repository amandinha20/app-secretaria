from django.db.models.signals import post_save
from django.dispatch import receiver

import os
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Advertencia, DocumentoAdvertencia


@receiver(post_save, sender=Advertencia)
def criar_documento_advertencia(sender, instance, created, **kwargs):
    if created:
        # Dados para o documento
        aluno_nome = instance.aluno.complet_name_aluno
        data = instance.data.strftime('%d/%m/%Y')
        motivo = instance.motivo
        responsavel_nome = instance.aluno.responsavel.complet_name

        html_content = f"""
        <html>
        <head><meta charset='utf-8'><title>Advertência</title></head>
        <body>
            <h2>Advertência Escolar</h2>
            <p><strong>Aluno:</strong> {aluno_nome}</p>
            <p><strong>Data:</strong> {data}</p>
            <p><strong>Motivo:</strong> {motivo}</p>
            <br><br>
            <p><strong>Responsável:</strong> {responsavel_nome}</p>
            <p>Assinatura: ____________________________________________</p>
        </body>
        </html>
        """

        # Nome do arquivo
        filename = f"advertencia_{instance.id}_{aluno_nome.replace(' ', '_')}.html"
        documento = DocumentoAdvertencia.objects.create(advertencia=instance)
        documento.documento_assinado.save(filename, ContentFile(html_content.encode('utf-8')))
        documento.save()
