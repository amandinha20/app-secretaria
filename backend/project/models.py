from django.db import models
from django.core.exceptions import ValidationError
import django.db import models

# Create your models here.
def validar_telefone(value):

def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) !=11:
        return False
    soma=0
    for i in range(9):
        soma+= int(cpf[i]) * (10-i)
    resto = soma%11
    digito1= 0 if resto < 2 else 11- resto
    soma=0
    for i in range(10):
        soma += int(cpf[i]) * (11-i)
        resto= soma%11
        digito2= 0 if resto < 2 else 11 - resto
        if int(cpf[9]) == digito1 and int (cpf[10]) == digito2:
            return True
        else:
            return False
        
    def validar_cpf_model(value):
        if not validar_cpf(value):
            raise ValidationError('CPF inválido')
        
        
class Responsavel(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, valitators=[validar_telefone], verbose_name= "Digite o N° do celular (xx) xxxxx-xxxx")
    email = models.EmailField(max_length=100, verbose_name= "Email do responsável")
    adress = models.CharField(max_length=100) #melhoria: Inserir validador ou "buscador" de CEP
    cpf = models.CharField(max_length=11, unique=True, verbose_name= "Informe o CPF do responsável")
    birthday = models.DateField()

    def __str__(self):
        return self.first_name
    
    
class Aluno(models.Model):
    ANO_CHOICES = (
        ("1A", "1° ano A"),
        ("1B", "1° ano B"),
        ("1C", "1° ano C"),
        ("2A", "2° ano CN"),
        ("2B", "2° ano DS"),
        ("2C", "1° ano JOGOS"),
        ("3A", "3° ano CN"),
        ("3B", "3° ano DS"),
        ("3C", "3° ano JOGOS"),
    )

    first_name_aluno = models.CharField(max_length=50, verbose_name= "Digite o primeiro nome do aluno")
    last_name_aluno = models.CharField(max_length=50, verbose_name= "Digite o sobrenome do aluno")
    phone_number_aluno = models.CharField(max_length=15, validators=[validar_telefone], verbose_name= "Digite o N° de celular (xx) xxxxx-xxxx")
    email_aluno = models.EmailField(max_length=100, verbose_name= "Digite o Email do aluno")
    cpf_aluno = models.CharField(max_length=11, unique=True, verbose_name= "Informe o CPF do aluno")
    birthday_aluno = models.DateField()
    class_choices = models.CharField(max_length=2, choices=ANO_CHOICES, blank=True, null=False)

    def __str__(self):
        return self.first_name_aluno
    
    
class Professor(models.Model):
    first_name_prof = models.CharField(max_length=50, verbose_name= "Digite o primeiro nome do professor")
    last_name_prof = models.CharField(max_length=50, verbose_name= "Digite o sobrenome do professor")
    phone_number_prof = models.CharField(max_length=15, valitators= [validar_telefone], verbose_name= "Digite o N° de celular (xx) xxxxx-xxxx")
    email_prof = models.EmailField(max_length=100, verbose_name= "Digite o Email do professor")
    cpf_prof = models.CharField(max_length=11, unique=True, verbose_name= "Informe o CPF do professor")
    birthday_prof = models.DateField()

    def __str__(self):
        return self.first_name_prof
    
class Turmas (models.Model):
    TURMA_CHOICES = [
        (1, '1° ano')
        (2, '2° ano')
        (3, '3° ano')
    ]
    ITINERARIO_CHOICES =[
        ('CN', 'Ciências da Natureza'),
        ('DS', 'Desenvolvimento de Sistemas'),
        ('DJ', 'DEsenvolvimento de Jogos'),
    ]

    nome = models.CharField(max_length=50)
    class_name = models.CharField(max_length=50, verbose_name = "Digite qual a turma " )
    itinerary_name = models.CharField(max_length=50, verbose_name = "Digite o itinerário a qual essa turma pertence")
    godfather_prof = models.CharField(max_length=50, verbose_name = "Digite o nome do professor padrinho da turma")
    class_representative = models.Field(max_legth=50, verbose_name = "Digite o nome do(a) representante da turma")
    models.ForeignKey(Professor, on_delete= models.CASCADE)

    def __str__(self):
        return f"{self.get_class_name_display()} - {self.get_itinerary_name_display()}"
    
class Contrato(models.Model):
    contrato_name = models.CharField(max_length=50, verbose_name= "Digite o nome do aluno que deseja realizar o contrato" )
    models.OneToOneField(Aluno, on_delete= models.CASCADE)
    data_contrato = models.CharField(max_length=50, verbose_name= "Digite a data do contrato")
    models.DateField(auto_now_add=True)
    conteudo= models.TextField()

    def __str__(self):
        return f"Contrato de {self.contrato_name}"

