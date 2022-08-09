from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Policy

import os
import logging
#import c7n_azure
#from c7n.commands import run
#from c7n.config import Config



# Create your views here.

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

def addrecord(request):
    policy = Policy(name=request.POST['name'], subscription_id=request.POST['subscription_id'],description=request.POST['description'], file_path=request.POST['file_path'])
    policy.save()
    return HttpResponseRedirect(reverse('index'))

def set_subscription(subscription_id):
    cmd = "az account set -s "+subscription_id
    returned_value = os.system(cmd)
    #create directory if dosent exist
    #path = "./output/"+subscription_id
    #isExist = os.path.exists(path)
    #if not isExist:
    #    os.makedirs(path)
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
    policy.name = request.POST['name']
    policy.subscription_id = request.POST['subscription_id']
    policy.description = request.POST['description']
    policy.file_path = request.POST['file_path']
    policy.save()
    return HttpResponseRedirect(reverse('index'))

def execute_policy(request, id):
    
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    policy = Policy.objects.get(id=id)
    result = set_subscription(policy.subscription_id)
    ymlfile = THIS_DIR+policy.file_path
    logger = logging.getLogger(__name__)
    logger.info('-----------------Ploicy Ececution Started------------------------')
    THIS_DIR=os.path.dirname(os.path.abspath(__file__))
    logger.info(ymlfile)
    OUT_DIR = THIS_DIR+'./output/'+policy.subscription_id
    #assumed_role = 'arn:aws:iam::749812993810:role/cloudcustodian_role'
    filename= THIS_DIR+policy.file_path
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
        run(run_config)
    except:
        return HttpResponse("Exception occurred.")
    
    return HttpResponse("Policy executed successfully....")


def policy_log_output(request, id):

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    lines=""
    with open(THIS_DIR+"/output/ec2-unoptimized-ebs/resources.json", "r") as file:
        next_line = file.readline()
        while next_line:
            lines =lines+"<br>"+next_line
            next_line = file.readline()

    template = loader.get_template('policyoutput.html')
    context = {
        'output': lines,
    }
    return HttpResponse(template.render(context, request))
