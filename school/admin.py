from django.contrib import admin
from django import forms
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
import weasyprint
from django.utils.safestring import mark_safe
from django.urls import reverse, path, re_path
from django.utils.html import format_html
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from .models import Aluno, Responsavel, Professor, Turmas, Materia, Contrato, Nota, AlunoNotas, Falta, Advertencia, DocumentoAdvertencia
from .admin_attendance import AttendanceDateAdmin

# Inline para DocumentoAdvertencia dentro de Advertencia
class DocumentoAdvertenciaInline(admin.StackedInline):
    model = DocumentoAdvertencia
    extra = 0
    fields = ('documentoadvertencia_assinado', 'arquivo_assinado', 'documentoadvertencia_pdf_link', 'upload_documentoadvertencia_assinado')
    readonly_fields = ('documentoadvertencia_pdf_link',)
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        # Só permite adicionar documento se a advertência já foi salva
        return obj is not None

    def documentoadvertencia_pdf_link(self, obj):
        if obj and obj.id:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('gerar_documentoadvertencia_pdf', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📄 Gerar PDF da Advertência</a>')
        return "-"
    documentoadvertencia_pdf_link.short_description = "PDF da Advertência"

    def upload_documentoadvertencia_assinado(self, obj):
        if obj and obj.id:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:school_documentoadvertencia_upload', args=[obj.id])
            return format_html(f'<a href="{url}">📤 Enviar Documento Assinado</a>')
        return "-"
    upload_documentoadvertencia_assinado.short_description = "Upload Documento Assinado"

# Admin para Advertencia
class AdvertenciaAdmin(admin.ModelAdmin):
    list_display = ('aluno','data', 'motivo')
    search_fields = ('aluno__complet_name_aluno', 'motivo')
    list_filter = ('data',)
    inlines = [DocumentoAdvertenciaInline]
    actions = ['gerar_e_enviar_documento']

    def gerar_e_enviar_documento(self, request, queryset):
        for advertencia in queryset:
            # Gera o PDF
            html_string = render_to_string('admin/app/documento_advertencia.html', {'advertencia': advertencia})
            pdf = weasyprint.HTML(string=html_string).write_pdf()

            # Obtém o e-mail do responsável
            responsavel = advertencia.aluno.responsavel
            if not responsavel or not responsavel.email:
                self.message_user(request, f"Erro: Não há e-mail para o responsável de {advertencia.aluno.complet_name_aluno}.", level='ERROR')
                continue

            # Prepara o e-mail
            subject = f"Documento de Advertência - {advertencia.aluno.complet_name_aluno}"
            body = f"Prezado(a) {responsavel.complet_name},\n\nSegue em anexo o documento de advertência para assinatura. Por favor, assine digitalmente (usando uma ferramenta como Adobe Acrobat ou similar) e envie de volta através do sistema ou pelo e-mail {responsavel.email}. Data de emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\nAtenciosamente,\nEquipe Escolar"
            from_email = "seuemail@exemplo.com"  # Configure no settings.py
            to_email = [responsavel.email]

            # Envia o e-mail com o PDF
            try:
                send_mail(subject, body, from_email, to_email, fail_silently=False, attachments=[('advertencia.pdf', pdf, 'application/pdf')])
            except Exception as e:
                self.message_user(request, f"Erro ao enviar e-mail para {responsavel.email}: {str(e)}", level='ERROR')
                continue

            # Cria ou atualiza o DocumentoAdvertencia
            documento, created = DocumentoAdvertencia.objects.get_or_create(advertencia=advertencia)
            documento.documentoadvertencia_assinado = False
            documento.save()

        self.message_user(request, "Documentos gerados e enviados com sucesso.")
    gerar_e_enviar_documento.short_description = "Gerar e Enviar Documento de Advertência"

    def get_inline_instances(self, request, obj=None):
        # Só mostra o inline se a advertência já foi salva
        if obj:
            return super().get_inline_instances(request, obj)
        return []

# Admin para AlunoNotas (proxy para visualizar notas)
class AlunoNotasAdmin(admin.ModelAdmin):
    list_display = ('complet_name_aluno', 'responsavel', 'get_turma')
    search_fields = ('complet_name_aluno',)
    inlines = []

    def get_turma(self, obj):
        return obj.class_choices
    get_turma.short_description = 'Turma'

    # Impede adicionar ou deletar via proxy
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Usa todos os alunos para o proxy
    def get_queryset(self, request):
        return Aluno.objects.all()

class ResponsaveisAdmin(admin.ModelAdmin):
    list_display = ('id', 'complet_name', 'phone_number', 'email', 'cpf', 'birthday')
    list_display_links = ('complet_name', 'phone_number', 'email')
    search_fields = ('complet_name',)
    list_filter = ('complet_name',)
    # Adicione outros campos e métodos conforme necessário

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id', 'complet_name_prof', 'phone_number_prof', 'email_prof', 'cpf_prof', 'birthday_prof')
    list_display_links = ('complet_name_prof', 'phone_number_prof', 'email_prof')
    search_fields = ('complet_name_prof',)
    list_filter = ('complet_name_prof',)
    # Adicione outros campos e métodos conforme necessário

class TurmasAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'itinerary_name', 'godfather_prof', 'class_representante')
    search_fields = ('class_name', 'itinerary_name')
    list_filter = ('class_name', 'itinerary_name')
    # Adicione outros campos e métodos conforme necessário

