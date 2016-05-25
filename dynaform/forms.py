from django import forms 

from .models import LegalQuestionaire,Questions

FIELD_TYPES={
	0:forms.CharField,
	1:forms.CharField,
	2:forms.BooleanField,
	3:forms.IntegerField,
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
			self.fields['%s' % question.question_name] = FIELD_TYPES[question.field_type](label=question.label)

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
		#pop the questionaire id
		self.questionaire=kwargs.pop('questionaire')
		if "parent" in kwargs:
			self.parent = kwargs.pop('parent')
		else:
			self.parent = "None"
		self.is_formset = kwargs.pop('is_formset')

		

		super(QuestionsFormNest,self).__init__(*args,**kwargs)

		#this creates the questions based on the questionaire number
		questionaire = LegalQuestionaire.objects.get(pk=self.questionaire)
		questions= Questions.objects.filter(questionaire=questionaire)
		for question in questions:
			self.fields['%s' % question.question_name] = FIELD_TYPES[question.field_type](label=question.label)
		
		#this creates some of the management of questions
		self.fields['is_deleted'] = forms.CharField(widget=forms.HiddenInput(),max_length=255,initial=str(False))
		self.fields['parent_name'] = forms.CharField(widget=forms.HiddenInput(),max_length=255,initial=self.parent)
		self.fields['parent_id'] = forms.IntegerField(widget=forms.HiddenInput(),initial=0)
		self.fields['form_name']= forms.CharField(widget=forms.HiddenInput(),max_length=255,initial=questionaire.name)		
		self.fields['form_id'] = forms.IntegerField(widget=forms.HiddenInput(),initial=0)
		self.fields['is_formset'] = forms.CharField(widget=forms.HiddenInput(),initial=str(self.is_formset))
		
	#this is going to get the questions from the database

	def get_questionaire(self):
		questionaire = LegalQuestionaire.objects.get(pk=self.questionsionaire)
		questions= Questions.objects.filter(questionaire=questionaire)
		return questions