**********************************************************************************************
********************* Tutorial: Django user account creation *********************************
**********************************************************************************************
# TODO : AR - proof-read
 
# In settings.py: write the name of your app, for example : 'dataviz' -> " '<name of your app>', " as the last line of the list "INSTALLED_APPS" at line 40.
# In <your project name>/urls.py create the empty url at the end of the list urlpatterns: path('', include('<your app name>.urls')). Add include to "from django.urls import path" -> "from django.urls import path,include"
# Create urls.py file in the app folder and copy the code about urls of the below tutorial (at the end of the tut's page):
  http://apprendre-python.com/page-django-login-authentification-de-base-apprendre-creer-cours-tutoriel-python
# Create "templates" folder in app folder; then create "front" and "backoffice" folders with an index.html file in each of them.
# In settings.py, in TEMPLATES = [], in 'DIRS':[]:, write -> os.path.join(BASE_DIR,'templates'), to indicate the template folder.
# Follow the rest of the previous tutorial: http://apprendre-python.com/page-django-login-authentification-de-base-apprendre-creer-cours-tutoriel-python

Follow the instructions above to fix the following seen problems:
# Seen problem: cannot import name 'patterns' -> retire patterns from imports in views.py
# Seen problem: No module named 'rest_framework' -> retire the line 'from rest_framework import routers' in <the app folder>/urls.py
# Seen problem: No module named 'erp' -> replace the line 'from erp.views import *' by from dataviz.views import *
# Seen problem: No module named 'eboutique' -> retire the line 'from eboutique.views import *'
# Seen problem: name 'patterns' is not defined -> replace 'urlpatterns = patterns('', <the url links> )' by 'urlpatterns = [ <the url links> ]'

# initialize the database (you need to be in the project folder) -> python manage.py migrate
# Create a super user (you need to be in the project folder) : python manage.py createsuperuser. Follow the instructions.
# You can create an other user that is not a super user by going into the django shell -> manage.py shell, from django.contrib.auth.models import User, then user=User.objects.create_user('user_name', password='user_password').
  and finally: user.save()
# To run the application (you need to be in your project folder) -> python manage.py runserver
# Go to web browser and go to 127.0.0.1:8000 and connect with superuser or user identifiers. And that's it.
# Additionally, go to 127.0.0.1:8000/admin and connect with superuser identifiers to open the administration interface and manage app data




***********************************************************************************************
********************* Tutorial: Git repository creation ***************************************
***********************************************************************************************

#make 'git init' in the directory of your project
#Write in a file .gitignore at project root: 
venv
.idea
*.sqlite3
#From the command line, enter cd <path_to_your_local_repo> so that you can enter commands for your repository.
#Enter git add <folder or file name> from your project directory. Add one by one the folders and file of your project directory.
#Enter git commit -am '<commit_message>' at the command line to commit ALL (thanks to -a ) new files/changes to the local repository. For the <commit_message> , you can enter anything that describes the changes you are committing.
#Enter git push  at the command line to copy your files from your local repository to Bitbucket.
#If prompted for authentication, enter your Bitbucket password.