from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.views.generic import View
from django.http import Http404
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.core.files import File

from models import LegalQuestionaire,Questions,LegalTemplates
from models import FormBaseLevel, FormLevelOne, FormLevelTwo,FormLevelThree
from models import LegalTemplates, LegalDocuments
from forms import QuestionsForm,LegalTemplatesUploadForm, QuestionsFormNest
import json
import datetime
# Create your views here.
from docxtpl import DocxTemplate

from django.conf import settings



class HomeView(ListView):
	template_name = 'base.html'
	queryset = LegalQuestionaire.objects.all()

def docx_download_page(request,slug,uuid):
	try: 
		doc= LegalDocuments.objects.get(slug=slug,unique_id=uuid)
		
		file_name =  str(doc.filename())
		print file_name
		return render(request, 'dynaform/file.html', {'filename':file_name})

	except LegalDocuments.DoesNotExist:
		raise Http404("Legal document does not exist")	

	return render(request, 'dynaform/file.html', {'filename':file_name})





def form_to_docx(request,slug):

	#an attempt at nested formsets

	formset_list =[]
	try:
		#create the base formset that everything is based off of.
		QuestionsFormset = formset_factory(QuestionsFormNest)

		#get the questionaire list from the group
		questionaire_list = FormBaseLevel.objects.filter(slug=slug)

		#get the template
		template_file = LegalTemplates.objects.filter(slug=slug)

		
		formset_list =[]
		formset_dict = {}
		#create the formsets to access the cleaned data
		if request.method=='POST':
			
			for questionaire in questionaire_list:
				formset_dict['name'] = questionaire.form.name
				formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.form.id,'is_formset':questionaire.is_formset},prefix=questionaire.form.name)  
				formset_dict['parent'] = "None"
				formset_dict['is_formset'] = questionaire.is_formset
				if questionaire.child is not None:
					formset_dict['child'] = str(questionaire.child.form.name)
				else:
					formset_dict['child'] = str(None)
				
				formset_dict['level'] = 0
				
				formset_list.append(formset_dict.copy())
				#set the parent for the child
				parent = questionaire.form.name
				if questionaire.child is not None:
					
					formset_dict['name'] = questionaire.child.form.name
					formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.child.form.id,'parent':parent,'is_formset':questionaire.child.is_formset},prefix=questionaire.child.form.name)
					formset_dict['parent'] = parent 

					formset_dict['is_formset'] = questionaire.child.is_formset
					if questionaire.child.child is not None:
						formset_dict['child'] = str(questionaire.child.child.form.name)
					else:
						formset_dict['child'] = str(None)
					formset_dict['level'] = 1

					parent = questionaire.child.form.name
					formset_list.append(formset_dict.copy())
						
					#this is the child of the child.
					if questionaire.child.child is not None:
					
						formset_dict['name'] = questionaire.child.child.form.name
						formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.is_formset},prefix=questionaire.child.child.form.name) 
						formset_dict['parent'] = parent
						formset_dict['is_formset'] = questionaire.child.child.is_formset
					
						if questionaire.child.child.child is not None:
							formset_dict['child'] = str(questionaire.child.child.child.form.name)
						else:
							formset_dict['child'] = str(None)
						
						formset_dict['level'] = 2
							
						#set for the next level down.
						parent = questionaire.child.child.form.name
						level = formset_dict['level']

						formset_list.append(formset_dict.copy())			
						#this is the child of the child.
						if questionaire.child.child.child is not None:
						
							formset_dict['name'] = questionaire.child.child.child.form.name
							formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.child.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.child.is_formset},prefix=questionaire.child.child.child.form.name) 
							formset_dict['parent'] = parent
							formset_dict['is_formset'] = questionaire.child.child.child.is_formset
					
							if questionaire.child.child.child is not None:
								formset_dict['child'] = str(questionaire.child.child.child.form.name)
							else:
								formset_dict['child'] = str(None)
							
							formset_dict['level'] = 3
								
							#set for the next level down.
							parent = questionaire.child.child.child.form.name
							level = formset_dict['level']

							formset_list.append(formset_dict.copy())			
					
			#print the clean data to a dict
			cleaned_data = []				
			if_errors = False
			print json.dumps(formset_list[0]['data'].data,sort_keys=True, indent=4)
			for formset in formset_list:
				print ""
				print "check for formset" +str(formset['name'])
				
				#print json.dumps(formset['data'].data,sort_keys=True, indent=4)
				if formset['data'].is_valid():
					print formset['data'].cleaned_data
					cleaned_data = cleaned_data + formset['data'].cleaned_data
					
				else:
					print formset['data'].errors
					if_errors = True
			
			#print "thisis the cleaned data"
			#print the cleaned data out
			print json.dumps(cleaned_data,sort_keys=True, indent=4)
			



			if if_errors ==False:		
				#This can be done in another function
				counter = 0
				length = len(cleaned_data)
				while counter<length:

					data = cleaned_data[counter]

					if data['parent_name']!="None":

						for append_data in cleaned_data:

							cleaned_data,length,counter = format_form_data(append_data,cleaned_data,counter,length)		
					
					else:
						counter = counter + 1

				print cleaned_data
							
				'''
				if data['parent_name']!="None":
					
					for append_data in cleaned_data:
						
						if data['parent_name'] == append_data['form_name'] and data['parent_id'] == append_data['form_id']:
							append_data['child'] =data['form_name']
							if data['is_formset'] =="True":
								if data['form_name'] not in append_data:
									append_data[data['form_name']] = [] 
								append_data[data['form_name']].append(data)
							else:
								append_data[data['form_name']] = data
							
							#append_data[data['form_name']] = data
							del cleaned_data[i]
							break
							
						elif 'child' in append_data:
							child1 = append_data['child']
							if isinstance(append_data[child1],list):
								print child1 + " is a list"
								
								for child_data in append_data[child1]:

									if data['parent_name'] == child_data['form_name'] and data['parent_id'] == child_data['form_id']:			
										child_data['child'] =data['form_name']
										if data['is_formset'] =="True":
											if data['form_name'] not in child_data:
												child_data[data['form_name']] = [] 
											child_data[data['form_name']].append(data)
										else:
											child_data[data['form_name']] = data
										
										del cleaned_data[i]
										break
									elif 'child' in child_data:
										child2 = child_data['child']
										if isinstance(child_data[child2],list):
											print child2 + " is a list"
											for child_data_1 in child_data[child2]:
											
												if data['parent_name'] == child_data_1['form_name'] and data['parent_id'] == child_data_1['form_id']:
													
													child_data_1['child'] =data['form_name']
													if data['is_formset'] =="True":
														if data['form_name'] not in child_data_1:
															child_data_1[data['form_name']] = [] 
														child_data_1[data['form_name']].append(data)
													else:
														child_data_1[data['form_name']] = data
													
													del cleaned_data[i]
													break
												elif 'child' in child_data_1:
													child3 = child_data_1['child']
													if isinstance(child_data_1[child3],list):
														print child3 + " is a list"
														for child_data_2 in child_data_1[child3]:
														
															if data['parent_name'] == child_data_2['form_name'] and data['parent_id'] == child_data_1['form_id']:
																
																child_data_2['child'] =data['form_name']
																if data['is_formset'] =="True":
																	if data['form_name'] not in child_data_2:
																		child_data_2[data['form_name']] = [] 
																	child_data_2[data['form_name']].append(data)
																else:
																	child_data_2[data['form_name']] = data
																
																del cleaned_data[i]
																break
													elif isinstance(child_data[child2],dict):
														if data['parent_name'] == child_data_1[child3]['form_name'] and data['parent_id'] == append_data[child1]['form_id']:
															#print "match!" + child1
															child_data_1[child3][data['form_name']] = data	
															child_data_1[child3]['child'] = data['form_name']
															
															del cleaned_data[i]
															break	
										elif isinstance(child_data[child2],dict):
											if data['parent_name'] == append_data[child1]['form_name'] and data['parent_id'] == append_data[child1]['form_id']:
												#print "match!" + child1
												child_data[child2][data['form_name']] = data	
												child_data[child2]['child'] = data['form_name']
												
												del cleaned_data[i]
												break	
																						


							elif isinstance(append_data[child1],dict):
								print child1 +" is a dict"

								if data['parent_name'] == append_data[child1]['form_name'] and data['parent_id'] == append_data[child1]['form_id']:
									#print "match!" + child1
									append_data[child1][data['form_name']] = data	
									append_data[child1]['child'] = data['form_name']
									if data['is_formset'] =="True":
										if data['form_name'] not in append_data[child1]:
											append_data[child1][data['form_name']] = [] 
										append_data[child1][data['form_name']].append(data)
									else:
										append_data[child1][data['form_name']] = data
										
									del cleaned_data[i]
									break
								


								elif 'child' in append_data[child1]:
									child2 = append_data[child1]['child']
									#print "match!" + child1 +" "+  child2
									
									if data['parent_name'] == append_data[child1][child2]['form_name'] and data['parent_id'] == append_data[child1][child2]['form_id']:
										#print "match!"
										append_data[child1][child2][data['form_name']] = data
										append_data[child1][child2]['child'] = data['form_name']
										del cleaned_data[i]
										break
									
									elif 'child' in append_data[child1][child2]['child']:
										child3 = append_data[child1][child2]['child']
										
										if data['parent_name'] == append_data[child1][child2][child3]['form_name'] and data['parent_id'] == append_data[child1][child2][child3]['form_id']:
											#print "match!"
											append_data[child1][child2][child3][data['form_name']] = data
											del cleaned_data[i]
											break									
										
									break
					'''	
					
				

				#create the new file
				
				#f = open('/path/to/file')
				#self.license_file.save(new_name, File(f))
				
				#this actually works do keep this
				print cleaned_data[0]
				print 'MEDIA ROOT'
				print settings.MEDIA_ROOT 
				print 'Templates'
				file_name = settings.MEDIA_ROOT+'/'+str(template_file[0].docfile)
				template = DocxTemplate(file_name)
				template.render(cleaned_data[0])
				end_file_name = 'daneltest-'+ str( datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))+'.docx'
				end_file = settings.MEDIA_ROOT+'/'+end_file_name
				template.save(end_file)
				

				#this is going to create the file
				savefile = open(end_file)
				doc = LegalDocuments(docfile = File(savefile),group=slug)
				doc.save()

				print "unique id " + str(doc.unique_id)
				print "group " + str(doc.group)

				return HttpResponseRedirect('/form-to-docx/file/'+str(doc.group)+'/'+str(doc.unique_id) )	


			#print the cleaned data out
			print json.dumps(cleaned_data,sort_keys=True, indent=4)
			
		else:
			#set the current level for the template so that wen you nest you can compare them
			level = 0

			#loop through the form list and add the info to render the nested templates
			for questionaire in questionaire_list:
				formset_dict['name'] = questionaire.form.name
				formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.form.id,'is_formset':questionaire.is_formset},prefix=questionaire.form.name)
				formset_dict['parent'] = "None"
				formset_dict['is_formset'] = questionaire.is_formset
					
				if questionaire.child is not None:
					formset_dict['child'] = str(questionaire.child.form.name)
				else:
					formset_dict['child'] = str(None)
				#set the level so that you can you can compare
				formset_dict['level'] = 0
				formset_dict['prev_level'] = level
				formset_list.append(formset_dict.copy())
				#set the parent and the 
				parent = questionaire.form.name
				level = formset_dict['level']
				print formset_dict

				if questionaire.child is not None:
					
					formset_dict['name'] = questionaire.child.form.name
					formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.child.form.id,'parent':parent,'is_formset':questionaire.child.is_formset},prefix=questionaire.child.form.name) 
					formset_dict['parent'] = parent
					formset_dict['is_formset'] = questionaire.child.is_formset
					
					if questionaire.child.child is not None:
						formset_dict['child'] = str(questionaire.child.child.form.name)
					else:
						formset_dict['child'] = str(None)
					
					formset_dict['level'] = 1
					formset_dict['prev_level'] = 0
						
					#set for the next level down.
					parent = questionaire.child.form.name
					#level = formset_dict['level']
					print formset_dict

					formset_list.append(formset_dict.copy())			


					#this is the child of the child.
					if questionaire.child.child is not None:
					
						formset_dict['name'] = questionaire.child.child.form.name
						formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.is_formset},prefix=questionaire.child.child.form.name) 
						formset_dict['parent'] = parent
						formset_dict['is_formset'] = questionaire.child.child.is_formset
					
						if questionaire.child.child.child is not None:
							formset_dict['child'] = str(questionaire.child.child.child.form.name)
						else:
							formset_dict['child'] = str(None)
						
						formset_dict['level'] = 2
						formset_dict['prev_level'] = 1
										
						#set for the next level down.
						parent = questionaire.child.child.form.name
						level = formset_dict['level']
						print formset_dict
						formset_list.append(formset_dict.copy())
						
						#this is the child of the child.
						if questionaire.child.child.child is not None:
						
							formset_dict['name'] = questionaire.child.child.child.form.name
							formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.child.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.child.is_formset},prefix=questionaire.child.child.child.form.name) 
							formset_dict['parent'] = parent
							formset_dict['is_formset'] = questionaire.child.child.child.is_formset
					
							'''
							if questionaire.child.child.child is not None:
								formset_dict['child'] = str(questionaire.child.child.child.form.name)
							else:
								formset_dict['child'] = str(None)
							'''
							#this is the last level of nesting that needs to be done.
							formset_dict['child'] = str(None)
							formset_dict['prev_level'] = 2
						
							formset_dict['level'] = 3
								
							#set for the next level down.
							parent = questionaire.child.child.child.form.name
							level = formset_dict['level']
							print formset_dict

							formset_list.append(formset_dict.copy())

		return render(request, 'dynaform/questionaire_v4.html', {'formsets': formset_list})

	except LegalQuestionaire.DoesNotExist:
		raise Http404("LegalQuestionaire does not exist")	
	return render(request, 'dynaform/questionaire_v4.html', {'formsets': formset_list})


