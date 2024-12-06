from django.shortcuts import render
from django.contrib import messages
from dashboard.models import Notes,HomeWork,Todo
from django.shortcuts import redirect
from django.views import generic
from dashboard.forms import Noteform,HomeworkForm,DashboardForm,Todoform,UserRegisterForm
from youtubesearchpython import VideosSearch
import wikipedia
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method == "POST":
        form=Noteform(request.POST)
        
        if form.is_valid():
            notes=Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully")
        
    else:
        form=Noteform()
    notes=Notes.objects.filter(user=request.user)
    return render(request,'dashboard/notes.html',{'notes':notes,'form':form})

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes

@login_required  
def homework(request):
    if request.method=='POST':
        form=HomeworkForm(request.POST)
        
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished =='on':
                    finished=True
                else:
                    finished=False
            except:
                finished =False
            homework= HomeWork(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            homework.save()
            messages.success(request,f"Homework Added from {request.user.username}!!")
    else:
        form=HomeworkForm()
    homework=HomeWork.objects.filter(user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
    return render(request,'dashboard/homework.html',{'homework':homework,'homework_done':homework_done,'form':form})

@login_required
def update_homework(request,pk=None):
    homework=HomeWork.objects.get(id=pk)
    if homework.is_finished==True:
        homework.is_finished=False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')
@login_required
def delete_homework(request,pk=None):
    HomeWork.objects.get(id=pk).delete()
    return redirect("homework")



def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            try:
                video_search = VideosSearch(text, limit=10)
                result_list = []
                for i in video_search.result()['result']:
                    result_dict = {
                        'input': text,
                        'title': i.get('title', 'No Title'),
                        'duration': i.get('duration', 'N/A'),
                        'thumbnails': i.get('thumbnails', [{'url': ''}])[0].get('url', ''),
                        'channel': i.get('channel', {}).get('name', 'No Channel'),
                        'link': i.get('link', '#'),
                        'views': i.get('viewCount', {}).get('short', '0 views'),
                        'published': i.get('publishedTime', 'Unknown'),
                    }
                    result_list.append(result_dict)
                context = {'form': form, 'results': result_list}
                return render(request, 'dashboard/youtube.html', context)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = DashboardForm()
    return render(request, 'dashboard/youtube.html', {'form': form})
@login_required
def todo(request):
    if request.method=='POST':
      form=Todoform(request.POST)
      if form.is_valid():
          try:
              finished=request.POST["is_finished"]
              if finished == 'on':
                  finished=True
              else:
                  finished=False
          except:
              finished=False
          todos=Todo(
               user=request.user,
               title=request.POST['title'],
               is_finished=finished
           )
          todos.save()
          messages.success(request,f"TODO Added from {request.user.username}!!")
    else:
        form=Todoform()
    todos=Todo.objects.filter(user=request.user)
    if len(todos)==0:
        todos_done=True
    else:
        todos_done=False
    # print(todos) 
    return render(request,'dashboard/todo.html',{'todo':todos,'form':form,'todos_done':todos_done})  

@login_required
def update_todo(request,pk=None):
    todo=Todo.objects.get(id=pk)
    if todo.is_finished==True:
        todo.is_finished=False
    else:
        todo.is_finished=True
    todo.save();
    return redirect('todo')

@login_required
def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')


def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            try:
                url = f"https://openlibrary.org/search.json?q={text}"
                r = requests.get(url)
                r.raise_for_status()  # Ensure the request was successful
                data = r.json()
                
                result_list = []
                for book in data.get('docs', [])[:10]:  # Limit results to 10
                    result_dict = {
                        'title': book.get('title', 'N/A'),
                        'subtitle': book.get('subtitle', 'N/A'),
                        'author': ', '.join(book.get('author_name', [])),
                        'first_publish_year': book.get('first_publish_year', 'N/A'),
                        'cover': f"https://covers.openlibrary.org/b/id/{book.get('cover_i', '')}-M.jpg" if book.get('cover_i') else None,
                        'categories': book.get('subject', []),  # Assuming 'subject' holds category data
                        'preview': f"https://openlibrary.org{book.get('key', '')}/preview",
                    }
                    result_list.append(result_dict)
                
                context = {'form': form, 'results': result_list}
                return render(request, 'dashboard/books.html', context)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = DashboardForm()

    return render(request, 'dashboard/books.html', {'form': form})


def dictionary(request):
    definition_data = None  # Default to None
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            word = form.cleaned_data['text']  # Assuming the form field is named 'text'
            
            # Use the Free Dictionary API to fetch word details
            try:
                url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                response = requests.get(url)
                response.raise_for_status()  # Raise an error for invalid responses
                
                data = response.json()
                # Extract relevant data
                word_data = data[0] if isinstance(data, list) else {}
                phonetics = word_data.get('phonetics', [])
                definition = word_data.get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', 'No definition available')
                example = word_data.get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', 'No example available')
                synonyms = word_data.get('meanings', [{}])[0].get('synonyms', [])

                definition_data = {
                    'word': word,
                    'phonetics': phonetics,
                    'definition': definition,
                    'example': example,
                    'synonyms': synonyms,
                }

            except Exception as e:
                definition_data = {'error': str(e)}

    else:
        form = DashboardForm()

    return render(request, 'dashboard/dictionary.html', {'form': form, 'definition_data': definition_data})

def wiki(request):
    if request.method=='POST':
        text=request.POST['text']
        form = DashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:
      form=DashboardForm()
    return render(request,'dashboard/wiki.html',{'form':form})

def about(request):
    return render(request,'dashboard/conversion.html')

def register(request):
    if request.method=='POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid:
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"you are login as username {username} !!")
            return redirect("login")
    else:
        form=UserRegisterForm()
    return render(request,'dashboard/register.html',{'form':form})

@login_required
def profile(request):
    homework=HomeWork.objects.filter(is_finished=False,user=request.user)
    todo=Todo.objects.filter(is_finished=False,user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
    
    if len(todo) ==0:
        todo_done=True
    else:
        todo_done=False
    context={
        'homework':homework,
        'homework_done':homework_done,
        'todo':todo,
        'todo_done':todo_done,
    }
    return render(request,'dashboard/profile.html',context)
@login_required
def user_logout(request):
    logout(request)
    return render(request,'dashboard/logout.html')