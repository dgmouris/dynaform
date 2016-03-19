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
		
		#questions = self.get_questionaire()

		questionaire = LegalQuestionaire.objects.get(pk=self.questionaire)
		questions= Questions.objects.filter(questionaire=questionaire)
		print questions
		for question in questions:
			print question.label + " " + str(question.field_type)

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