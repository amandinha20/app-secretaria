from django.contrib import admin
from .models import Aluno, Responsavel, Professor, Turmas, Materia, Contrato, Nota, AlunoNotas
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path, re_path

# Permite editar alunos diretamente na tela do admin do responsável
class AlunoInline(admin.TabularInline):
    model = Aluno
    extra = 0

# Admin para o modelo Responsavel
class ResponsaveisAdmin(admin.ModelAdmin):
    # Campos exibidos na lista
    list_display = ('id', 'complet_name', 'phone_number', 'email', 'cpf', 'birthday')
    # Campos que são links clicáveis
    list_display_links = ('complet_name', 'phone_number', 'email')
    # Permite busca pelo nome
    search_fields = ('complet_name',)
    # Permite filtrar pelo nome
    list_filter = ('complet_name',)
    # Exibe os alunos relacionados diretamente na tela do responsável
    inlines = [AlunoInline]

# Admin para o modelo Aluno
class AlunoAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de alunos
    list_display = (
        'id', 'complet_name_aluno', 'phone_number_aluno', 'responsavel',
        'email_aluno', 'cpf_aluno', 'birthday_aluno', 'contrato_pdf_link', 'boletim_link', 'grafico_link'
    )
    # Define quais campos serão links clicáveis na lista
    list_display_links = ('complet_name_aluno', 'phone_number_aluno', 'email_aluno')
    # Permite busca pelo nome completo do aluno
    search_fields = ('complet_name_aluno',)
    # Permite filtrar pela lista de nomes de alunos
    list_filter = ('complet_name_aluno',)

    # Adiciona um link para gerar o contrato em PDF do aluno
    def contrato_pdf_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        # Se o aluno tem ID, gera o link para a view de contrato PDF
        if obj.id:
            url = reverse('gerar_contrato_pdf', args=[obj.id])
            return format_html(f'<a class="button" href="{url}" target="_blank">📄 Gerar Contrato</a>')
        return "-"
    contrato_pdf_link.short_description = "Contrato em PDF"

    # Adiciona um link para visualizar o boletim do aluno em PDF
    def boletim_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        # Se o aluno tem ID, gera o link para a view de boletim PDF
        if obj.id:
            url = reverse('boletim_aluno_pdf', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📊 Ver Boletim</a>')
        return "-"
    boletim_link.short_description = "Boletim"

    # Adiciona um link para visualizar o gráfico de desempenho do aluno
    def grafico_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.id:
            url = reverse('grafico_desempenho_aluno', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📈 Gráfico</a>')
        return "-"
    grafico_link.short_description = "Gráfico"

# Admin para o modelo Nota
class NotaAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de notas
    list_display = ('aluno', 'materia', 'nota', 'data_lancamento', 'boletim_link')
    # Permite busca pelo nome do aluno e da matéria
    search_fields = ('aluno__complet_name_aluno', 'materia__name_subject')
    # Permite filtrar por matéria e aluno
    list_filter = ('materia', 'aluno')

    # Adiciona um link para visualizar o boletim do aluno
    def boletim_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.aluno_id:
            url = reverse('boletim_aluno', args=[obj.aluno_id])
            return format_html(f'<a href="{url}" target="_blank">📊 Ver Boletim</a>')
        return "-"
    boletim_link.short_description = "Boletim"

# Admin para o modelo Professor
class ProfessorAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de professores
    list_display = ('id', 'complet_name_prof', 'phone_number_prof', 'email_prof', 'cpf_prof', 'birthday_prof')
    list_display_links = ('complet_name_prof', 'phone_number_prof', 'email_prof')
    search_fields = ('complet_name_prof',)
    list_filter = ('complet_name_prof',)

# Admin para o modelo Turmas
class TurmasAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de turmas
    list_display = ('id', 'class_name', 'itinerary_name', 'godfather_prof', 'class_representante', 'relatorio_link')
    search_fields = ('class_name', 'itinerary_name')
    list_filter = ('class_name', 'itinerary_name')

    # Adiciona um link para visualizar o relatório da turma
    def relatorio_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.id:
            url = reverse('relatorio_turma', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📊 Relatório</a>')
        return "-"
    relatorio_link.short_description = "Relatório"

# Admin para o modelo Materia
class MateriaAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de matérias
    list_display= ('id', 'name_subject', 'grafico_link')
    search_fields= ('name_subject',)
    list_filter= ('name_subject',)

    # Adiciona um link para visualizar o gráfico da disciplina
    def grafico_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.id:
            url = reverse('grafico_disciplina', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📈 Gráfico</a>')
        return "-"
    grafico_link.short_description = "Gráfico"

# Admin para o modelo Contrato
class ContratoAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de contratos
    list_display = ('aluno', 'contrato_assinado', 'contrato_pdf_link', 'upload_contrato_assinado', 'contrato_assinado_link')
    list_filter = ('aluno', 'contrato_assinado')
    search_fields = ('aluno__complet_name_aluno',)
    autocomplete_fields = ['aluno']
    readonly_fields = ()
    fields = ('aluno',)

    # Define os campos exibidos ao adicionar ou editar
    def get_fields(self, request, obj=None):
        # Ao adicionar: só mostra o campo aluno
        if not obj:
            return ('aluno',)
        # Após salvar: mostra apenas campos do modelo
        return ['aluno', 'contrato_assinado', 'arquivo_assinado']

    # Adiciona um link para gerar o contrato em PDF
    def contrato_pdf_link(self, obj):
        if obj.aluno_id:
            url = reverse('gerar_contrato_pdf', args=[obj.aluno_id])
            return format_html(f'<a href="{url}" target="_blank">📄 Gerar Contrato</a>')
        return "-"
    contrato_pdf_link.short_description = "Contrato PDF"

    # Adiciona um link para upload do contrato assinado
    def upload_contrato_assinado(self, obj):
        if obj.id:
            url = reverse('admin:school_contrato_upload', args=[obj.id])
            return format_html(f'<a href="{url}">📤 Enviar Contrato Assinado</a>')
        return "-"
    upload_contrato_assinado.short_description = "Enviar Contrato Assinado"

    # Adiciona um link para visualizar o contrato assinado
    def contrato_assinado_link(self, obj):
        if obj.arquivo_assinado:
            return format_html(f'<a href="{obj.arquivo_assinado.url}" target="_blank">📥 Visualizar Contrato Assinado</a>')
        return "-"
    contrato_assinado_link.short_description = "Contrato Assinado (PDF)"

    # Adiciona uma URL customizada para upload do contrato assinado
    def get_urls(self):
        from django.urls import re_path
        urls = super().get_urls()
        custom_urls = [
            re_path(r'^(?P<object_id>\d+)/upload/$', self.admin_site.admin_view(self.upload_view), name='school_contrato_upload'),
        ]
        return custom_urls + urls

    # View para upload do contrato assinado
    def upload_view(self, request, object_id):
        from django.shortcuts import redirect, get_object_or_404
        from django.contrib import messages
        obj = get_object_or_404(Contrato, pk=object_id)
        # Se for POST e houver arquivo, salva o contrato assinado
        if request.method == 'POST' and request.FILES.get('arquivo_assinado'):
            obj.arquivo_assinado = request.FILES['arquivo_assinado']
            if 'contrato_assinado' in request.POST:
                obj.contrato_assinado = True
            obj.save()
            messages.success(request, 'Contrato assinado enviado com sucesso!')
            return redirect('admin:school_contrato_change', obj.id)
        from django.template.response import TemplateResponse
        # Renderiza o template de upload
        context = dict(
            self.admin_site.each_context(request),
            title='Enviar Contrato Assinado',
            original=obj,
            opts=self.model._meta,
        )
        return TemplateResponse(request, 'admin/contrato_upload.html', context)

# Permite editar notas diretamente na tela do admin do aluno
class NotaInline(admin.TabularInline):
    model = Nota
    extra = 1

# Admin para o proxy AlunoNotas (visualização de notas por aluno)
class AlunoNotasAdmin(admin.ModelAdmin):
    # Campos exibidos na lista
    list_display = ('complet_name_aluno', 'responsavel', 'get_turma')
    search_fields = ('complet_name_aluno',)
    inlines = [NotaInline]
    readonly_fields = ('instrucoes_notas',)
    fields = ('complet_name_aluno', 'responsavel', 'class_choices', 'instrucoes_notas')

    # Adiciona instruções customizadas na tela de notas
    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['custom_help'] = mark_safe(
            '<div style="margin: 10px 0; padding: 10px; background: #e6f7ff; border: 1px solid #91d5ff; color: #005580; font-weight: bold;">'
            'Clique no nome do aluno para adicionar ou visualizar as notas.'
            '</div>'
        )
        return super().changelist_view(request, extra_context=extra_context)

    # Campo somente leitura com instruções
    def instrucoes_notas(self, obj):
        return (
            '<span style="color: #31708f; font-weight: bold;">'
            'Para adicionar notas, utilize o formulário abaixo e clique em "Adicionar Nota".'
            '</span>'
        )
    instrucoes_notas.short_description = "Como adicionar notas"
    instrucoes_notas.allow_tags = True

    # Exibe a turma do aluno
    def get_turma(self, obj):
        return obj.class_choices
    get_turma.short_description = 'Turma'

    # Impede adicionar novos alunos via proxy
    def has_add_permission(self, request):
        return False

    # Impede deletar alunos via proxy
    def has_delete_permission(self, request, obj=None):
        return False

    # Usa todos os alunos para o proxy
    def get_queryset(self, request):
        return Aluno.objects.all()

# Registra todos os modelos e admins customizados no admin do Django
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(AlunoNotas, AlunoNotasAdmin)
admin.site.register(Responsavel, ResponsaveisAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Turmas, TurmasAdmin)
admin.site.register(Materia, MateriaAdmin)
admin.site.register(Contrato, ContratoAdmin)