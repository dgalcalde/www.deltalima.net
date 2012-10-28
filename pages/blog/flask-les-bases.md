title: "Flask : les bases"
layout: blog_post
tags:
- Python
- Flask
published_date: 2012-10-28
links:
- name: Flask
  href: http://flask.pocoo.org/
- name: Flask (documentation)
  href: http://flask.pocoo.org/docs/
- name: FlaskTODO
  href: http://git.deltalima.net/flasktodo/
screenshots:
- flasktodo-ss1.png
- flasktodo-ss2.png

Souvenez-vous, dans le [premier article](/blog/flask-demarrer-un-projet/) nous avions vu comment démarrer un projet avec Flask. Nous avons créé un projet vide qui ne fait qu'afficher une erreur 404. Pas super intéressant, mais c'est déjà pas mal. Dans ce deuxième article de la série, je vais vous montrer rapidement les bases de Flask, ce qu'il faut connaitre au minimum pour se lancer. Et pour cela, rien de mieux que développer une application toute bête : une [TODO list](http://git.deltalima.net/flasktodo/).

### FlaskTODO

L'application est très simple, on va juste faire le minimum pour présenter quelques principes de développement avec Flask. Au final, on pourra réaliser les opérations suivantes :

- lister les tâches
- ajouter une nouvelle tâche
- marquer une tâche comme réalisée
- supprimer une tâche réalisée

