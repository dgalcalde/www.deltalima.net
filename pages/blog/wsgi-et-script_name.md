title: "WSGI et SCRIPT_NAME - ou comment déployer une application à différentes URL"
layout: blog_post
tags:
- Python
- WSGI
published_date: 2013-05-24
links:
- name: WSGI
  href: https://wsgi.org/


Vous avez déjà dû déployer une application qui n'est pas directement attachée à la racine du serveur ? Si oui et que vous avez réussi, alors vous connaissez certainement `SCRIPT_NAME`. Sinon, et bien ne partez pas, on va voir ça ensemble.

Le but est de pouvoir déployer une application WSGI et que celle-ci soit accessible à une sous-URL. Si la racine est `http://example.com/`, une sous-URL serait par exemple `http://example.com/myapp/`. Sauf que la partie `/myapp/` n'étant pas prévisible lors du développement de l'application (certaines personnes prèfèreront peut-être `/zeapp/`), on ne peut pas l'ajouter directement dans les routes de notre appli.

Pour illustrer un peu tout ça, on va partir d'une configuration classique : Nginx est en frontal et renvoie les requêtes vers notre appli écoutant sur le port `8000`.

    ::nginx
    server {
            listen [::]:80;
            server_name "example.com";

            # ... some settings ...

            location / {
                    proxy_pass       http://127.0.0.1:8000;
            }
    }

Jusque là tout va bien, l'appli fonctionne sans problème.

Maintenant, on va modifier légèrement la configuration Nginx pour déplacer notre appli dans la sous-URL `/zeapp/` :

    ::nginx
        location /zeapp/ {
                    proxy_pass       http://127.0.0.1:8000;
            }

Aïe ! Tout est cassé, plus rien ne fonctionne. Mais que se passe-t-il ?

En fait c'est simple, notre appli reçoit l'URL `/zeapp/` et essaie de la router. Comme il y a de fortes chances qu'elle ne la connaisse pas, on reçoit en retour une erreur 404. Il faut donc indiquer à notre appli de supprimer la partie `/zeapp` de l'URL avant de faire le routage. Ainsi `/zeapp/` redevient l'équivalent de `/` et le routage peut s'effectuer sans problème.

Pour cela, il suffit de définir `SCRIPT_NAME` dans la configuration Nginx:

    ::nginx
        location /zeapp/ {
                    proxy_pass       http://127.0.0.1:8000;
                    proxy_set_header SCRIPT_NAME /zeapp;
            }

Nginx va ajouter un header appelé `SCRIPT_NAME` qui contient la sous-URL lors de l'appel à notre appli. Et là, magie ! La valeur de `SCRIPT_NAME` est prise en compte pour le routage des URL. Ce qui signifie que vous n'avez absolument rien à changer dans votre appli, c'est uniquement de la configuration.

Ok, mais il se passe quoi pour les liens générés dans mes pages ?

Si vous avez choisi un bon framework et que vous utilisez les helpers pour construire les liens ([`url_for()`](http://flask.pocoo.org/docs/api/#flask.url_for) pour Flask et [`reverse()`](https://docs.djangoproject.com/en/dev/ref/urlresolvers/#reverse) pour Django), tout devrait se faire automatiquement. Il faut juste faire attention aux liens qui n'utilisent pas ces helpers. C'est typiquement le cas pour le contenu statique de Django, il faut ajouter `/zeapp` à `STATIC_URL` qui devient `/zeapp/static/`.
