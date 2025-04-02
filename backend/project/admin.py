from django.contrib import admin
from project.models import Responsavel, Aluno, Professor

class ResponsaveisAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone_number', 'email', 'adress', 'cpf', 'birthday')
    list_display_links = ('first_name', 'last_name', 'phone_number', 'email', 'adress')
    search_fields = ('first_name', 'last_name')
    list_filter = ('first_name', 'last_name')


class AlunosAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name_aluno', 'last_name_aluno', 'phone_number_aluno', 'email_aluno', 'cpf_aluno', 'birthday_aluno')
    list_display_links = ('first_name_aluno', 'last_name_aluno', 'phone_number_aluno', 'email_aluno')
    search_fields = ('first_name_aluno', 'last_name_aluno')
    list_filter = ('first_name_aluno', 'last_name_aluno')

class ProfessorAdmin(admin.ModelAdmin):

    list_display = ('id', 'first_name_prof', 'last_name_prof', 'phone_number_prof', 'email_prof', 'cpf_prof', 'birthday_prof')
    list_display_links = ('first_name_prof', 'last_name_prof', 'phone_number_prof', 'email_prof')
    search_fields = ('first_name_prof', 'last_name_prof')
    list_filter = ('first_name_prof', 'last_name_prof')


# Register your models here.
admin.site.register(Responsavel, ResponsaveisAdmin)
admin.site.register(Aluno, AlunosAdmin)
admin.site.register(Professor, ProfessorAdmin)
