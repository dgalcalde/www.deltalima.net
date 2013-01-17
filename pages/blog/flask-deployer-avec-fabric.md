title: "Flask : déployer une application avec Fabric"
layout: blog_post
tags:
- Python
- Flask
- Fabric
published_date: 2013-01-13
links:
- name: Flask
  href: http://flask.pocoo.org/
- name: Fabric
  href: http://fabfile.org/


Toujours dans la série d'[articles dédiées au framework Flask](/tag/Flask/), voici le cinquième dans lequel nous allons voir comment utiliser [Fabric](http://fabfile.org) pour automatiser le déploiement d'une application.

Le but est d'installer une application, et toutes ses dépendances, sur un ensemble de serveurs en une seule commande. Une mise en production d'une application est toujours une opération plus ou moins risquée, alors autant mettre toutes les chances de son côté et automatiser cette tâche au maximum. Et c'est là que Fabric intervient.

Fabric est un peu un équivalent d'un Makefile (Fabric utilise un fichier nommé *fabfile.py*, mais orienté Python et en simplifiant les échanges avec les serveurs distants. On peut ainsi facilement copier des fichiers et lancer des commandes directement sur les serveurs, le tout de manière sécurisée à travers SSH.

<!-- BODY -->

### Utilisation de Fabric

Utiliser Fabric signifie exécuter une série de commandes (locales ou distantes) de manière automatique sur un ou plusieurs serveurs. Le seul pré-requis à l'utilisation de Fabric est d'avoir une procédure de déploiement qui peut être automatisée. C'est-à-dire que si vous devez appeler Robert au service info pour lui demander de relancer un service, Fabric ne pourra pas l'appeler à votre place... Du coup, Fabric ne vous sera utile que pour une partie du déploiement (mais fort utile quand même ;) ).

Fabric fournit la commande *fab* (l'équivalent de *make*) qui va exécuter le contenu d'un fichier *fabfile.py* (l'équivalent du *Makefile*).

Mes applications sont généralement [packager avec distribute](/blog/flask-packager-application/) et fonctionnent en prod avec le trio [Nginx, gunicorn et supervisord](/blog/flask-deployer-avec-nginx-gunicorn-et-supervisor/). Ce qui simplifie grandement la procédure de déploiement qui peut se résumer à ces quelques étapes :

1. packager l'application dans une archive
2. envoyer l'archive sur le serveur
3. installer l'application à partir de l'archive
4. indiquer à Gunicorn de recharger l'application

Ce qui donne le fichier *fabfile.py* suivant :

    ::python
    from fabric.api import env, local, run, put

    env.hosts = ['user@s1.example.com']
    env.virtualenv_path = '/opt/MyApp/env'
    env.pid_file = '/tmp/gunicorn/myapp.pid'


    def pack():
        # create a new source distribution as tarball
        local('python setup.py sdist --formats=gztar', capture=False)

    def deploy():
        # figure out the release name and version
        dist = local('python setup.py --fullname', capture=True).strip()
        dist += ".tar.gz"

        # upload the source tarball to the temporary folder on the server
        put('dist/%s' % dist, '/tmp/%s' % dist)

        # install the application
        run('%s/bin/pip install /tmp/%s' % (env.virtualenv_folder, dist))

        # now that all is set up, delete the tarball
        run('rm -f /tmp/%s' % dist)

        # and finally reload of the application (send HUP to gunicorn)
        pid = run('cat %s' % env.pid_file).strip()
        run('kill -HUP %s' % pid)


Et on l'utilise de la manière suivante :

    ::console
    # ls
    fabfile.py MANIFEST.in myapp/ setup.py
    # fab pack
    [...]
    Writing MyApp-0.1/setup.cfg
    Creating tar archive
    removing 'MyApp-0.1' (and everything under it)
    
    Done.
    # fab deploy
    [user@s1.example.com] Executing task 'deploy'
    [localhost] local: python setup.py --fullname
    [user@s1.example.com] put: dist/MyApp-0.1.tar.gz -> /tmp/MyApp-0.1.tar.gz
    [user@s1.example.com] run: /opt/MyApp/env/bin/pip install /tmp/MyApp-0.1.tar.gz
    [user@s1.example.com] out: Unpacking /tmp/MyApp-0.1.tar.gz
    [user@s1.example.com] out:   Running setup.py egg_info for package from file:///tmp/MyApp-0.1.tar.gz
    [user@s1.example.com] out:     warning: no files found matching '*' under directory 'MyApp/static'
    [user@s1.example.com] out: Requirement already satisfied (use --upgrade to upgrade): Flask>=0.9 in /opt/MyApp/env/lib/python2.6/site-packages (from MyApp)
    [user@s1.example.com] out: Requirement already satisfied (use --upgrade to upgrade): Werkzeug>=0.7 in /opt/MyApp/env/lib/python2.6/site-packages (from Flask>=0.9->MyApp)
    [user@s1.example.com] out: Requirement already satisfied (use --upgrade to upgrade): Jinja2>=2.4 in /opt/MyApp/env/lib/python2.6/site-packages (from Flask>=0.9->MyApp)
    [user@s1.example.com] out: Installing collected packages: MyApp
    [user@s1.example.com] out:   Running setup.py install for MyApp
    [user@s1.example.com] out:     warning: no files found matching '*' under directory 'MyApp/static'
    [user@s1.example.com] out: Successfully installed MyApp
    [user@s1.example.com] out: Cleaning up...

    [user@s1.example.com] run: rm -f /tmp/MyApp-0.1.tar.gz
    [user@s1.example.com] run: cat /tmp/MyApp.pid
    [user@s1.example.com] out: 1448

    [user@s1.example.com] run: kill -HUP 1448

    Done.
    Disconnecting from user@s1.example.com... done.

Et encore mieux, on peut même enchaîner plusieurs tasks en une seule commande :

    ::console
    # fab pack deploy


### Aller plus loin

Ce que je viens de décrire ne montre que quelques possibilités offertes par Fabric. Pour approfondir le sujet, je vous recommande de [parcourir la doc](http://docs.fabfile.org).

Le fichier *fabfile.py* présenté juste au-dessus ne sera certainement pas adapté à votre cas mais peut il servir de point de départ. À vous d'imaginer et de mettre en place vos propres procédures de déploiement.

Avec un peu d'imagination, on peut faire des trucs assez poussés comme coupler Fabric et Git, il serait alors possible de faire un "git pull" directement depuis les serveurs en précisant un id de commit ou un tag (très pratique si vous avez une grosse application et une petite connexion montante).

    ::console
    # fab deploy:commit="5b792afabbaba31c516cf49844c8a2f5b98f88f2"

ou

    ::console
    # fab deploy:tag="v0.2.3"


