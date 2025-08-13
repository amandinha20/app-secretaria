from django.db import models
from .validators import validar_telefone, validar_cpf, validar_cpf_model

# Create your models here.
class Responsavel(models.Model):
    complet_name = models.CharField(max_length=50, verbose_name= "Nome completo do responsável")
    phone_number = models.CharField(max_length=15, validators=[validar_telefone], verbose_name= "Telefone (xx) xxxxx-xxxx")
    email = models.EmailField(max_length=100, verbose_name= "Email do responsável")
    cpf = models.CharField(max_length=11, unique=True, validators= [validar_cpf], verbose_name= "CPF do responsável")
    birthday = models.DateField()

    def __str__(self):
        return self.complet_name
    

class Aluno(models.Model):
    ANO_CHOICES = (
        ("1A", "1° ano A"),
        ("1B", "1° ano B"),
        ("1C", "1° ano C"),
        ("2CN", "2° ano CN"),
        ("2DS", "2° ano DS"),
        ("2JG", "2° ano JOGOS"),
        ("3CN", "3° ano CN"),
        ("3DS", "3° ano DS"),
        ("3JG", "3° ano JOGOS"),
    )

    # Informações do aluno, como telefone, matrícula, email, CPF e data de nascimento
    complet_name_aluno = models.CharField(max_length=100, verbose_name= "Nome completo do aluno")
    # Relação com o responsável
    responsavel= models.ForeignKey(Responsavel, on_delete=models.CASCADE, related_name="complet_name_aluno")
    phone_number_aluno = models.CharField(max_length=15, validators=[validar_telefone], verbose_name= "Telefone (xx) xxxxx-xxxx")
    matricula_aluno= models.CharField(max_length=50, verbose_name = "Matrícula do aluno")
    email_aluno = models.EmailField(max_length=100, verbose_name= "Email do aluno")
    cpf_aluno = models.CharField(max_length=11, unique=True, validators= [validar_cpf], verbose_name= "CPF do aluno")
    birthday_aluno = models.DateField()
    # Alterando para ForeignKey para Turmas
    class_choices = models.ForeignKey('Turmas', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Turma do aluno")

    def __str__(self):
        # Retorna o nome completo do aluno para exibição
        return self.complet_name_aluno

    def media_notas(self):
        # Calcula a média das notas do aluno usando agregação
        return self.notas.aggregate(media=models.Avg('nota'))['media']

    def total_faltas(self):
        return self.faltas.filter(status='F').count()

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Aluno"

# Modelo para registrar faltas/presenças
from django.conf import settings
# Modelo para registrar faltas/presenças
class Falta(models.Model):
    STATUS_CHOICES = (
        ('P', 'Presente'),
        ('F', 'Faltou'),
    )
    data = models.DateField(verbose_name="Data da chamada")
    turma = models.ForeignKey('school.Turmas', on_delete=models.CASCADE, related_name="faltas")
    aluno = models.ForeignKey('school.Aluno', on_delete=models.CASCADE, related_name="faltas")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="Presença/Falta")

    class Meta:
        unique_together = ('data', 'turma', 'aluno')
        verbose_name = "Falta"
        verbose_name_plural = "Faltas"

    def __str__(self):
        return f"{self.data} - {self.turma} - {self.aluno}: {self.get_status_display()}"

class Advertencia(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="advertencias")
    data = models.DateField()
    motivo = models.TextField(verbose_name="Motivo da advertência")


    def advertencia_pdf_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.id:
            url = reverse('gerar_advertencia_pdf', args=[obj.id])
            return format_html(f'<a class="button" href="{url}" target="_blank">📄 Gerar Advertência</a>')
        return "-"
    advertencia_pdf_link.short_description = "Advertência em PDF"

class DocumentoAdvertencia(models.Model):

    advertencia = models.ForeignKey('Advertencia', on_delete=models.CASCADE)
    documentoadvertencia_assinado = models.BooleanField(default=False, verbose_name="Documento de Advertência Assinado")
    documento_assinado = models.FileField(upload_to='documentos_advertencia/', blank=True, null=True, verbose_name="Arquivo do Documento de Advertência Assinado")

    def __str__(self):
        # Retorna uma string identificando o contrato pelo nome do aluno
        return f"Documento de {self.advertencia.motivo}"

    class Meta:
        verbose_name = "Documento de Advertência"
        verbose_name_plural = "Documento de Advertência"


