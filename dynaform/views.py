from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.views.generic import View
from django.http import Http404
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from models import LegalQuestionaire,Questions,LegalTemplates
from forms import QuestionsForm,LegalTemplatesUploadForm, QuestionsFormNest

# Create your views here.

class HomeView(ListView):
	template_name = 'base.html'
	queryset = LegalQuestionaire.objects.all()



def multi_formset_view(request,lq_id):
	#a nested 
	try:
		p = LegalQuestionaire.objects.get(pk=lq_id)
		form = QuestionsFormNest(request.POST,questionaire=lq_id)
		QuestionsFormset = formset_factory(QuestionsFormNest)
		print "\n\n\n\n\n"
		print "POST QUERY DICT"
		print request.POST
		if request.method == 'POST':
			formset = QuestionsFormset(request.POST,form_kwargs={'questionaire':lq_id})
			if formset.is_valid():
				print "\n\n\n\n\n"
				print "FORMSET DATA"
				print formset.cleaned_data
				
				for form in formset:
					print "\n\n"
					print "FORM Data "
					print(form.cleaned_data)
			else:
				print "it didn'st work"
		else:
			formset = QuestionsFormset(form_kwargs={'questionaire':lq_id})
			print "nothing"
		return render(request, 'dynaform/questionaire_v1.html', {'formset': formset})

	except LegalQuestionaire.DoesNotExist:
		raise Http404("LegalQuestionaire does not exist")	
	return render(request, 'dynaform/questionaire_v1.html', {'formset': formset})



def formset_view(request,lq_id):
	#this creates formsets and posts it. This is a simple example.
	try:
		p = LegalQuestionaire.objects.get(pk=lq_id)
		form = QuestionsForm(request.POST,questionaire=lq_id)
		QuestionsFormset = formset_factory(QuestionsForm)
		print "\n\n\n\n\n"
		print "POST QUERY DICT"
		print request.POST
		if request.method == 'POST':
			formset = QuestionsFormset(request.POST,form_kwargs={'questionaire':lq_id})
			

			if formset.is_valid():
				
				print "\n\n\n\n\n"
				print "FORMSET DATA"
				print formset.cleaned_data
				
				for form in formset:
					print "\n\n"
					print "FORM Data "
					print(form.cleaned_data)
			else:
				print "it didn'st work"
		else:
			formset = QuestionsFormset(form_kwargs={'questionaire':lq_id})
			print "nothing"
		return render(request, 'dynaform/questionaire_v1.html', {'formset': formset})

	except LegalQuestionaire.DoesNotExist:
		raise Http404("LegalQuestionaire does not exist")	
	return render(request, 'dynaform/questionaire_v1.html', {'formset': formset})




def questionaire_view(request,lq_id):
	try:
		p = LegalQuestionaire.objects.get(pk=lq_id)
		form = QuestionsForm(request.POST,questionaire=lq_id)
		form2 = QuestionsForm(request.POST,questionaire=lq_id)
		sub_form = QuestionsForm(request.POST,questionaire=2)
		


		if request.method =='POST':
			print "DUMP CLEAN OF REQUEST"
			print request.POST
			#dumpclean(request.POST)
			#print "\n\n\n\n\n"
			#print form.getlist('custom_why would you use linux')
			print "\n\n\n\n\n"
				
			if form.is_valid():
				print "DUMP CLEAN OF FORM DATA"
				print form.cleaned_data
				#dumpclean(form.cleaned_data)
				return HttpResponseRedirect('/')
			else:
				print form.errors
		else:
			form = QuestionsForm(questionaire=lq_id)
			return render(request, 'dynaform/questionaire.html', {'form': form})

	except LegalQuestionaire.DoesNotExist:
		raise Http404("LegalQuestionaire does not exist")	
	return render(request, 'dynaform/questionaire.html', {'LegalQuestionaire': p})

def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dumpclean(v)
            else:
                print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v
    else:
        print obj

def legal_template_upload_view(request):
	if request.method == 'POST':
		form = LegalTemplatesUploadForm(request.POST, request.FILES)
		if form.is_valid():
			newdoc = LegalTemplates(docfile = request.FILES['docfile'])
			newdoc.save()

			# Redirect to the document list after POST
			return HttpResponseRedirect(reverse('/'))
	else:
		form = LegalTemplatesUploadForm() # A empty, unbound form
	# Load documents for the list page
	documents = LegalTemplates.objects.all()
	
    # Render list page with the documents and the form context_instance=RequestContext(request)
	return render(
		request,'dynaform/legal_template_form.html',{'documents': documents, 'form': form},
	)

'''
class QuestionaireView(CreateView):
	template_name = 'dynaform/questionaire.html'
	form_class = QuestionsForm
		
	success_url='/'

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.
		#form.send_email()
		return super(QuestionaireView, self).form_valid(form)


	def get_context_data(self,**kwargs):
		d = super(QuestionaireView,self).get_context_data(**kwargs)
		d['questionaire']= self.get_object()
		return d

	def get_form_kwargs(self):
		kwargs = super(QuestionaireView,self).get_form_kwargs()
		kwargs['questionaire'] = self.get_object()
		return kwargs
'''