class MateriaAdmin(admin.ModelAdmin):
    list_display= ('id', 'name_subject')
    search_fields= ('name_subject',)
    list_filter= ('name_subject',)
    # Adicione outros campos e métodos conforme necessário

class ContratoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'contrato_assinado')
    list_filter = ('aluno', 'contrato_assinado')
    search_fields = ('aluno__complet_name_aluno',)
    autocomplete_fields = ['aluno']
    # Adicione outros campos e métodos conforme necessário

# Outros admins
class FaltaForm(forms.ModelForm):
    class Meta:
        model = Falta
        fields = ['data', 'turma', 'aluno', 'status']
        widgets = {
            'data': forms.SelectDateWidget(),
        }

class FaltaAdmin(admin.ModelAdmin):
    list_display = ('data', 'turma', 'aluno', 'status')
    list_filter = ('data', 'turma', 'status')
    search_fields = ('aluno__complet_name_aluno', 'turma__class_name')
    form = FaltaForm
    actions = ['ver_datas_chamadas']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        data = request.GET.get('data')
        turma = request.GET.get('turma')
        if data:
            qs = qs.filter(data=data)
        if turma:
            qs = qs.filter(turma_id=turma)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'aluno' and request.GET.get('turma'):
            turma_id = request.GET.get('turma')
            kwargs["queryset"] = Aluno.objects.filter(class_choices=turma_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def ver_datas_chamadas(self, request, queryset):
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/faltas/')
    ver_datas_chamadas.short_description = 'Visualizar datas de chamadas salvas'

# Classe AlunoAdmin (básica)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id', 'complet_name_aluno', 'phone_number_aluno', 'responsavel', 'email_aluno', 'cpf_aluno', 'birthday_aluno')
    list_display_links = ('complet_name_aluno', 'phone_number_aluno', 'email_aluno')
    search_fields = ('complet_name_aluno',)
    list_filter = ('complet_name_aluno',)

# Registra todos os modelos e admins customizados
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Advertencia, AdvertenciaAdmin)
admin.site.register(AlunoNotas, AlunoNotasAdmin)
admin.site.register(Responsavel, ResponsaveisAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Turmas, TurmasAdmin)
admin.site.register(Materia, MateriaAdmin)
admin.site.register(Contrato, ContratoAdmin)
admin.site.register(Falta, FaltaAdmin)