#this is going to format the formdata into cleaned data
def format_form_data(append_data,cleaned_data,counter,length):

	data = cleaned_data[counter]

	if isinstance(append_data,list):
		for child_data in append_data:
			#print child_data['form_name'] + " " + child_data['form_id']
			if data['parent_name'] == child_data['form_name'] and data['parent_id'] == child_data['form_id']:
				child_data['child'] =data['form_name']
				if data['is_formset'] =="True":
					if data['form_name'] not in child_data:
						child_data[data['form_name']] = [] 
					child_data[data['form_name']].append(data)
				else:
					child_data[data['form_name']] = data
				
				#append_data[data['form_name']] = data
				del cleaned_data[counter]
				length = length - 1
				break
			elif 'child' in child_data:
				child = child_data['child']
				cleaned_data,length,counter = format_form_data(child_data[child],cleaned_data,counter,length)
							
	elif isinstance(append_data,dict):
		#print append_data['form_name'] + " " + str(append_data['form_id'])
		if data['parent_name'] == append_data['form_name'] and data['parent_id'] == append_data['form_id']:
			append_data['child'] =data['form_name']
			if data['is_formset'] =="True":
				if data['form_name'] not in append_data:
					append_data[data['form_name']] = [] 
				append_data[data['form_name']].append(data)
			else:
				append_data[data['form_name']] = data
			
			#append_data[data['form_name']] = data
			del cleaned_data[counter]
			length = length -1 

		elif 'child' in append_data:
			child = append_data['child']
			cleaned_data,length,counter = format_form_data(append_data[child],cleaned_data,counter,length)
				
	return cleaned_data,length,counter


