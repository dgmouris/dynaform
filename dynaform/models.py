from __future__ import unicode_literals

from django.db import models
from django.utils.text import slugify
import uuid
import os
# Create your models here.

class LegalQuestionaire(models.Model):
	name = models.CharField(max_length=255)
	#def __str__(self):
	#	return self.name

	def __unicode__(self):
		return unicode(self.name)



'''
Field types to include
 - text
 - date
 - number
 - true/false
 - multiple choice field.(this is going to need a separate table? for values)

'''
FIELD_TYPE_CHOICES=(
	(0,'textfield'),
	(1,'charfield'),
	(2,'boolean'),
	(3,'integer'),
	(4,'select'),
	)

class Questions(models.Model):
	questionaire = models.ForeignKey(LegalQuestionaire)
	question_name = models.CharField(max_length=255)
	label = models.CharField(max_length=255)
	field_type = models.IntegerField(choices = FIELD_TYPE_CHOICES)

	#def __str__(self):
	#	return self.label

	def __unicode__(self):
		return unicode(self.label)

class LegalDocuments(models.Model):
	docfile = models.FileField(upload_to='documents/')
	group = models.CharField(max_length=255,default='form_group')
	slug = models.SlugField(default="abc",editable=False)
	unique_id=models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)

	def filename(self):
		return os.path.basename(self.docfile.name)

	def __unicode__(self):
		return unicode(str(self.group) + " " + str(self.unique_id))

	def save(self):
		super(LegalDocuments, self).save()
		self.slug = slugify(self.group)
		super(LegalDocuments, self).save()

	
class LegalTemplates(models.Model):
	group = models.CharField(max_length=255,default='form_group')
	slug = models.SlugField(default="abc",editable=False)	
	docfile = models.FileField(upload_to='docx-templates/')

	def __unicode__(self):
		return unicode(self.group)

	def save(self):
		super(LegalTemplates, self).save()
		self.slug = slugify(self.group)
		super(LegalTemplates, self).save()

class FormLevelThree(models.Model):
	form = models.ForeignKey(LegalQuestionaire,blank=True,null=True)
	#form = models.ForeignKey(LegalQuestionaire,blank=True,null=True)
	is_formset = models.BooleanField(default=True)
	def __unicode__(self):
		return unicode(self.form)
		
class FormLevelTwo(models.Model):
	form = models.ForeignKey(LegalQuestionaire,blank=True,null=True)
	is_formset = models.BooleanField(default=True)
	child = models.ForeignKey(FormLevelThree,blank=True,null=True)
	def __unicode__(self):
		return unicode(self.form)


class FormLevelOne(models.Model):
	form = models.ForeignKey(LegalQuestionaire,blank=True,null=True)
	is_formset = models.BooleanField(default=True)
	child = models.ForeignKey(FormLevelTwo,blank=True,null=True)
	def __unicode__(self):
		return unicode(self.form)

class FormBaseLevel(models.Model):
	group = models.CharField(max_length=255,default='form_group')
	form = models.ForeignKey(LegalQuestionaire,blank=True,null=True)
	is_formset = models.BooleanField(default=True)
	child = models.ForeignKey(FormLevelOne,blank=True,null=True)
	slug = models.SlugField(default="abc")
	def __unicode__(self):
		return unicode(self.form)

	def save(self):
		super(FormBaseLevel, self).save()
		self.slug = slugify(self.group)
		super(FormBaseLevel, self).save()
		

'''
create the 4 nest levels 
legal questionaire as foreign key
include a parent field
and a child field
as well maybe a ref field to some value in the parent or something.
''' 