from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpRequest
from .models import Falta, Turmas, Aluno
from datetime import datetime

class AttendanceDateAdmin(admin.ModelAdmin):
    """
    Custom admin interface for viewing attendance by date
    """
    change_list_template = 'admin/attendance_date_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('by-date/', self.admin_site.admin_view(self.attendance_by_date), name='attendance_by_date'),
            path('by-date/<str:date>/', self.admin_site.admin_view(self.attendance_date_detail), name='attendance_date_detail'),
            path('by-date/<str:date>/<int:turma_id>/', self.admin_site.admin_view(self.attendance_turma_detail), name='attendance_turma_detail'),
        ]
        return custom_urls + urls
    
    def attendance_by_date(self, request):
        """Show list of unique dates with attendance records"""
        dates = Falta.objects.values('data').distinct().order_by('-data')
        
        # Add count of turmas for each date
        date_info = []
        for date_dict in dates:
            date = date_dict['data']
            turmas_count = Falta.objects.filter(data=date).values('turma').distinct().count()
            total_records = Falta.objects.filter(data=date).count()
            
            date_info.append({
                'date': date,
                'turmas_count': turmas_count,
                'total_records': total_records,
            'url': reverse('admin:school_falta_attendance_date_detail', args=[date.strftime('%Y-%m-%d')])
            })
        
        context = {
            'title': 'Chamadas Realizadas',
            'dates': date_info,
            'opts': self.model._meta,
        }
        return render(request, 'admin/attendance_by_date.html', context)
    
    def attendance_date_detail(self, request, date):
        """Show turmas for a specific date"""
        # Convert string date to date object
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        formatted_date = date_obj.strftime('%d/%m/%Y')
        
        turmas = Turmas.objects.filter(
            faltas__data=date_obj
        ).distinct()
        
        turma_info = []
        for turma in turmas:
            total_alunos = Falta.objects.filter(data=date_obj, turma=turma).count()
            presentes = Falta.objects.filter(data=date_obj, turma=turma, status='P').count()
            faltas = Falta.objects.filter(data=date_obj, turma=turma, status='F').count()
            
            turma_info.append({
                'turma': turma,
                'total_alunos': total_alunos,
                'presentes': presentes,
                'faltas': faltas,
            'url': reverse('admin:attendance_turma_detail', args=[date, turma.id])
            })
        
        context = {
            'title': f'Chamada do dia {formatted_date}',
            'date': date,  # Keep original string format for URL generation
            'formatted_date': formatted_date,
            'turmas': turma_info,
            'opts': self.model._meta,
        }
        return render(request, 'admin/attendance_date_detail.html', context)
    
    def attendance_turma_detail(self, request, date, turma_id):
        """Show attendance details for a specific date and turma"""
        from django.shortcuts import get_object_or_404
        from datetime import datetime
        
        turma = get_object_or_404(Turmas, id=turma_id)
        
        # Convert string date to date object for filtering
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            formatted_date = date_obj.strftime('%d/%m/%Y')
        except ValueError:
            date_obj = date
            formatted_date = str(date)
        
        attendance_records = Falta.objects.filter(
            data=date_obj,
            turma=turma
        ).select_related('aluno').order_by('aluno__complet_name_aluno')
        
        # Calculate summary
        total_alunos = attendance_records.count()
        presentes = attendance_records.filter(status='P').count()
        faltas = attendance_records.filter(status='F').count()
        
        context = {
            'title': f'Chamada - {turma} - {formatted_date}',
            'date': date,  # Keep as string for URL generation
            'formatted_date': formatted_date,
            'turma': turma,
            'attendance_records': attendance_records,
            'summary': {
                'total_alunos': total_alunos,
                'presentes': presentes,
                'faltas': faltas,
            },
            'opts': self.model._meta,
            'back_url': reverse('admin:attendance_date_detail', args=[date]),
        }
        return render(request, 'admin/attendance_turma_detail.html', context)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
