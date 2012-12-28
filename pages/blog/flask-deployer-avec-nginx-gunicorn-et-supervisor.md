title: "Déployer une application WSGI avec Nginx, Gunicorn et supervisor"
layout: blog_post
tags:
- Python
- Flask
- Nginx
- Gunicorn
- supervisor
- WSGI
published_date: 2012-12-28
links:
- name: Flask
  href: http://flask.pocoo.org/
- name: WSGI
  href: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
- name: Nginx
  href: http://wiki.nginx.org/
- name: Gunicorn
  href: http://gunicorn.org/
- name: supervisor
  href: http://supervisord.org/


Nous sommes arrivés au quatrième article de [la série dédiée au framework Flask](/tag/Flask/), et pour changer on va mettre de côté nos talents de développeur pour prendre le rôle de l'admin sys et s'intéresser au déploiement d'une application [WSGI](http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface). Bien que les précédents articles soient dédiés à Flask, celui-ci sera plus généraliste et sera valable pour toutes vos applications WSGI. Alors si vous n'utilisez pas Flask, ne partez pas ! La suite pourrait vous intéresser.

Comme d'habitude, et pour bien commencer, on va déjà expliquer un peu ce qu'on cherche à faire. Et bien le but est simple : on doit déployer notre application WSGI sur un serveur. Et pour cela, on va utiliser tout une suite d'outils ayant chacun son propre rôle à jouer : Nginx, Gunicorn et supervisor.

<span class="center">
![Schéma avec Nginx, Gunicorn et supervisor](/static/img/wsgi-nginx-gunicorn-supervisor.png "Déployer une application WSGI avec Nginx, Gunicorn et supervisor")
</span>

Pour illustrer cet article, on va utiliser l'application [FlaskTODO](http://git.deltalima.net/flasktodo/) que vous commencez à connaître tous. On considère que l'application est déjà installée dans un virtualenv situé dans */opt/flasktodo/env*. Au final, on souhaite que l'appli soit disponible à l'URL suivante : [http://demo.deltalima.net/flasktodo/](http://demo.deltalima.net/flasktodo/)


### Nginx

C'est notre serveur web en frontal sur Internet (c'est à lui que les internautes vont se connecter). On va l'utiliser pour deux rôles différents : reverse-proxy vers Gunicorn et servir les fichiers statiques. Nginx est disponible dans les dépôts Debian et la version Squeeze est suffisamment récente pour ne pas avoir besoin de fouiller les backports ou de le recompiler (ouf !).

Et donc l'installation se résume à ceci :

    ::console
    # apt-get install nginx

Une fois installé, on va modifier le fichier */etc/nginx/sites-available/default* pour y ajouter une nouvelle section 'server' :

    ::nginx
    # demo.deltalima.net
    server {
            listen [::]:80;
            server_name "demo.deltalima.net";

            access_log /var/log/nginx/demo.deltalima.net_access.log combined;
            error_log  /var/log/nginx/demo.deltalima.net_error.log;

            location /flasktodo/static/ {
                    alias   /opt/flasktodo/env/lib/python2.6/site-packages/flasktodo/static/;
            }
            location /flasktodo {
                    proxy_pass       http://127.0.0.1:8004;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header Host $http_host;
                    proxy_set_header SCRIPT_NAME /flasktodo;
            }
    }


Les seuls points à noter de cette configuration sont les deux sections *location* :

- Le premier permet de servir les fichiers statiques directement depuis Nginx, ça évite de passer par Python pour une tâche que Nginx accompli à merveilles. Dans le cas de FlaskTODO, c'est inutile car il n'y a aucun fichier statique, mais je le laisse à titre d'exemple (et ça pourra servir plus tard). L'ordre est important, ce 'location' doit se trouver *avant* le suivant.
- Le second 'location' définit un reverse-proxy vers Gunicorn. Quand une requête commence par /flasktodo (autre que /flasktodo/static), celle-ci est renvoyée vers le serveur définit par la directive *proxy_pass* (et donc vers http://127.0.0.1:8004 qui n'est autre que Gunicorn).

Vous noterez qu'on souhaite déployer l'appli sur une URI différente de la racine, elle doit être accessible sur */flasktodo*. Pour ne pas avoir à modifier tous les liens de l'appli, on définit le header SCRIPT_NAME pour indiquer à Gunicorn de ne pas tenir compte de */flasktodo*. Ainsi, une requête */flasktodo/foobar* sur Nginx sera transformée en */foobar* sur Gunicorn. Si vous déployée votre appli à la racine, vous pouvez supprimer cette ligne (pensez également à modifier les URI des directives 'location').


Nginx est prêt, il ne reste plus qu'à le redémarrer :

    ::console
    # /etc/init.d/nginx restart


### Gunicorn

Gunicorn est un serveur HTTP / WSGI développé en Python. Son rôle sera d'héberger notre application WSGI et ainsi de faire l'interface entre Nginx et notre appli (dans le monde Java, il serait l'équivalent d'un Tomcat faisant tourner une application J2EE).

Pour installer Gunicorn, vous pouvez soit l'installer depuis les dépôts Debian, soit installer depuis [PyPI](http://pypi.python.org/pypi/gunicorn/) directement dans le virtualenv. J'ai choisi la second option pour deux raisons : la version disponible dans Debian commence à dater, et il est très facile de l'installer dans le virtualenv (Gunicorn étant en pur Python, il n'y a aucune autre dépendance à compiler/installer).

    ::console
    # . /opt/flasktodo/env/bin/activate
    (env)# pip install gunicorn


