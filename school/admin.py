from django.contrib import admin
from .models import Aluno, Responsavel, Professor, Turmas, Materia, Contrato, Nota, AlunoNotas, Falta, Advertencia, DocumentoAdvertencia
from .admin_attendance import AttendanceDateAdmin
from datetime import datetime
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils import timezone
import csv
 # Removido import de AttendanceDate, modelo não existe
# Admin para DocumentoAdvertencia
class DocumentoAdvertenciaAdmin(admin.ModelAdmin):
    list_display = ('advertencia', 'documentoadvertencia_assinado', 'documento_assinado')
    search_fields = ('advertencia__aluno__complet_name_aluno',)

admin.site.register(DocumentoAdvertencia, DocumentoAdvertenciaAdmin)
# Admin para o modelo Falta (chamada)


class FaltaAdmin(admin.ModelAdmin):
    list_display = ('data', 'turma', 'aluno', 'professor', 'status')
    list_filter = ('data', 'turma', 'status', 'professor')
    search_fields = ('aluno__complet_name_aluno', 'turma__class_name', 'professor__username')
    # Remova ou defina FaltaForm se necessário
    # form = FaltaForm  # Comente ou remova se não tiver o formulário
    actions = ['gerar_relatorio_faltas']

    def gerar_relatorio_faltas(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="relatorio_faltas_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Data', 'Turma', 'Aluno', 'Professor', 'Status', 'Observação'])
        
        for falta in queryset:
            writer.writerow([
                falta.data,
                falta.turma,
                falta.aluno.complet_name_aluno,
                falta.professor.username if falta.professor else '',
                falta.get_status_display(),
                falta.observacao or ''
            ])
        
        return response

    gerar_relatorio_faltas.short_description = "Gerar relatório de faltas em CSV"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:turma_id>/chamada/', self.admin_site.admin_view(self.fazer_chamada), name='fazer_chamada'),
        ]
        return custom_urls + urls

    def fazer_chamada(self, request, turma_id):
        turma = get_object_or_404(Turmas, id=turma_id)
        alunos = Aluno.objects.filter(class_choices=turma).order_by('complet_name_aluno')

        if request.method == 'POST':
            data = request.POST.get('data')
            if not data:
                messages.error(request, 'Por favor, selecione uma data válida.')
                return redirect(request.path_info)
            
            try:
                data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Formato de data inválido.')
                return redirect(request.path_info)
            
            for aluno in alunos:
                status = request.POST.get(f'status_{aluno.id}')
                if status in ['P', 'F']:
                    Falta.objects.update_or_create(
                        data=data_obj,
                        turma=turma,
                        aluno=aluno,
                        defaults={'status': status, 'professor': request.user if request.user.is_staff else None}
                    )
            messages.success(request, 'Chamada registrada com sucesso!')
            return redirect('admin:school_turmas_changelist')
        
        return render(request, 'admin/fazer_chamada.html', {
            'title': f'Chamada da turma {turma.class_name}',
            'turma': turma,
            'alunos': alunos,
            'data_atual': timezone.now().date().strftime('%Y-%m-%d'),
        })

    # ...existing code...
    list_display = ('data', 'turma', 'aluno', 'status', 'chamada_link')
    list_filter = ('data', 'turma', 'status')
    search_fields = ('aluno__complet_name_aluno', 'turma__class_name')
    form = FaltaForm

    # Exibe só alunos da turma selecionada
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'aluno' and request.GET.get('turma'):
            turma_id = request.GET.get('turma')
            kwargs["queryset"] = Aluno.objects.filter(class_choices=turma_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def chamada_link(self, obj):
        url = f"/admin/school/turmas/{obj.turma.id}/chamada/"
        return format_html(f'<a href="{url}">📝 Fazer Chamada</a>')
    chamada_link.short_description = "Fazer Chamada"

# admin.site.register(Falta, FaltaAdmin)  # Removido para evitar conflito com AttendanceDateAdmin
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
        # Se o aluno tem ID, gera o link para a view de boletim com seleção de bimestre
        if obj.id:
            url = reverse('boletim_aluno', args=[obj.id])
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

class AdvertenciaAdmin(admin.ModelAdmin):
    list_display = ('aluno','data', 'motivo')
    search_fields = ('aluno__complet_name_aluno', 'motivo')
    litst_filter = ('data')

    def __str__(self):
        return self.motivo[:200]  # Retorna os primeiros 200 caracteres do motivo
    

class DocumentoAdvertenciaAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de contratos
    list_display = ('advertencia', 'documentoadvertencia_assinado', 'documentoadvertencia_pdf_link', 'upload_documentoadvertencia_assinado', 'documentoadvertencia_assinado_link')
    list_filter = ('advertencia', 'documentoadvertencia_assinado')
    search_fields = ('advertencia__complet_name_advertencia',)
    autocomplete_fields = ['advertencia']
    readonly_fields = ()
    fields = ('advertencia',)

    # Define os campos exibidos ao adicionar ou editar
    def get_fields(self, request, obj=None):
        # Ao adicionar: só mostra o campo advertencia
        if not obj:
            return ('advertencia',)
        # Após salvar: mostra apenas campos do modelo
        return ['advertencia', 'documentoadvertencia_assinado', 'arquivo_assinado']

    # Adiciona um link para gerar o documentoadvertencia em PDF
    def documentoadvertencia_pdf_link(self, obj):
        if obj.advertencia_id:
            url = reverse('gerar_documentoadvertencia_pdf', args=[obj.advertencia_id])
            return format_html(f'<a href="{url}" target="_blank">📄 Gerar documentoadvertencia</a>')
        return "-"
    documentoadvertencia_pdf_link.short_description = "documentoadvertencia PDF"

    # Adiciona um link para upload do documentoadvertencia assinado
    def upload_documentoadvertencia_assinado(self, obj):
        if obj.id:
            url = reverse('admin:school_documentoadvertencia_upload', args=[obj.id])
            return format_html(f'<a href="{url}">📤 Enviar documentoadvertencia Assinado</a>')
        return "-"
    upload_documentoadvertencia_assinado.short_description = "Enviar documentoadvertencia Assinado"

    # Adiciona um link para visualizar o documentoadvertencia assinado
    def documentoadvertencia_assinado_link(self, obj):
        if obj.arquivo_assinado:
            return format_html(f'<a href="{obj.arquivo_assinado.url}" target="_blank">📥 Visualizar documentoadvertencia Assinado</a>')
        return "-"
    documentoadvertencia_assinado_link.short_description = "documentoadvertencia Assinado (PDF)"

    # Adiciona uma URL customizada para upload do documentoadvertencia assinado
    def get_urls(self):
        from django.urls import re_path
        urls = super().get_urls()
        custom_urls = [
            re_path(r'^(?P<object_id>\d+)/upload/$', self.admin_site.admin_view(self.upload_view), name='school_documentoadvertencia_upload'),
        ]
        return custom_urls + urls

    # View para upload do documentoadvertencia assinado
    def upload_view(self, request, object_id):
        from django.shortcuts import redirect, get_object_or_404
        from django.contrib import messages
        from django.template.response import TemplateResponse
        obj = get_object_or_404(DocumentoAdvertencia, pk=object_id)
        if request.method == 'POST' and request.FILES.get('arquivo_assinado'):
            obj.arquivo_assinado = request.FILES['arquivo_assinado']
            if 'documentoadvertencia_assinado' in request.POST:
                obj.documentoadvertencia_assinado = True
            obj.save()
            messages.success(request, 'documentoadvertencia assinado enviado com sucesso!')
            return redirect('admin:school_documentoadvertencia_change', obj.id)
        context = dict(
            self.admin_site.each_context(request),
            title='Enviar documentoadvertencia Assinado',
            original=obj,
            opts=self.model._meta,
        )
        return TemplateResponse(request, 'admin/contrato_upload.html', context)
# Admin para o modelo Nota
class NotaAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de notas
    list_display = ('aluno', 'materia', 'bimestre', 'nota', 'data_lancamento', 'boletim_link')
    # Permite busca pelo nome do aluno e da matéria
    search_fields = ('aluno__complet_name_aluno', 'materia__name_subject')
    # Permite filtrar por matéria, aluno e bimestre
    list_filter = ('materia', 'aluno', 'bimestre')
    # Inclui o campo bimestre no formulário
    fields = ('aluno', 'materia', 'bimestre', 'nota', 'observacao')

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
from django.shortcuts import render, redirect
from django.urls import path



class TurmasAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de turmas
    list_display = ('id', 'class_name', 'itinerary_name', 'godfather_prof', 'class_representante', 'relatorio_link', 'chamada_link')
    search_fields = ('class_name', 'itinerary_name')
    list_filter = ('class_name', 'itinerary_name')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:turma_id>/chamada/', self.admin_site.admin_view(self.fazer_chamada), name='fazer_chamada'),
        ]
        return custom_urls + urls

    def fazer_chamada(self, request, turma_id):
        from .models import Falta, Aluno
        from django.shortcuts import get_object_or_404
        from django.contrib import messages
        turma = get_object_or_404(Turmas, id=turma_id)
        alunos = Aluno.objects.filter(class_choices=turma).order_by('complet_name_aluno')
        if request.method == 'POST':
            data = request.POST.get('data')
            if not data:
                messages.error(request, 'Por favor, selecione uma data válida.')
                return redirect(request.path_info)
            try:
                data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Formato de data inválido.')
                return redirect(request.path_info)
            for aluno in alunos:
                status = request.POST.get(f'status_{aluno.id}')
                if status in ['P', 'F']:
                    Falta.objects.update_or_create(
                        data=data_obj,
                        turma=turma,
                        aluno=aluno,
                        defaults={'status': status}
                    )
            messages.success(request, 'Chamada registrada com sucesso!')
            return redirect('admin:school_turmas_changelist')
        return render(request, 'admin/fazer_chamada.html', {
            'title': f'Chamada da turma {turma.class_name}',
            'turma': turma,
            'alunos': alunos,
        })

    def chamada_link(self, obj):
        url = f"/admin/school/turmas/{obj.id}/chamada/"
        return format_html(f'<a href="{url}">📝 Fazer Chamada</a>')
    chamada_link.short_description = "Chamada"

    # Adiciona um link para visualizar o relatório da turma
    def relatorio_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.id:
            url = reverse('relatorio_turma', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank">📊 Relatório</a>')
        return "-"
    relatorio_link.short_description = "Relatório"

    def relatorio_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.id:
            url = reverse('relatorio_faltas_pdf', args=[obj.id])
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

# Inline customizado para Nota, sem campo bimestre
class NotaInline(admin.TabularInline):
    model = Nota
    extra = 1
    fields = ('materia', 'nota', 'observacao')
    # Remove bimestre do inline
    def get_fields(self, request, obj=None):
        return ('materia', 'nota', 'observacao')

# Admin para o proxy AlunoNotas (visualização de notas por aluno)

from .forms_batch import BimestreBatchForm
from django.shortcuts import render, redirect
from django.contrib import messages

class AlunoNotasAdmin(admin.ModelAdmin):
    list_display = ('complet_name_aluno', 'responsavel', 'get_turma')
    search_fields = ('complet_name_aluno',)
    inlines = [NotaInline]
    readonly_fields = ('instrucoes_notas',)
    fields = ('complet_name_aluno', 'responsavel', 'class_choices', 'instrucoes_notas')

    def get_turma(self, obj):
        return obj.class_choices
    get_turma.short_description = 'Turma'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return Aluno.objects.all()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Adiciona o formulário de bimestre ao contexto
        if extra_context is None:
            extra_context = {}
        # Sempre cria o form de bimestre com os dados do POST, se houver
        if request.method == 'POST':
            bimestre_form = BimestreBatchForm(request.POST)
        else:
            bimestre_form = BimestreBatchForm()
        extra_context['bimestre_form'] = bimestre_form
        extra_context['custom_help'] = mark_safe(
            '<div style="margin: 10px 0; padding: 10px; background: #e6f7ff; border: 1px solid #91d5ff; color: #005580; font-weight: bold;">Selecione o bimestre abaixo. Todas as notas adicionadas neste lote serão salvas para o bimestre escolhido.</div>'
        )
        # Intercepta o salvamento das notas para incluir o bimestre selecionado
        if request.method == 'POST' and bimestre_form.is_valid():
            bimestre = bimestre_form.cleaned_data['bimestre']
            # Altera o POST para incluir o bimestre em cada nota nova
            post_data = request.POST.copy()
            for key in post_data:
                if key.startswith('nota_set-') and key.endswith('-id') and not post_data[key]:
                    prefix = key[:-3]
                    post_data[prefix + '-bimestre'] = bimestre
            request.POST = post_data
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def render_change_form(self, request, context, *args, **kwargs):
        # Adiciona o formulário de bimestre acima do inline
        if 'bimestre_form' not in context:
            context['bimestre_form'] = BimestreBatchForm()
        return super().render_change_form(request, context, *args, **kwargs)

    def instrucoes_notas(self, obj):
        return mark_safe(
            '<span style="color: #31708f; font-weight: bold;">Para adicionar notas, selecione o bimestre abaixo, preencha as notas e clique em "Salvar".</span>'
        )
    instrucoes_notas.short_description = "Como adicionar notas"
    instrucoes_notas.allow_tags = True

# Registra todos os modelos e admins customizados no admin do Django
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Advertencia, AdvertenciaAdmin)
admin.site.register(AlunoNotas, AlunoNotasAdmin)
admin.site.register(Responsavel, ResponsaveisAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Turmas, TurmasAdmin)
admin.site.register(Materia, MateriaAdmin)
admin.site.register(Contrato, ContratoAdmin)

