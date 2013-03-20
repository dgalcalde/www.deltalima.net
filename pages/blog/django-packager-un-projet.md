title: "Django : packager un projet"
layout: blog_post
tags:
- Python
- Django
- distribute
published_date: 2013-03-20
links:
- name: Django
  href: https://www.djangoproject.com/
- name: Distribute
  href: http://pypi.python.org/pypi/distribute


Dans ce billet, je vais décrire une méthode pour packager un projet Django avec [distribute](http://pypi.python.org/pypi/distribute), le but étant d'avoir un joli tarball qu'on peut ensuite uploader sur le [CheeseShop](http://pypi.python.org) ou installer directement dans un virtualenv.

Un peu de vocabulaire pour bien commencer, dans le monde de Django il faut bien faire la différence entre une **application** et un **projet** :

- Une application est un ensemble de fonctionnalités ajoutées à Django.
- Un projet est une instance de Django. Un projet va utiliser plusieurs applications (listées dans `INSTALLED_APPS`).

Nous allons voir comment packager un projet Django et non une application. Comme je n'ai trouvé pratiquement aucune ressource sur ce sujet sur le web, je me permets de partager ma technique, ça intéressera peut-être quelques personnes :)

Bon, maintenant que tout le monde sait de quoi on va parler, allons-y !

<!-- BODY -->

### Le principe

On va utiliser le classique distribute pour faire un package. Ce qui revient à utiliser le fichier que vous connaissez déjà : `setup.py`. La seule difficulté est de réussir à transformer un projet Django en un module Python (c'est la condition pour utiliser distribute).

Au final, la procédure d'installation ressemblera à ceci :

    ::bash
    $ virtualenv env
    $ . ./env/bin/activate
    (env) $ pip install myproject-1.0.tar.gz

### Initialiser le projet Django

Pour initialiser un projet Django, vous connaissez tous la commande `django-admin.py` :

    ::bash
    $ django-admin.py startproject myproject

Cette commande va créer une arborescence qui ressemble à ceci :

    ::bash
    myproject/__init__.py
    myproject/wsgi.py
    myproject/urls.py
    myproject/settings.py
    manage.py

À partir de maintenant, tous les développements se feront uniquement dans le dossier `myproject/`. Et vous avez certainement remarqué la présence du fichier `__init__.py`, la seul présence de ce fichier fait du dossier `myproject/` un module Python, ce qui va nous simplifier la vie avec distribute.

Vous pouvez tester avec une console Python :

    ::bash
    $ ls manage.py myproject/
    $ python
    >>> import myproject
    >>>

### Ajouter setup.py

Nous allons ajouter un fichier `setup.py` à la racine de l'arborescence avec le contenu suivant :

    ::python
    from setuptools import setup, find_packages

    version='0.1.0'

    setup(
        name='myproject',
        version=version,
        description='Django skeleton project',
        long_description=__doc__,
        author='Laurent Meunier',
        author_email='laurent@deltalima.net',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=['Django==1.5'],
    )

Avec ce nouveau fichier, on peut maintenant créer notre package :

    ::bash
    $ python setup.py sdist

Si tout se passe bien (et ça devrait bien se passer), vous obtenez un tarball `myproject-0.1.0.tar.gz` dans le dossier `dist/`.

L'arborescence devrait maintenant ressembler à ceci :

    ::bash
    myproject.egg-info/...
    myproject/__init__.py
    myproject/wsgi.py
    myproject/urls.py
    myproject/settings.py
    dist/myproject-0.1.0.tar.gz
    manage.py
    setup.py

Il est maintenant possible d'installer `myproject-0.1.0.tar.gz` dans un nouveau virtualenv, Django sera installé automatiquement (il est dans le `install_requires`) et notre projet sera installé comme un module Python classique.

Bon, c'est pas mal tout ça, mais il y a juste un petit problème. Que faire du script `manage.py` ? Dans l'état actuel, il est en dehors du module Python et ne pourra donc pas être dans le package généré par distribute.

### Gérer le cas de manage.py

Le script `manage.py` est indispensable pour tous projets Django et il faut absolument le conserver. C'est lui qui nous permet de lancer les différentes commandes liées au projet comme initialiser la base de données (`syncdb`) ou récupérer tous les fichiers statiques (`collectstatic`).

D'après la [documentation de Django](https://docs.djangoproject.com/en/1.5/ref/django-admin/), `manage.py` est juste une surcouche à `django-admin.py`. En théorie, on pourrait supprimer `manage.py` et utiliser uniquement `django-admin.py`. En pratique, on va le conserver et l'intégrer proprement au package en deux étapes :

- déplacer/modifier `manage.py` dans le dossier `myproject/`
- ajouter une entrée `console_scripts` dans `setup.py`


Pour commencer, nous allons déplacer `manage.py` dans le dossier `myproject/`, ceci a pour conséquence de l'ajouter au package créé avec distribute. Par contre, nous ne pourrons pas l'utiliser en l'état, il faut le modifier légèrement.

    ::python
    import os
    import sys

    def main():
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)


Ensuite, nous allons modifier `setup.py` pour ajouter une entrée `console_scripts` :

    ::python
    setup(
        [...]
        entry_points={
            'console_scripts': [
                'myproject_admin = myproject.manage:main',
            ],
        }
    )

L'ajout de `console_scripts` indique à distribute de créer, lors de l'installation du package, un script nommé `myproject_admin` qui exécutera la fonction `main` du module `myproject.manage`.

Le script sera créé dans le `PATH` et sera donc accessible directement en ligne de commande.

    ::bash
    (env) $ myproject_admin runserver
    Validating models...

    0 errors found
    March 19, 2013 - 13:45:53
    Django version 1.5, using settings 'myproject.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Nous avons ainsi remplacé `manage.py` par un nouveau script `myproject_admin` qui a exactement le même comportement (accepte les mêmes commandes `syncdb`, `runserver`, etc.) et qui est intégré à notre package. On a fini alors ? Pas tout à fait, il nous reste encore un point à voir : la configuration.


### Gérer la configuration

La configuration d'un projet Django se fait généralement dans le fichier `settings.py`. Mais maintenant que notre projet est packagé puis installé dans un virtualenv, il est fortement déconseillé d'aller modifier `settings.py` directement dans le virtualenv : il sera écrasé lors de la prochaine mise à jour du package.

Il faut trouver un moyen de lire un fichier de configuration externe au virtualenv. Pour cela, j'ajoute simplement les trois lignes suivantes à la fin de mon `settings.py` :

    ::python
    import os
    if 'MYPROJECT_CONFIG' in os.environ:
        execfile(os.environ['MYPROJECT_CONFIG'])

Si une variable d'environnement nommée `MYPROJECT_CONFIG` existe, alors on va exécuter le script Python indiqué par cette variable.

On peut alors utiliser ce script pour définir la configuration locale (comme les accès à la base de données par exemple). Tout ce qu'il est possible de mettre dans `settings.py` peut se trouver dans ce script externe.

En pratique, ça ressemble à ceci :

    ::bash
    (env) $ export MYPROJECT_CONFIG=/etc/myproject/local_settings.py
    (env) $ myproject_admin runserver
    Validating models...

    0 errors found
    March 19, 2013 - 13:45:53
    Django version 1.5, using settings 'myproject.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.


Et voilà, il nous reste maintenant à modifier le fichier `/etc/myproject/local_settings.py` pour surcharger la configuration par défaut présente dans le projet Django.


### Une installation, plusieurs instances

Conséquence bien pratique de tout ceci : il est possible de faire fonctionner en parallèle plusieurs instances du project Django à partir d'une seule installation.


On démarre notre première instance :

    ::bash
    (env) $ export MYPROJECT_CONFIG=/etc/myproject/instance_1.py
    (env) $ myproject_admin runserver 8001
    [...]


Et toujours dans le même virtualenv, mais dans une autre console :

    ::bash
    (env) $ export MYPROJECT_CONFIG=/etc/myproject/instance_2.py
    (env) $ myproject_admin runserver 8002
    [...]


### Le mot de la fin

Pour avoir utilisé récemment cette technique avec un client, je trouve que ça facilite vraiment le déploiement. On ne passait pas par PyPI, j'envoyais directement le tarball au client qui avait juste un `pip install -U foobar-0.1.tar.gz` à faire pour mettre à jour l'application. Moins de manipulations en prod = plus de sérénité pour tout le monde. En externalisant la configuration, on est sûr de ne pas l'écraser en mettant à jour l'application, et le client est moins tenté d'aller faire des modifications quand le code est dans le virtualenv (et c'est pas plus mal...).

Pour ceux qui sont intéressés, j'ai mis en ligne un [squelette de projet Django](https://github.com/lmeunier/django-package-project-skel) avec tout ce qui est décrit dans cet article, ça devrait aider à rapidement démarrer un nouveau projet.

