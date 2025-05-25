from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from nlp import nlp_service

from io import BytesIO
# Create your views here.


@login_required
def dataset_generate(request):
    username = request.user.username
    
    template_name = "dictionary/dataset_generate.html"
    context = {}
    
    return render(request, template_name, context)