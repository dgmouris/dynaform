from __future__ import unicode_literals

from django.db import models

# Create your models here.

class LegalQuestionaire(models.Model):
	name = models.CharField(max_length=255)
	#def __str__(self):
	#	return self.name

	def __unicode__(self):
		return unicode(self.name)


FIELD_TYPE_CHOICES=(
	(0,'textfield'),
	(1,'charfield'),
	(2,'boolean'),
	(3,'file'),
	)

class Questions(models.Model):
	questionaire = models.ForeignKey(LegalQuestionaire)
	label = models.CharField(max_length=255)
	field_type = models.IntegerField(choices = FIELD_TYPE_CHOICES)

	#def __str__(self):
	#	return self.label

	def __unicode__(self):
		return unicode(self.label)

class LegalDocuments(models.Model):
	docfile = models.FileField(upload_to='documents/')

class LegalTemplates(models.Model):
	docfile = models.FileField(upload_to='docx-templates/')