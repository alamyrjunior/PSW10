from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.http import HttpResponse
from django.contrib.messages import constants, add_message
from paciente.models import Consulta, Documento
from datetime import datetime, timedelta

# Create your views here.
def cadastro_medico(request):

    if is_medico(request.user):
        add_message(request, constants.WARNING, 'Você já é um médico')
        return redirect('/medicos/abrir_horario')
    

    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        context = {'especialidades': especialidades,  "is_medico": is_medico(request.user)}
        
        return render(request, 'medico/cadastro_medico.html', context=context)
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.POST.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')
        
        dados_medicos = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            cedula_identidade_medica=cim,
            rg=rg,
            foto=foto,
            especialidade_id=especialidade,
            descricao=descricao,
            valor_consulta=valor_consulta,
            user=request.user
        )
        
        dados_medicos.save()
        
        add_message(request, constants.SUCCESS, 'Cadastro médico realizado')
        
        return redirect('/medicos/abrir_horario')
    
def abrir_horario(request):
    
    if not is_medico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos poderm abrir horários')
        return redirect('/usuarios/sair')
    
    if request.method == "GET":
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        context = {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas,  "is_medico": is_medico(request.user)}
        
        return render(request, 'abrir_horario.html', context)
    
    elif request.method == "POST":
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')
        
        if data_formatada <= datetime.now():
            add_message(request, constants.WARNING, 'A data não pode ser anterior a data atual')
            
            return redirect('/medicos/abrir_horario')
        
        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
        )
        
        horario_abrir.save()
        add_message(request, constants.SUCCESS,'Horário cadastrado com sucesso.')
        return redirect('/medicos/abrir_horario')       
        
        
def consultas_medico(request):
    if not is_medico(request.user):
        add_message(request, constants.WARNING, "Somente médicos podem abrir horários")
        return redirect('/usuarios/sair')
    
    hoje = datetime.now().date()
    
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
    context = {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes,  "is_medico": is_medico(request.user)}
    return render(request, 'consultas_medico.html', context)

def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        add_message(request, constants.WARNING, "Somente médicos podem abrir horários")
        return redirect('/usuarios/sair')
    
    if request.method == "GET":
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        context = {"consulta": consulta, "documentos": documentos}
        return render(request, 'consulta_area_medico.html', context)
    elif request.method == "POST":
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')
        
        if consulta.status == "C":
            add_message(request, constants.WARNING, 'Essa consulta foi cancelada.')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        elif consulta.status == "F":
            add_message(request, constants.WARNING, 'Essa consulta já foi finalizada.')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        consulta.link = link
        consulta.status = "I"
        consulta.save()
        add_message(request, constants.SUCCESS, "Consulta inicializada")
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        add_message(request, constants.WARNING, "Somente médicos podem abrir horários")
        return redirect('/usuarios/sair')
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        add_message(request, constants.ERROR, "Essa consulta não é sua!")
        return redirect(f'/medicos/abrir_horario')
        
    consulta.status = "F"
    consulta.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

def add_documento(request, id_consulta):
    if not is_medico(request.user):
        add_message(request, constants.WARNING, "Somente médicos podem abrir horários")
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        add_message(request, constants.ERROR, "Essa consulta não é sua!")
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')
    
    if not documento:
        add_message(request, constants.WARNING, "Preencha o campo documento")
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento
    )
    documento.save()
    add_message(request, constants.SUCCESS, 'Documento enviado com sucesso.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    