title: "Flask : packager une application"
layout: blog_post
tags:
- Python
- Flask
published_date: 2012-12-07
links:
- name: Flask
  href: http://flask.pocoo.org/
- name: Flask (documentation)
  href: http://flask.pocoo.org/docs/
- name: Distribute
  href: http://pypi.python.org/pypi/distribute
- name: FlaskTODO
  href: http://git.deltalima.net/flasktodo/


Troisième article de [la série dédiée au framework Flask](/tag/Flask/), cette fois-ci nous allons voir comment packager une application en utilisant [distribute](http://pypi.python.org/pypi/distribute). Distribute est une bibliothèque Python permettant de packager une application puis d'installer facilement le package créé. Le but étant de pouvoir distribuer une application développée avec Flask et de permettre son installation le plus facilement possible.

Je ne vous apprends rien en vous disant que l'adoption d'une application se fait, en partie, en fonction de sa facilité d'installation. Bien sûr, c'est loin d'être le seul critère, mais généralement l'installation est le premier contacte de l'utilisateur avec l'appli, et si on ne veut pas le faire fuir tout de suite, il est préférable que cette étape se passe le mieux possible. Et comme on est tous des vieux qui trainons nos vielles habitudes, le mieux est encore d'utiliser des outils standards et biens connus de tous.

<!-- BODY -->

Les bibliothèques utilisées par Flask et Flask lui-même sont packagés en utilisant distribute. Ce qui nous permet de les installer très facilement depuis le [cheeseshop](http://pypi.python.org) avec un simple commande :

    ::bash
    $ pip install Flask

*pip*, via les informations du package Flask, va télécharger et installer automatiquement Flask ainsi que toutes ses dépendances.

Comme d'habitude, quand on parle d'installer des packages Python, le mieux est de travailler dans un *virtualenv*.


### Script setup.py

La création d'un package passe par l'édition d'un script Python. Ce script est généralement nommé *setup.py*, mais cela est plus une convention qu'autre chose. Je vous encourage néanmoins à conserver ce nom pour ne pas perturber les personnes qui installeront votre application.

Un fichier *setup.py* basique pour FlaskTODO ressemble à ceci :

    ::python
    from setuptools import setup, find_packages

    version='0.1'

    setup(
        name='FlaskTODO',
        version=version,
        description='TODO list application',
        long_description=__doc__,
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=['Flask>=0.9'],
    )


La plupart des champs sont suffisamment explicites pour ne pas nécessiter d'explication. Il y en a juste trois que je vais détailler rapidement : packages, include_pacakge_data et zip_safe.

- *packages* : Pour que distribute puisse construire votre package, il faut lui indiquer tous les modules de votre application. Pas seulement le module principale , mais également tous les sous-modules. Pour cela, soit vous tenez la liste à la main, soit vous utilisez *find_packages()* qui, comme son nom l'indique, va trouver tout seul les pacakges.
- *include_package_data* : Ce paramètre indique à distribute de lire le contenu d'un fichier *MANIFEST.in* et d'ajouter dans le package tous les fichiers qui y sont listés. C'est ce que nous utiliserons pour packager le contenu des dossiers *static* et *template*.
- *zip_safe* : Ce flag indique si l'application doit être installée sous forme de fichier Zip ou d'une arborescence classique dossiers/fichiers. Il est conseillé de désactivé l'installation au format Zip car son support n'est pas universel dans toutes les implémentations de Python et ça rend le debuging pénible (des informations sont manquantes comme le nom du fichier ou la ligne où s'est produit l'erreur).

### Gestion des dépendances

Vous avez du remarquer la ligne contenant *install_requires*, elle indique les dépendances à installer en même temps que votre package. Par défaut, c'est la dernière version disponible sur PyPI qui est installée, mais vous pouvez modifier ce comportement en utilisant des opérateurs comme : *>=*, *==*, ou *<=*.

    :::python
    install_requires=[
        'Flask>=0.9',
        'Flask-Mail==0.7.4',
        'SQLAlchemy>=0.7,<=1.0',
    ]


### Ajouter des ressources

Dans son comportement par défaut, distribute package uniquement les fichiers Python présents dans les modules listés par *packages*. Si on package notre application en l'état, on ne récupère pas les dossiers comme 'static' ou 'template' (qui sont pourant nécessaires). Pour ajouter ces dossiers, il faut créer un fichier *MANIFEST.in* dans le même dossier que votre *setup.py*. Les fichiers listés dans ce fichier seront ajoutés à l'archive.

    recursive-include flasktodo/templates *
    recursive-include flasktodo/static *

Le contenu du fichier MANIFEST.in est utilisé uniquement si include_package_data=True.


### Créer un package

Bon, tout est en place pour créer notre premier package. Pour lancer la génération du package, on utilise le script setup.py :

    :::bash
    $ python setup.py sdist

Cette commande va créer une archive *FlaskTODO-0.1.tar.gz* dans le dossier *dist/*. Cette archive peut maintenant être partagée avec le monde entier et l'installation de notre application se fera en quelques commandes.


### Installer le package

Pour installer le package, rien de plus simple : on va créer un nouveau virtalenv puis installer l'application FlaskTODO.

    :::bash
    $ virtualenv env
    $ . ./env/bin/activate
    (env)$ tar xzf FlaskTODO-0.1.tar.gz
    (env)$ cd FlaskTODO-0.1/
    (env)$ python setup.py install

Et voilà, en cinq commandes j'ai pu installé mon application ainsi que toute ses dépendances dans un nouvel environnement.

Si tout s'est bien passé, on peut maintenant démarrer FlaskTODO :

    :::bash
    (env)$ python
    >>> from flasktodo import app
    >>> app.run()
     * Running on http://127.0.0.1:5000/