class AlunoNotas(Aluno):
    class Meta:
        # Define como proxy para visualização de notas por aluno
        proxy = True
        verbose_name = "Notas por Aluno"
        verbose_name_plural = "Notas por Aluno"
          
class Turmas (models.Model):
    # Opções de turma (ano escolar)
    TURMA_CHOICES = [
        ('1°', '1° ano'),
        ('2°', '2° ano'),
        ('3°', '3° ano'),
    ]
    # Opções de itinerário formativo
    ITINERARIO_CHOICES =[
        ('N', 'Nenhum'),
        ('CN', 'Ciências da Natureza'),
        ('DS', 'Desenvolvimento de Sistemas'),
        ('DJ', 'DEsenvolvimento de Jogos'),
    ]

    # informações da turma, como nome, itinerário, professor padrinho e representante	
    class_name = models.CharField(max_length=50, choices=TURMA_CHOICES, verbose_name="Turma " )
    itinerary_name = models.CharField(max_length=50, choices=ITINERARIO_CHOICES, verbose_name="Itinerário a qual essa turma pertence")
    godfather_prof = models.CharField(max_length=50, verbose_name="Professor padrinho da turma")
    class_representante = models.CharField(max_length=50, verbose_name="Representante da turma")


    def __str__(self):
        # Retorna a identificação da turma e itinerário
        return self.class_name + "" + self.itinerary_name
    
    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turma"
    
class Materia(models.Model):
    # Opções de matérias/disciplina
    MATERIA_CHOICES = (
        ("DS", "Desenvolvimento de Sistemas"),
        ("CN", "Ciencias da Natureza"),
        ("DJ", "Desenvolvimento de Jogos"),
        ("MAT", "Matematica"),
        ("CH", "Ciencias Humanas"),
        ("LG", "Linguagens")    
    )
    # Nome da matéria/disciplina
    name_subject = models.CharField(max_length=50, choices=MATERIA_CHOICES, verbose_name="Selecione a Materia desejada")

    def __str__(self):
        # Retorna o nome da matéria para exibição
        return self.name_subject
    
    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplina"
    
class Professor(models.Model):
    # informações do professor, como nome completo, matéria lecionada, telefone, matrícula, email, CPF e data de nascimento
    complet_name_prof = models.CharField(max_length=50, verbose_name= "Nome completo do professor", null=True)
    materia_prof = models.CharField(max_length=50, verbose_name= "Matéria lecionada pelo professor")
    phone_number_prof = models.CharField(max_length=15, validators= [validar_telefone], verbose_name= "Telefone (xx) xxxxx-xxxx")
    matricula_prof= models.CharField(max_length=50, verbose_name = "Matrícula do professor")
    email_prof = models.EmailField(max_length=100, verbose_name= "Email do professor")
    cpf_prof = models.CharField(max_length=11, unique=True, validators= [validar_cpf], verbose_name= "'CPF do professor", blank= False, null=True)
    birthday_prof = models.DateField(max_length=10, verbose_name= "data de nascimentp do professor")
    # Relação com a matéria (objeto Materia)
    subject_choice= models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="materia", blank=False, null=True)
    # Relação com a turma (objeto Turmas)
    class_choices = models.ForeignKey(Turmas, on_delete=models.CASCADE, related_name="padrinho", blank=False, null=True)

    def __str__(self):
        # Retorna o nome completo do professor para exibição
        return self.complet_name_prof
    
    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professor"
    
class Contrato(models.Model):
    # Relação com o aluno
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE)
    # Indica se o contrato foi assinado
    contrato_assinado = models.BooleanField(default=False, verbose_name="Contrato Assinado")
    # Arquivo do contrato assinado (upload)
    arquivo_assinado = models.FileField(upload_to='contratos_assinados/', blank=True, null=True, verbose_name="Arquivo do Contrato Assinado")

    def __str__(self):
        # Retorna uma string identificando o contrato pelo nome do aluno
        return f"Contrato de {self.aluno.complet_name_aluno}"

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contrato"
    
class Nota(models.Model):
    # Relação com o aluno
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='notas')
    # Relação com a matéria
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='notas')
    # Valor da nota
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    # Observação opcional sobre a nota
    observacao = models.TextField(blank=True, null=True)
    # Data de lançamento da nota (preenchida automaticamente)
    data_lancamento = models.DateField(auto_now_add=True)

    def __str__(self):
        # Retorna uma string com nome do aluno, matéria e nota
        return f"{self.aluno.complet_name_aluno} - {self.materia.name_subject}: {self.nota}"
    
    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Nota"



