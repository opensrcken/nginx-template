import os
from subprocess import call, check_output
from jinja2 import Environment, FileSystemLoader

NGINX_VERSION = "1.7.9"

ENV = os.environ['ENV']
KORAM_NGINX_FOLDER = os.environ['KORAM_NGINX_FOLDER']

# todo: set this to be owned by django
# todo: make this virtualenv a system env variable
KORAM_PIP = os.environ['KORAM_PIP']
KORAM_PYTHON = os.environ['KORAM_PYTHON']
KORAM_UWSGI = os.environ['KORAM_UWSGI']


def create_file(dest_filename, template_filename, args={}, chmod=0770):
    template = env.get_template(template_filename)
    output = template.render(args)

    with open(dest_filename, 'w') as file:
        file.write(output)
    os.chmod(dest_filename, chmod)


template_loader = FileSystemLoader(searchpath=KORAM_NGINX_FOLDER + "/templates")
env = Environment(loader=template_loader)

def gen_compile_file():
    modules = [x for x in os.listdir(KORAM_NGINX_FOLDER + '/modules')]
    compile_file = KORAM_NGINX_FOLDER + '/script/compile'
    create_file(compile_file, "compile.jinja2", {
        'modules': modules,
        'NGINX_VERSION': NGINX_VERSION,
        'KORAM_NGINX_FOLDER': KORAM_NGINX_FOLDER
    })


def gen_bootstrap_file():
    bootstrap_file = KORAM_NGINX_FOLDER + '/script/bootstrap'
    create_file(bootstrap_file, "bootstrap.jinja2", {'NGINX_VERSION': NGINX_VERSION})


def gen_conf_file():
    create_file(KORAM_NGINX_FOLDER + '/nginx.conf', 'nginx.conf.jinja2', {
        'env': os.environ
    })


def bootstrap_nginx():
    if not os.path.isfile(KORAM_NGINX_FOLDER + '/vendor/' + NGINX_VERSION) or not os.path.isfile(KORAM_NGINX_FOLDER + '/build/nginx/sbin/nginx'):
        gen_bootstrap_file()
        call(KORAM_NGINX_FOLDER + "/script/bootstrap", shell=True)

    gen_compile_file()
    gen_conf_file()

    cmd = KORAM_NGINX_FOLDER + "/script/compile"

    print cmd
    call(cmd, shell=True)

    # indicator that nginx is already running
    if os.path.isfile(KORAM_NGINX_FOLDER + '/build/nginx/logs/nginx.pid'):
        cmd = KORAM_NGINX_FOLDER + "/build/nginx/sbin/nginx -s stop"
        print cmd
        call(cmd, shell=True)

    cmd = KORAM_NGINX_FOLDER + "/build/nginx/sbin/nginx"
    print cmd
    call(cmd, shell=True)


bootstrap_nginx()
