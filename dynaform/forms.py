from django import forms 

from .models import LegalQuestionaire,Questions

FIELD_TYPES={
	0:forms.CharField(max_length=255),
	1:forms.CharField(max_length=255),
	2:forms.BooleanField(),
	3:forms.FileField(),
}

class QuestionsForm(forms.Form):


	#this is going to pop out the questionaire id created in the view
	def __init__(self,*args,**kwargs):
		self.questionaire=kwargs.pop('questionaire')
		super(QuestionsForm,self).__init__(*args,**kwargs)
		
		#these are the questions that you can 
		questionaire = LegalQuestionaire.objects.get(pk=self.questionaire)
		questions= Questions.objects.filter(questionaire=questionaire)
		for question in questions:
			#self.fields['custom_%s' % question.label] = forms.CharField(max_length=255) 
			self.fields['custom_%s' % question.label] = FIELD_TYPES[question.field_type]

	#this is going to get the questions from the database

	def get_questionaire(self):
		questionaire = LegalQuestionaire.objects.get(pk=self.questionsionaire)
		questions= Questions.objects.filter(questionaire=questionaire)
		return questions

class LegalTemplatesUploadForm(forms.Form):
	docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

class QuestionsFormNest(forms.Form):


	#this is going to pop out the questionaire id created in the view
	def __init__(self,*args,**kwargs):
		self.questionaire=kwargs.pop('questionaire')
		super(QuestionsForm,self).__init__(*args,**kwargs)
		
		#to create the nestable asset you need to create the three tags below.
		'''
		get the status of this part of the questionaire from some part of the models

		//this is going to have to the class name of the parent so that you can get the value from the div
		self.fields['parent_name'] 
		self.fields['parent_value'] the iterator value so that you can tie the form information to it.
		self.fields['child_name'] (this is going to default to nothing, "None" is probably the best option)
		self.fields['form_name'] (this is going to be the default name)
		//the form name and the parent name need to match.
		//these fields need to all be hidden and rendered in the template.
		'''
		#this creates the questions based on the questionaire number
		questionaire = LegalQuestionaire.objects.get(pk=self.questionaire)
		questions= Questions.objects.filter(questionaire=questionaire)
		for question in questions:
			#self.fields['custom_%s' % question.label] = forms.CharField(max_length=255) 
			self.fields['custom_%s' % question.label] = FIELD_TYPES[question.field_type]

	#this is going to get the questions from the database

	def get_questionaire(self):
		questionaire = LegalQuestionaire.objects.get(pk=self.questionsionaire)
		questions= Questions.objects.filter(questionaire=questionaire)
		return questions