# Registra o AttendanceDateAdmin para o modelo Falta
    # ...existing code...
 # Removido registro de AttendanceDate, modelo não existe
# Registra o AttendanceDateAdmin para o modelo Falta (visualização por data)
from django.urls import path
from django.shortcuts import render, redirect
from .models import Turmas, Aluno, Falta
from django.contrib import messages

class CustomAttendanceDateAdmin(AttendanceDateAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fazer-chamada/', self.admin_site.admin_view(self.selecionar_turma_para_chamada), name='attendance_fazer_chamada'),
            path('fazer-chamada/<int:turma_id>/', self.admin_site.admin_view(self.fazer_chamada), name='attendance_fazer_chamada_turma'),
        ]
        return custom_urls + urls

    def selecionar_turma_para_chamada(self, request):
        turmas = Turmas.objects.all().order_by('class_name')
        return render(request, 'admin/selecionar_turma_chamada.html', {'turmas': turmas, 'opts': self.model._meta, 'title': 'Selecionar Turma para Chamada'})

    def fazer_chamada(self, request, turma_id):
        turma = Turmas.objects.get(id=turma_id)
        alunos = Aluno.objects.filter(class_choices=turma).order_by('complet_name_aluno')
        if request.method == 'POST':
            data = request.POST.get('data')
            if not data:
                messages.error(request, 'Por favor, selecione uma data válida.')
                return redirect(request.path_info)
            try:
                data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Formato de data inválido.')
                return redirect(request.path_info)
            for aluno in alunos:
                status = request.POST.get(f'status_{aluno.id}')
                if status in ['P', 'F']:
                    Falta.objects.update_or_create(
                        data=data_obj,
                        turma=turma,
                        aluno=aluno,
                        defaults={'status': status}
                    )
            messages.success(request, 'Chamada registrada com sucesso!')
            return redirect('admin:attendance_by_date')
        return render(request, 'admin/fazer_chamada.html', {
            'title': f'Chamada da turma {turma.class_name}',
            'turma': turma,
            'alunos': alunos,
        })

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        # Adiciona botão para fazer chamada
        extra_context['fazer_chamada_url'] = 'admin:attendance_fazer_chamada'
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Falta, CustomAttendanceDateAdmin)