def multi_formset_view(request,slug):

	#an attempt at nested formsets

	formset_list =[]
	try:
		#create the base formset that everything is based off of.
		QuestionsFormset = formset_factory(QuestionsFormNest)

		#get the questionaire list from the group
		questionaire_list = FormBaseLevel.objects.filter(slug=slug)

		
		formset_list =[]
		formset_dict = {}
		#create the formsets to access the cleaned data
		if request.method=='POST':
			
			for questionaire in questionaire_list:
				formset_dict['name'] = questionaire.form.name
				formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.form.id,'is_formset':questionaire.is_formset},prefix=questionaire.form.name)  
				formset_dict['parent'] = "None"
				formset_dict['is_formset'] = questionaire.is_formset
				if questionaire.child is not None:
					formset_dict['child'] = str(questionaire.child.form.name)
				else:
					formset_dict['child'] = str(None)
				
				formset_dict['level'] = 0
				
				formset_list.append(formset_dict.copy())
				#set the parent for the child
				parent = questionaire.form.name
				if questionaire.child is not None:
					
					formset_dict['name'] = questionaire.child.form.name
					formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.child.form.id,'parent':parent,'is_formset':questionaire.child.is_formset},prefix=questionaire.child.form.name)
					formset_dict['parent'] = parent 

					formset_dict['is_formset'] = questionaire.child.is_formset
					if questionaire.child.child is not None:
						formset_dict['child'] = str(questionaire.child.child.form.name)
					else:
						formset_dict['child'] = str(None)
					formset_dict['level'] = 1

					parent = questionaire.child.form.name
					formset_list.append(formset_dict.copy())
						
					#this is the child of the child.
					if questionaire.child.child is not None:
					
						formset_dict['name'] = questionaire.child.child.form.name
						formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.is_formset},prefix=questionaire.child.child.form.name) 
						formset_dict['parent'] = parent
						formset_dict['is_formset'] = questionaire.child.child.is_formset
					
						if questionaire.child.child.child is not None:
							formset_dict['child'] = str(questionaire.child.child.child.form.name)
						else:
							formset_dict['child'] = str(None)
						
						formset_dict['level'] = 2
							
						#set for the next level down.
						parent = questionaire.child.child.form.name
						level = formset_dict['level']

						formset_list.append(formset_dict.copy())			
						#this is the child of the child.
						if questionaire.child.child.child is not None:
						
							formset_dict['name'] = questionaire.child.child.child.form.name
							formset_dict['data'] = QuestionsFormset(request.POST,form_kwargs={'questionaire':questionaire.child.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.child.is_formset},prefix=questionaire.child.child.child.form.name) 
							formset_dict['parent'] = parent
							formset_dict['is_formset'] = questionaire.child.child.child.is_formset
					
							if questionaire.child.child.child is not None:
								formset_dict['child'] = str(questionaire.child.child.child.form.name)
							else:
								formset_dict['child'] = str(None)
							
							formset_dict['level'] = 3
								
							#set for the next level down.
							parent = questionaire.child.child.child.form.name
							level = formset_dict['level']

							formset_list.append(formset_dict.copy())			
					
			#print the clean data to a dict
			cleaned_data = []				
			for formset in formset_list:
				print "check for formset" +str(formset['name'])
				if formset['data'].is_valid():
					
					cleaned_data = cleaned_data + formset['data'].cleaned_data
				else:
					print formset['data'].errors
					
			print "\n\n\n"
			print "bring back together"	
			#This can be done in another function
			i = 0
			length = len(cleaned_data)
			while i<length:
				data = cleaned_data[i]
				print data['parent_name']
				if data['parent_name']!="None":
					for append_data in cleaned_data:
						
						if data['parent_name'] == append_data['form_name'] and data['parent_id'] == append_data['form_id']:
							#print "match!"
							print data['form_name']				
							append_data[data['form_name']] = data
							append_data['child'] =data['form_name']
							
							del cleaned_data[i]
							break
							
						elif 'child' in append_data:
							child1 = append_data['child']
							
							if data['parent_name'] == append_data[child1]['form_name'] and data['parent_id'] == append_data[child1]['form_id']:
								#print "match!" + child1
								append_data[child1][data['form_name']] = data	
								append_data[child1]['child'] = data['form_name']
								
								del cleaned_data[i]
							elif 'child' in append_data[child1]:
								child2 = append_data[child1]['child']
								#print "match!" + child1 +" "+  child2
								
								if data['parent_name'] == append_data[child1][child2]['form_name'] and data['parent_id'] == append_data[child1][child2]['form_id']:
									#print "match!"
									append_data[child1][child2][data['form_name']] = data
									append_data[child1][child2]['child'] = data['form_name']
									del cleaned_data[i]
									break
								
								elif 'child' in append_data[child1][child2]['child']:
									child3 = append_data[child1][child2]['child']
									
									if data['parent_name'] == append_data[child1][child2][child3]['form_name'] and data['parent_id'] == append_data[child1][child2][child3]['form_id']:
										#print "match!"
										append_data[child1][child2][child3][data['form_name']] = data
										del cleaned_data[i]
										break									
									
								break
					length = length - 1
				else:
					i = i + 1

			


			#print the cleaned data out
			print json.dumps(cleaned_data,sort_keys=True, indent=4)
			
		else:
			#set the current level for the template so that wen you nest you can compare them
			level = 0

			#loop through the form list and add the info to render the nested templates
			for questionaire in questionaire_list:
				formset_dict['name'] = questionaire.form.name
				formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.form.id,'is_formset':questionaire.is_formset},prefix=questionaire.form.name)
				formset_dict['parent'] = "None"
				formset_dict['is_formset'] = questionaire.is_formset
					
				if questionaire.child is not None:
					formset_dict['child'] = str(questionaire.child.form.name)
				else:
					formset_dict['child'] = str(None)
				#set the level so that you can you can compare
				formset_dict['level'] = 0
				formset_dict['prev_level'] = level
				formset_list.append(formset_dict.copy())
				#set the parent and the 
				parent = questionaire.form.name
				level = formset_dict['level']
				print formset_dict

				if questionaire.child is not None:
					
					formset_dict['name'] = questionaire.child.form.name
					formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.child.form.id,'parent':parent,'is_formset':questionaire.child.is_formset},prefix=questionaire.child.form.name) 
					formset_dict['parent'] = parent
					formset_dict['is_formset'] = questionaire.child.is_formset
					
					if questionaire.child.child is not None:
						formset_dict['child'] = str(questionaire.child.child.form.name)
					else:
						formset_dict['child'] = str(None)
					
					formset_dict['level'] = 1
					formset_dict['prev_level'] = 0
						
					#set for the next level down.
					parent = questionaire.child.form.name
					#level = formset_dict['level']
					print formset_dict

					formset_list.append(formset_dict.copy())			


					#this is the child of the child.
					if questionaire.child.child is not None:
					
						formset_dict['name'] = questionaire.child.child.form.name
						formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.is_formset},prefix=questionaire.child.child.form.name) 
						formset_dict['parent'] = parent
						formset_dict['is_formset'] = questionaire.child.child.is_formset
					
						if questionaire.child.child.child is not None:
							formset_dict['child'] = str(questionaire.child.child.child.form.name)
						else:
							formset_dict['child'] = str(None)
						
						formset_dict['level'] = 2
						formset_dict['prev_level'] = 1
										
						#set for the next level down.
						parent = questionaire.child.child.form.name
						level = formset_dict['level']
						print formset_dict
						formset_list.append(formset_dict.copy())
						
						#this is the child of the child.
						if questionaire.child.child.child is not None:
						
							formset_dict['name'] = questionaire.child.child.child.form.name
							formset_dict['data'] = QuestionsFormset(form_kwargs={'questionaire':questionaire.child.child.child.form.id,'parent':parent,'is_formset':questionaire.child.child.child.is_formset},prefix=questionaire.child.child.child.form.name) 
							formset_dict['parent'] = parent
							formset_dict['is_formset'] = questionaire.child.child.child.is_formset
					
							'''
							if questionaire.child.child.child is not None:
								formset_dict['child'] = str(questionaire.child.child.child.form.name)
							else:
								formset_dict['child'] = str(None)
							'''
							#this is the last level of nesting that needs to be done.
							formset_dict['child'] = str(None)
							formset_dict['prev_level'] = 2
						
							formset_dict['level'] = 3
								
							#set for the next level down.
							parent = questionaire.child.child.child.form.name
							level = formset_dict['level']
							print formset_dict

							formset_list.append(formset_dict.copy())

		return render(request, 'dynaform/questionaire_v3.html', {'formsets': formset_list})

	except LegalQuestionaire.DoesNotExist:
		raise Http404("LegalQuestionaire does not exist")	
	return render(request, 'dynaform/questionaire_v3.html', {'formsets': formset_list})

def formset_view(request,lq_id):
	#this creates formsets and posts it. This is a simple example.
	try:
		p = LegalQuestionaire.objects.get(pk=lq_id)
		form = QuestionsFormNest(request.POST,questionaire=lq_id)
		QuestionsFormset = formset_factory(QuestionsFormNest)
		print "\n\n\n\n\n"
		print "POST QUERY DICT"
		print request.POST
		if request.method == 'POST':
			formset = QuestionsFormset(request.POST,form_kwargs={'questionaire':lq_id},prefix='books')
			if formset.is_valid():
				print "\n\n\n\n\n"
				print "FORMSET DATA"
				print formset.cleaned_data
				
				for form in formset:
					print ""
					#print "FORM Data "
					#print(form.cleaned_data)
			else:
				print "it didn'st work"
		else:
			formset = QuestionsFormset(form_kwargs={'questionaire':lq_id},prefix='books')
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
