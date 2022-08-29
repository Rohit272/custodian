from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from .models import Policy

import os
import mimetypes
import datetime
import subprocess
import logging
import yaml
import c7n_azure
from c7n.commands import run
from c7n.config import Config



# Create your views here.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)
def index(request):
    #policy = Policy.objects.all().values()
    policy = Policy.objects.raw('SELECT * FROM policy_policy where is_active=1')
    template = loader.get_template('index.html')
    context = {
        'policy': policy,
    }
    return HttpResponse(template.render(context, request))

def create(request):
    template = loader.get_template('create.html')
    return HttpResponse(template.render({}, request))

def upload_file(request):
    myfile = request.FILES['myfile']
    fs = FileSystemStorage()
    filepath = THIS_DIR+'/yaml/azure/'+myfile.name
    if os.path.exists(filepath):
        os.remove(filepath)
    filename = fs.save(filepath, myfile)
    return '/yaml/azure/' + myfile.name

def addrecord(request):
    if request.method == 'POST' and request.FILES['myfile']:
        filepath = upload_file(request)
    policy = Policy(name=request.POST['name'], subscription_id=request.POST['subscription_id'],description=request.POST['description'], file_path=filepath)
    policy.save()
    return HttpResponseRedirect(reverse('index'))

def set_subscription(subscription_id):
    cmd = "az account set -s "+subscription_id
    returned_value = os.system(cmd)
    return returned_value;

def delete(request, id):
    policy = Policy.objects.get(id=id)
    policy.delete()
    return HttpResponseRedirect(reverse('index'))

def update(request, id):
    policy = Policy.objects.get(id=id)
    template = loader.get_template('update.html')
    context = {
        'policy': policy,
    }
    return HttpResponse(template.render(context, request))
def updaterecord(request, id):
    policy = Policy.objects.get(id=id)
    policy.subscription_id = request.POST['subscription_id']
    policy.description = request.POST['description']
    policy.save()
    return HttpResponseRedirect(reverse('index'))

def execute_policy(request, subscription, policyname):

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    policy = Policy.objects.raw("SELECT * FROM policy_policy where is_active=1 and subscription_id='"+subscription+"' and name= '"+policyname+"' LIMIT 1 ")
    if len(policy) == 0 :
        return HttpResponse("No record found, subscription id or policy name not valid",  status=404)

    result = set_subscription(policy[0].subscription_id)
    ymlfile = THIS_DIR+policy[0].file_path
    logger.info('-----------------Ploicy Ececution Started------------------------')
    THIS_DIR=os.path.dirname(os.path.abspath(__file__))
    logger.info(ymlfile)
    OUT_DIR = THIS_DIR+'/output/'+policy[0].subscription_id
    #assumed_role = 'arn:aws:iam::749812993810:role/cloudcustodian_role'
    filename= THIS_DIR+policy[0].file_path
    default_c7n_config = {
        'skip-validation': True,
        'vars': None,
        'debug': True,
        #'assume': assumed_role,
        'output_dir': OUT_DIR,
        'region': 'us-east-1',
        'configs': [filename]
    }
    run_config = Config.empty(**default_c7n_config)
    logger.info('Running policy: '+filename)
    try:
        rsl = run(run_config)
        resp = output_view(request, policy[0].subscription_id, policy[0].name, 'resources.json')
    except:
        return HttpResponse("Exception occurred while executing policy.",  status=500)


    return HttpResponse(resp)

def output_dir(request, id):
    policy = Policy.objects.get(id=id)
    dir_path = THIS_DIR + '/output/'+policy.subscription_id
    res = []
    # Iterate directory
    for path in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, path)):
            res.append(path)

    template = loader.get_template('output_dir.html')
    context = {
        'subscription_id': policy.subscription_id,
        'directory': res,
    }
    return HttpResponse(template.render(context, request))

def output_files(request, subscription, directory):
    dir_path = THIS_DIR + '/output/'+subscription+'/'+directory
    files = []

    for filename in os.listdir(dir_path):
        file = os.path.join(dir_path, filename)
        if os.path.isfile(file):
            c_time = os.path.getctime(file)
            m_time = os.path.getmtime(file)
            files.append({"name": filename, "created_datetime":datetime.datetime.fromtimestamp(c_time), "modified_datetime":datetime.datetime.fromtimestamp(m_time)})

    template = loader.get_template('output_files.html')
    context = {
        'policy': directory,
        'subscription': subscription,
        'files': files,
    }
    return HttpResponse(template.render(context, request))

def output_download(request, subscription, directory, filename):
    filepath = THIS_DIR + '/output/'+subscription+'/'+directory+'/' + filename
    logger.info(filepath)
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

def output_view(request, subscription, directory, filename):
    filepath = THIS_DIR + '/output/'+subscription+'/'+directory+'/' + filename
    logger.info(filepath)
    path = open(filepath, 'r')
    mime_type, _ = mimetypes.guess_type(filepath)
    lines = path.readlines()
    cont = '\t'.join([line.strip() for line in lines])
    response = HttpResponse(cont, content_type=mime_type, status=200)
    return response

def authenticate_sp_form(request):
    template = loader.get_template('authenticatespform.html')
    return HttpResponse(template.render({}, request))

def authenticate_service_principal(request):
    cmd = "az login --service-principal -u " + request.POST['app_id'] + " -p "+request.POST['app_secret']+" --tenant " + request.POST['tenant_id']
    #cmd="az --version"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        return HttpResponse("Success : Service Principal authenticated successfully.")

    return HttpResponse("Failed: Service Principal could not be authenticated, please check parameters or logs.")