Comme Gunicorn est démarré par supervisor, il n'y rien de plus à faire ici.


### supervisor

Supervisor est un système de contrôle de processus. Pour être plus parlant, son but est de démarrer Gunicorn et d'être sûr que celui-ci sera toujours en cours d'exécution (en le redémarrant si besoin).

Comme pour Nginx, on va l'installer depuis les dépôts Debian :

    ::console
    # apt-get install supervisor

C'est installé, on passe à la configuration. Là, toujours rien de compliquer, on va créer un fichier dans */etc/supervisor/conf.d/* :

    ::ini
    [program:flasktodo]
    directory=/opt/flasktodo
    command=/opt/flasktodo/env/bin/python /opt/flasktodo/env/bin/gunicorn --bind=127.0.0.1:8004 --workers=2 --pid=/tmp/flasktodo.pid flasktodo:app
    user=www-data
    autostart=true
    autorestart=true
    environment=FLASKTODO_CONFIG='/opt/flasktodo/config.py'
    stdout_logfile=/var/log/supervisor/%(program_name)s_stdout.log
    stderr_logfile=/var/log/supervisor/%(program_name)s_stderr.log


La plupart des options sont une fois de plus suffisamment explicites. Je vais juste revenir sur deux d'entres elles :

- *command* : C'est ici qu'on va définir la commande pour lancer Gunicorn depuis le virtualenv. On retrouve également les options de Gunicorn dont '--bind=127.0.0.1:8004' qui devrait vous rappelez quelque chose (si non, retournez voir la configuration de Nginx).
- *environment* : Permet de définir les variables d'environnements du processus Gunicorn. On définit ici la variable FLASKTODO_CONFIG avec le chemin vers le fichier /opt/flasktodo/config.py qui sera utilisé au démarrage de FlaskTODO pour charger sa configuration. C'est spécifique à cette application, alors ne recopiez pas bêtement cette ligne vu qu'il y a de fortes chances que ce soit différent dans votre cas.

Tout est prêt, on recharge la configuration de supervisor :

    ::console
    # supervisorctl update
    flasktodo: added process group


Supervisor connait maintenant notre programme et le démarré automatiquement (autostart=true). On vérifie que tout est bien démarré :

    ::console
    # supervisorctl status
    flasktodo                        RUNNING    pid 1374, uptime 0:02:07

    # ps auxf
    [...]
    root      4776  0.0  2.2  52740 10944 ?        Ss   07:06   0:10 /usr/bin/python /usr/bin/supervisord
    www-data  1374  0.1  2.2  38432 10560 ?        S    19:16   0:00  \_ /opt/flasktodo/env/bin/python /opt/flasktodo/env/bin/gunicorn --bind=127.0.0.1:8004 --workers=2 --pid=/tmp/flasktodo.pid flasktodo:app
    www-data  1377  0.0  2.9  46752 13976 ?        S    19:16   0:00      \_ /opt/flasktodo/env/bin/python /opt/flasktodo/env/bin/gunicorn --bind=127.0.0.1:8004 --workers=2 --pid=/tmp/flasktodo.pid flasktodo:app
    www-data  1378  0.0  2.9  46760 13980 ?        S    19:16   0:00      \_ /opt/flasktodo/env/bin/python /opt/flasktodo/env/bin/gunicorn --bind=127.0.0.1:8004 --workers=2 --pid=/tmp/flasktodo.pid flasktodo:app


### Le mot de la fin

Tout est en place, tout fonctionne et FlaskTODO est disponible comme prévu à l'adresse [http://demo.deltalima.net/flasktodo/](http://demo.deltalima.net/flasktodo/). Ouf, on peut souffler :)

Notez bien que je présente une des solutions possibles pour déployer une application WSGI. On aurait pu faire plus simple en se passant de supervisor (en démarrant Gunicorn avec un script d'init), ou encore en remplaçant nginx par [Apache](http://httpd.apache.org/), ou Gunicorn par [un autre serveur WSGI](http://www.wsgi.org/en/latest/servers.html). Le plus important est de comprendre le rôle de chaque composant et de bien connaitre les outils choisis (comme souvent...).

Prochain article : automatiser le déploiement avec [Fabric](http://fabfile.org).

