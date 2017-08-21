# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.models import User

from gestaoapp.forms.bolsa import FormBolsa, FormBolsaEdit
from gestaoapp.forms.busca import Busca
from gestaoapp.forms.vinculo import FormVinculoBolsa
from gestaoapp.models import Vinculo
from gestaoapp.models.bolsa import Bolsa
from gestaoapp.models.usuario import Usuario
from gestaoapp.views.loginrequired import LoginRequiredMixin

class CadastroBolsa(LoginRequiredMixin, View):
    template = 'bolsa/cadastro.html'

    def get(self, request, bolsa_id=None):

        if bolsa_id:
            bolsa = Bolsa.objects.get(id=bolsa_id)
            form = FormBolsaEdit(instance=bolsa)
            editar = True
        else:
            form = FormBolsa()
            editar = False

        return render(request, self.template, {'form': form, 'editar': editar})

    def post(self, request, bolsa_id=None):

        if bolsa_id:
            bolsa = Bolsa.objects.get(id=bolsa_id)
            form = FormBolsaEdit(instance=bolsa, data=request.POST)
        else:
            form = FormBolsa(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.responsavel_cadastro = User.objects.get(pk=request.user.id)
            post.save()

            form.save(request)
            msg = "Operação realizada com sucesso!"

            form = FormBolsa()

            return render(request, self.template, {'form': form, 'msg': msg})
            # return redirect('/cadastro_sucesso')

        else:
            return render(request, self.template, {'form': form})


class ConsultaBolsa(LoginRequiredMixin, View):
    template = 'bolsa/consulta.html'

    def get(self, request):
        form = Busca()
        bolsa = Bolsa.objects.all()

        return render(request, self.template, {'bolsas': bolsa, "form": form})

    def post(self, request):
        form = Busca(request.POST)
        if form.is_valid():
            bolsa = Bolsa.objects.filter(nome__icontains=form.cleaned_data['codigo'])

            return render(request, self.template, {'bolsas': bolsa, 'form': form})
        else:
            form = Busca(request.POST)
            bolsa = Bolsa.objects.all()
        return render(request, self.template, {'bolsas': bolsa, "form": form})


class VisualizarBolsa(LoginRequiredMixin, View):
    template = "bolsa/visualizar.html"

    def get(self, request, bolsa_id=None):

        if bolsa_id:
            bolsa = Bolsa.objects.get(id=bolsa_id)
            vinculos = Vinculo.objects.filter(bolsa=bolsa).order_by('-dt_inicio')
        else:
            return render(request, self.template, {})

        return render(request, self.template, {'bolsa': bolsa, 'vinculos': vinculos})

    def post(self, request):

        return render(request, self.template)
