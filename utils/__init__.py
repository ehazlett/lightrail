import os

def generate_uwsgi_config(*args, **kwargs):
    '''
        Generates a uWSGI supervisor config
    '''
    app_name = kwargs['app_name']
    app_dir = kwargs['app_dir']
    ve_dir = kwargs['ve_dir']
    framework = kwargs['framework']
    uwsgi_config = '[program:uwsgi-{0}]\n'.format(app_name)
    uwsgi_config += 'command=uwsgi\n'
    # defaults
    if 'user' in kwargs:
        uwsgi_config += '  --uid {0}\n'.format(kwargs['user'])
    if 'group' in kwargs:
        uwsgi_config += '  --gid {0}\n'.format(kwargs['group'])
    uwsgi_config += '  -s {0}\n'.format(os.path.join(kwargs['app_state_dir'], '{0}.sock'.format(app_name)))
    if 've_dir' in kwargs:
        uwsgi_config += '  -H {0}\n'.format(ve_dir)
    uwsgi_config += '  -M\n'
    uwsgi_config += '  -C 666\n'
    uwsgi_config += '  -p 2\n'
    uwsgi_config += '  --no-orphans\n'
    uwsgi_config += '  --vacuum\n'
    uwsgi_config += '  --post-buffering\n'
    uwsgi_config += '  --harakiri 300\n'
    uwsgi_config += '  --max-requests 5000\n'
    uwsgi_config += '  --python-path {0}\n'.format(app_dir)
    uwsgi_config += '  -w wsgi\n'
    # uwsgi args
    if 'uwsgi_args' in kwargs:
        for k,v in uwsgi_args.iteritems():
            uwsgi_config += '  --{0} {1}\n'.format(k, v)
    uwsgi_config += 'directory={0}\n'.format(app_dir)
    if 'user' in kwargs:
        uwsgi_config += 'user={0}\n'.format(kwargs['user'])
    uwsgi_config += 'stopsignal=QUIT\n' 
    return uwsgi_config

def generate_nginx_config(*args, **kwargs):
    '''
        Generates an nginx config
    '''
    app_name = kwargs['app_name']
    deployed_url = kwargs['deployed_url']
    app_state_dir = kwargs['app_state_dir']
    cfg = 'server {\n'
    cfg += '    listen 80;\n'
    cfg += '    server_name {0};\n'.format(deployed_url)
    cfg += '    server_name_in_redirect off;\n'
    cfg += '    location / {\n'
    cfg += '        include uwsgi_params;\n'
    cfg += '        uwsgi_pass unix://{0}/{1}.sock;\n'.format(app_state_dir, app_name)
    cfg += '    }\n'
    cfg += '}\n'
    return cfg
