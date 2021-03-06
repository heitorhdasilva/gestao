# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views.generic.base import View

from gestaoapp.forms.busca import Busca
from gestaoapp.forms.projeto import FormProjeto, FormProjetoEdit
from gestaoapp.forms.projeto_membro import FormProjetoMembro
from gestaoapp.models import Coordenacao
from gestaoapp.models.projeto import Projeto
from gestaoapp.models.usuario import Usuario
from django.contrib.auth.models import User
from gestaoapp.views.loginrequired import LoginRequiredMixin


class CadastroProjeto(LoginRequiredMixin, View):
    template = 'projeto/cadastro.html'

    def get(self, request, projeto_id=None):

        if projeto_id:
            nome = Projeto.objects.get(id=projeto_id)
            form = FormProjetoEdit(instance=nome)

            projeto = Projeto.objects.get(pk=projeto_id)
            usuario = Usuario.objects.get(pk=request.user.id)

            coordenadores = Usuario.objects.filter(vinculo_institucional="Professor", is_active=True)
            coordenador = nome.coordenador
            inicio = nome.data_inicio
            termino = nome.data_fim
            membros = Usuario.objects.filter(is_active=True)
            membro = nome.membro
            editar = True

            is_coordenador(usuario=usuario, projeto=projeto)

            return render(request, self.template,
                          {'form': form, 'editar': editar, 'coordenadores': coordenadores, 'membro': membro,
                           'membros': membros, 'coordenador': coordenador, 'inicio': inicio, 'termino': termino})
        else:
            form = FormProjeto()
            coordenadores = Usuario.objects.filter(vinculo_institucional="Professor", is_active=True)
            membros = Usuario.objects.filter(is_active=True)
            # teste = request.user.first_name
            editar = False
            return render(request, self.template,
                          {'form': form, 'editar': editar, 'membros': membros, 'coordenadores': coordenadores})

    def post(self, request, projeto_id=None):

        if projeto_id:
            nome = Projeto.objects.get(id=projeto_id)
            form = FormProjetoEdit(instance=nome, data=request.POST)
        else:
            form = FormProjeto(request.POST, request.FILES)

        if form.is_valid():
            projeto = form.save(commit=False)

            usuario = Usuario.objects.get(pk=request.user.id)
            projeto.responsavel_cadastro = User.objects.get(pk=request.user.id)
            projeto.save()

            if not projeto_id:
                projeto.coordenacao = self.registrar_coordenacao(usuario, projeto)
                projeto.save()

            user = form.save(request)
            if 'imagem' in request.FILES:
                user.imagem = request.FILES['imagem']
            user.save()

            msg = "Operação realizada com sucesso!"
            form = FormProjeto()

            return render(request, self.template, {'form': form, 'msg': msg})
            # return redirect('/cadastro_sucesso')
        else:
            if projeto_id:
                nome = Projeto.objects.get(id=projeto_id)
                form = FormProjetoEdit(instance=nome, data=request.POST)
            else:
                form = FormProjeto(request.POST, request.FILES)

            return render(request, self.template, {'form': form})

    def registrar_coordenacao(self, coordenador, projeto):
        coordenacao = Coordenacao(
            coordenador=coordenador,
            projeto=projeto,
            dt_inicio=projeto.data_inicio
        )
        coordenacao.save()
        return coordenador

class ConsultaProjeto(LoginRequiredMixin, View):
    template = 'projeto/consulta.html'

    def get(self, request):
        form = Busca()
        projeto = Projeto.objects.all()
        usuario = Usuario.objects.get(pk=request.user)

        return render(request, self.template, {'projetos': projeto, "form": form, 'usuario': usuario})

    def post(self, request):
        form = Busca(request.POST)
        if form.is_valid():
            projeto = Projeto.objects.filter(nome__icontains=form.cleaned_data['nome'])

            return render(request, self.template, {'projetos': projeto, 'form': form})
        else:
            form = Busca(request.POST)
            projeto = Projeto.objects.all()
        return render(request, self.template, {'projetos': projeto, "form": form})


class VisualizarProjeto(LoginRequiredMixin, View):
    template = "projeto/visualizar.html"

    def get(self, request, projeto_id=None):

        if projeto_id:
            projeto = Projeto.objects.get(id=projeto_id)
            # membro = Usuario.objects.get(id=request.user.id)
            coordenacao = Coordenacao.objects.get(projeto=projeto, status=True)
        else:
            return render(request, self.template, {})

        return render(request, self.template, {'projeto': projeto, 'coordenacao': coordenacao})

    def post(self, request):

        return render(request, self.template)


class AddMembro(LoginRequiredMixin, View):
    template = 'projeto/add_membro.html'

    def get(self, request, projeto_id=None):

        if projeto_id:
            nome = Projeto.objects.get(id=projeto_id)
            form = FormProjetoMembro(instance=nome)
            editar = True
            return render(request, self.template, {'form': form, 'editar': editar, })
        else:
            form = FormProjetoMembro()
            coordenadores = Usuario.objects.filter(vinculo_institucional="Professor", is_active=True)
            membros = Usuario.objects.filter(is_active=True)
            editar = False

        return render(request, self.template,
                      {'form': form, 'editar': editar, 'coordenadores': coordenadores, 'membros': membros})

    def post(self, request, projeto_id=None):

        if projeto_id:
            nome = Projeto.objects.get(id=projeto_id)
            form = FormProjetoMembro(instance=nome, data=request.POST)
        else:
            form = FormProjetoMembro(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/cadastro_sucesso')
        else:
            return render(request, self.template, {'form': form})

def is_coordenador(usuario, projeto):
    if Coordenacao.objects.filter(coordenador=usuario, projeto=projeto, status=True).count() > 0:
        return True
    return False