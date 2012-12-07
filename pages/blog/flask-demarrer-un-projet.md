title: "Flask : démarrer un nouveau projet"
layout: blog_post
tags:
- Python
- Flask
- Git
published_date: 2012-09-21
links:
- name: Flask
  href: http://flask.pocoo.org/
- name: FlaskTODO
  href: http://git.deltalima.net/flasktodo/


Si vous faites un peu de développement, vous devez savoir que démarrer un projet est toujours un peu pénible. On se pose pleins de questions sur les meilleurs choix à prendre : comment organiser son code, monter un environnement de développement, packager son application pour la partager avec la communauté, déployer efficacement en production, etc...

Bref, pas toujours facile d'y répondre quand on débarque sur un nouveau framework ou un nouveau langage. Du coup, je vais tenter de partager avec vous quelques conseils et astuces autour du [framework Flask](http://flask.pocoo.org) au travers de plusieurs articles. Je ne prétends pas avoir les meilleures idées ni les meilleures méthodes, mais j'ai eu l'occasion de les tester et de les améliorer avec les quelques projets réalisés ces derniers mois, et je m'en suis toujours bien sorti (ou pas trop mal en tout cas :p).

<!-- BODY -->

Pour le premier article de la série, on va commencer doucement par la base : démarrer un nouveau projet et bien s'organiser. C'est toujours mieux de partir sur de bonnes bases pour éviter de tout chambouler par la suite. Un projet bien organisé permet également de s'y retrouver plus facilement (pour les nouveaux contributeurs, ou si vous revenez dessus au bout de quelques temps).

Alors, que va-t-on voir aujourd'hui ?

- une arborescence simple et logique (enfin ... logique pour moi ne veut pas forcément dire logique pour tout le monde !)
- monter un petit environnement de dév (avec VirtualEnv)
- une intégration à Git

### L'arborescence

L'arborescence doit rester simple et ne pas comporter trop de sous niveaux (sinon je risque de m'y perdre...).

Le premier niveau comporte juste deux dossiers. Le premier, nommé *env*, contient le VirtualEnv. Le second dossier, nommé *src*, va contenir tous les fichiers versionnés. J'ai pris l'habitude de suffixer le nom du dossier avec le nom du VCS utilisé (.git ou .svn ou ...). Ça permet de voir rapidement où se trouve la racine des fichiers versionnés.

    monprojet/
        env/
        src.git/

Ce qui correspond aux commandes shell :

    :::bash
    $ mkdir monprojet
    $ cd monprojet
    monprojet/ $ virtualenv env
    monprojet/ $ mkdir src.git
    monprojet/ $ cd src.git
    monprojet/src.git/ $ git init

Le dossier *env* étant géré par le VirtualEnv, je ne vais pas m'étendre dessus. Gardez juste à l'esprit qu'il faut toujours être dans le VirtualEnv avant d'installer des modules ou de démarrer l'application. Pour me simplifier la vie, dès que je bosse sur un projet je rentre dans le VirtualEnv, je ne me pose pas de question.

Pour entrer dans le VirtualEnv :

    monprojet/ $ . ./env/bin/activate
    (env) monprojet/ $

Notez bien le "point" juste avant "./env/bin/activate", il ne faut pas l'oublier. Il indique au shell qu'il faut "sourcer" le fichier et non l'exécuter.

Puis on installe Flask (dans le VirtualEnv) :

    (env) monprojet $ pip install Flask

### L'arborescence des fichiers versionnés

Pour simplifier la gestion des fichiers Python et le déploiement, je vous recommande de faire de votre projet un [module Python](http://docs.python.org/tutorial/modules.html). Un module Python est très simple à réaliser, il suffit de créer un dossier et d'y ajouter un fichier *\_\_init\_\_.py*. Ce fichier *\_\_init\_\_.py* peut être vide ou contenir du code, mais tous les cas il *doit* exister.

    monprojet/
        env/
        src.git/
            monprojet/
                __init__.py

Et les commandes shell qui vont bien :

    :::bash
    monprojet/src.git/ $ mkdir monprojet
    monprojet/src.git/ $ touch monprojet/__init__.py

Avec cette arborescence, nous avons un module nommé *monprojet* qu'on peut importer dans un shell Python.

    :::bash
    monprojet/src.git/ $ python

    >>> import monprojet
    >>>

### Initialiser l'application Flask

Typiquement, le fichier *\_\_init\_\_.py* va nous servir à initialiser l'application Flask.

    :::python
    # -*- coding: utf-8 -*-

    from flask import Flask

    # Flask configuration
    DEBUG = True

    # Create our app
    app = Flask(__name__)
    app.config.from_object(__name__)

On peut ensuite créer un script *run-server.py* tout simple pour démarrer l'application Flask. Script à placer dans le même dossier que notre module Python.

    :::python
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    from monprojet import app
    app.run(host='0.0.0.0')

Une simple commande shell suffit ensuite à lancer l'application :

    :::bash
    (env) src.git $ python run-server.py
     * Running on http://0.0.0.0:5000/
     * Restarting with reloader

Vous pouvez maintenant ouvrir votre navigateur à l'adresse [http://localhost:5000/](http://localhost:5000/) et admirer une jolie erreur 404 ! Une erreur, oui, mais générée par Flask. Ce qui nous prouve que tout fonctionne correctement.

### Initial commit

Tout fonctionne correctement ? Ouf, on va pouvoir commiter tout ça avant de tout casser, sans oublier de créer un fichier *.gitignore* pour éviter d'ajouter les script Python compilés (les fichiers *.pyc*) dans notre dépôt Git.

    :::bash
    (env) src.git $ echo "*.pyc" >> .gitignore
    (env) src.git $ git add .gitignore run-server.py monprojet/
    (env) src.git $ git commit -m "Initial commit"


Et voilà, ce sera tout pour cet article ! Dans la suite on verra comment packager l'application avec [distribute](http://pypi.python.org/pypi/distribute) et la déployer en prod avec [Fabric](http://docs.fabfile.org/en/1.4.3/index.html).

### FlaskTODO

Pour illustrer cet article et les suivants, rien de mieux qu'une petite application développée avec Flask. C'est le but de [FlaskTODO](http://git.deltalima.net/flasktodo/), une application toute bête et toute simple qui gère une TODO list.

Et donc pour ce premier article (qui ne va pas bien loin finalement), le résultat est visible dans le [commit dd046bd](http://git.deltalima.net/flasktodo/tree/?id=dd046bdd3516a7e44f926c7ba6373393025b0e15).
