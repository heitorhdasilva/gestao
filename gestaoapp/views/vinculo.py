#coding:utf-8
from django.shortcuts import render, redirect
from django.views.generic.base import View

from gestaoapp.models import Bolsa
from gestaoapp.models import Vinculo
from gestaoapp.views.loginrequired import LoginRequiredMixin

from gestaoapp.forms.vinculo import FormVinculo, FormVinculoBolsa

class CadastroVinculo(LoginRequiredMixin, View):

    template = 'vinculo/cadastro.html'

    def get(self, request, vinculo_id):
        if vinculo_id:
            vinculo = Vinculo.objects.get(pk=vinculo_id)
            form = FormVinculo(instance=vinculo)
            editar = True
        else:
             form = FormVinculo()
             editar = False
             vinculo = None

        return render(request, self.template, {
            'form': form,
            'editar' : editar,
            'vinculo' : vinculo,
        })

    def post(self, request,vinculo_id):
        if vinculo_id:
            vinculo = Vinculo.objects.get(id=vinculo_id)
            form = FormVinculo(instance=vinculo,data=request.POST)
        else:
            form = FormVinculo(request.POST)
            
        if form.is_valid():
            form.save()
            msg = 'Operação realizada com sucesso'
        else:
            msg = 'Algo deu errado'
        return render(request, self.template, {
            'form': form,
            'msg' : msg
        })

class CadastroVinculoBolsa(LoginRequiredMixin, View):

    template = 'vinculo/vincular_bolsa.html'

    def get(self, request, bolsa_id=None):
        if bolsa_id:
            bolsa = Bolsa.objects.get(pk=bolsa_id)
            form = FormVinculoBolsa(bolsa=bolsa)
            vinculo_atual = self.get_vinculo_atual(bolsa=bolsa)

            return render(request, self.template, {
                'bolsa': bolsa,
                'form': form,
                'vinculo_atual': vinculo_atual
            })
        return render(request, self.template, {})

    def post(self, request, bolsa_id=None):

        if bolsa_id:
            bolsa = Bolsa.objects.get(pk=bolsa_id)
            form = FormVinculoBolsa(data=request.POST)
            vinculo_atual = self.get_vinculo_atual(bolsa=bolsa)
            if form.is_valid():
                vinculo = form.save(commit=False)
                vinculo.bolsa = bolsa

                if vinculo_atual:
                    dt_termino = request.POST.get('dt_termino_vinculo_atual')
                    vinculo_atual.status = False
                    vinculo_atual.dt_termino = dt_termino
                    vinculo_atual.save()
                vinculo.save()
                msg = {'status': True, 'texto': 'Vínculo registrado com sucesso!'}
            else:
                msg = {'status': False, 'texto': 'Não foi possível registrar o novo vínculo!'}
            return render(request, self.template, {
                'bolsa': bolsa,
                'form': form,
                'msg': msg
            })
        return render(request, self.template, {})

    def get_vinculo_atual(self, bolsa):
        try:
            return Vinculo.objects.get(bolsa=bolsa, status=True)
        except:
            return None