La persistance de la liste des tâches est réalisée avec le module [Shelve](http://docs.python.org/2/library/shelve.html) de Python. Pourquoi ? Tout simplement parce que ce module est fourni en standard et qu'il est suffisamment facile d'utilisation pour ne pas nous faire perdre du temps (pas de création de base de données ou d'import de schéma).

### La configuration

Pour configurer notre application Flask, on va définir une série de variables dans *\_\_init\_\_.py* qui seront en majuscule (ce point est très important). Lors de la création de l'application Flask (l'objet *app* dans le module *flasktodo*), on utilisera la fonction *[from_object()](http://flask.pocoo.org/docs/api/#flask.Config.from_object)* qui lira les variables en majuscule pour peupler la configuration de l'application.

    :::python
    DEBUG = True
    SECRET_KEY = 'you_should_change_this_key_asap'
    DATABASE = '/tmp/flasktodo.db'
    ...
    app.config.from_object(__name__)

Les variables *DEBUG* et *SECRET_KEY* sont des [clés de configuration standard](http://flask.pocoo.org/docs/config/#builtin-configuration-values) de Flask. On ajoute juste la clé *DATABASE* qui définie le chemin vers la base de données contenant les tâches.

### Le routing d'URL

Pour faire le lien entre une URL et du code Python, Flask utilise un principe simple : on réalise un mapping entre une fonction en Python et une URL via l'utilisation du decorator *[route()](http://flask.pocoo.org/docs/api/#flask.Flask.route)*.

Un exemple tout bête qui affiche la chaine "Hello World" quand on accède à la racine de l'application :

    :::python
    @app.route('/')
    def index():
        return 'Hello World'

On est ainsi libre de choisir le format des URL et le nom des fonctions associées. Dans le cas de FlaskTODO, on a listé quatre opérations, ce qui nous fait quatre URL :

    :::python
    @app.route('/')
    def tasks_list():
        # affiche la liste des tâches

    @app.route('/add/', methods=['GET', 'POST'])
    def task_add():
        # GET  : affiche un formulaire pour ajouter une nouvelle tâche
        # POST : ajoute la tâche en base de données
        #
        # On doit préciser que cette URL accepte également les POST, par
        # défaut Flask n'acceptant que les GET.

    @app.route('/done/<int:key>/')
    def task_done(key):
        # marque une tâche comme réalisée
        #
        # Flask extrait pour nous l'id (key) de la tâche depuis l'URL et le
        # passe en paramètre de la fonction.

    @app.route('/delete/<int:key>/')
    def task_delete(key):
        # supprime une tâche
        #
        # Flask extrait pour nous l'id (key) de la tâche depuis l'URL et le
        # passe en paramètre de la fonction.

Maintenant que nous savons comment faire le lien entre une URL et une fonction, il faut savoir où placer le code. Il est possible de le mettre directement dans *\_\_init\_\_.py*, ou si on veut avoir quelque chose d'un peu propre et d'organisé, on place toutes ces fonctions dans un fichier séparé. J'ai l'habitude de mettre tout ce qui est routing d'URL dans un fichier *views.py* dans le module de l'application (sûrement une habitude venant de Django...).

Et il ne faut pas oublier d'importer *views.py* depuis *\_\_init\_\_.py* :

    :::python
    from flasktodo import views

Seul point important : il faut que cet import soit réalisé à la fin de *\_\_init\_\_.py*, sinon on risque d'avoir des dépendances circulaires entre *views.py* et *\_\_init\_\_.py*.


### Le templating

Flask n'impose aucun moteur de templating, mais il est toutefois fourni par défaut avec [Jinja2](http://jinja.pocoo.org/docs/). Si vous avez déjà fait du [Django](https://docs.djangoproject.com/en/dev/topics/templates/) ou du [Smarty](http://www.smarty.net/), vous ne serez pas perdus, on retrouve beaucoup d'idées en commun.

Le principe : on a d'un côté un template en Jinja2 et d'un autre côté un dictionnaire Python (appelé le *context*), et on utilise le second pour peupler le premier et obtenir un résultat (généralement du HTML) qu'on renvoie à l'utilisateur. Flask a pensé à nous et nous simplifie la vie avec la méthode *[render_template()](http://flask.pocoo.org/docs/api/#flask.render_template)* qui s'occupe de tout à notre place.

Voici le code dans *views.py* qui affiche la liste des tâches (uniquement 4 lignes de code) :

    :::python
    @app.route('/')
    def tasks_list():
        tasks = g.tasks
        return render_template('tasks_list.html', tasks=tasks)

Et un extrait du template *tasks_list.html* :

    :::jinja2
      <ul>
      {% for key, task in tasks.iteritems() %}
        <li>
          <p class="task-description {% if task.done %}task-done{% endif %}">
            {{ task.description }}
          </p>
          {% if task.done %}
            <a href="{{ url_for('task_delete', key=key) }}">delete</a>
          {% else %}
            <a href="{{ url_for('task_done', key=key) }}">done</a>
          {% endif %}
        </li>
      {% else %}
        <p>No task! You can <a href="{{ url_for('task_add') }}">create a new one</a>.<p>
      {% endfor %}
      </ul>


Petite explication :

- le dictionnaire *tasks* contenant nos tâches est passé au template
- on itère sur chaque tâche pour afficher sa description et un lien pour marquer cette tâche comme lue ou la supprimer
- on affiche un message si aucune tâche n'existe


### La nouvelle arborescence du projet

Après tous ces ajouts, voici à quoi ressemble la nouvelle arborescence du projet :

    flasktodo/
        env/
        src.git/
            flasktodo/
                __init__.py
                views.py
                models.py
                templates/
                    base.html
                    task_add.html
                    tasks_list.html


- [\_\_init\_\_.py](http://git.deltalima.net/flasktodo/tree/flasktodo/__init__.py?id=bc511c05afa89b1411d92a947799377f382c52f5)

On y trouve la configuration et la création de l'application Flask, ainsi que l'import des fichiers nécessaires à l'initialisation (le mapping des URL notamment).

- [views.py](http://git.deltalima.net/flasktodo/tree/flasktodo/views.py?id=bc511c05afa89b1411d92a947799377f382c52f5)

Permet de faire le mapping entre les URL et le code Python. Contient le code exécuté quand une requête arrive sur le serveur.

- [models.py](http://git.deltalima.net/flasktodo/tree/flasktodo/models.py?id=bc511c05afa89b1411d92a947799377f382c52f5)

Définition de la class *Task*. Le nom de ce fichier me vient également des habitudes prises avec Django ;)

- [templates/](http://git.deltalima.net/flasktodo/tree/flasktodo/templates?id=bc511c05afa89b1411d92a947799377f382c52f5)

Dossier contenant les templates Jinja2. Le template base.html est réutilisé par les autres templates par héritage. Les noms des autres templates sont suffisamment explicites pour ne pas avoir besoin de les présenter.

### Le mot de la fin

Et voilà, j'espère que vous avez une meilleure vision de Flask et de ses principes de fonctionnement. On n'a fait qu'effleurer les possibilités de ce merveilleux framework, le but n'est pas de réécrire la doc. Pour ça, je vous conseille d'aller directement sur le site de Flask, la [documentation](http://flask.pocoo.org/docs/) est riche, bien écrite et complète, et vous y trouverez même un [tutoriel](http://flask.pocoo.org/docs/tutorial/) bien plus complet que ces quelques lignes.

Le but ici est surtout d'avoir une petite application fonctionnelle pour démontrer toutes les facettes de la vie d'une appli web Python, du développement au déploiement.

Au niveau de Git, on est maintenant passé au [commit bc511c](http://git.deltalima.net/flasktodo/tree/flasktodo?id=bc511c05afa89b1411d92a947799377f382c52f5).
