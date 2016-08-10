from django.db import models

class Nucleo(models.Model):
	
	nome = models.CharField(max_length=255)
	sigla = models.CharField(max_length= 5)
	descricao = models.TextField()

	def __unicode__(self):
		return self.nome