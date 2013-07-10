title: "Utiliser le module Upload de Nginx"
layout: blog_post
tags:
- Nginx
published_date: 2013-07-10
links:
- name: Nginx
  href: http://nginx.org/en/
- name: Upload Module
  href: http://www.grid.net.ru/nginx/upload.en.html


Pendant le développement de [Flaskup](http://git.deltalima.net/flaskup/), j'ai dû faire face à une problématique concernant l'upload de fichiers volumineux. Le problème venait de performances médiocres à la fin de l'upload : le navigateur a fini d'envoyer la requête contenant notre fichier, et Flaskup pouvait mettre plusieurs minutes à répondre (pas terrible...).

On verra donc deux choses dans ce billet :

- pourquoi le serveur met si longtemps à nous répondre
- comment résoudre ce problème avec le module Upload de Nginx

<!-- BODY -->

### Pourquoi ?

Pour bien comprendre le mécanisme, il faut suivre le cheminement de la requête POST contenant notre fichier. Dans mon cas, j'utilise Nginx et Gunicorne. Le POST passe donc par deux étapes avant d'arriver jusqu'à Flaskup.

#### Nginx

Nginx est utilisé en tant que reverse-proxy, et son fonctionnement par défaut fait qu'il bufferise entièrement le POST avant de l'envoyer au backend (Gunicorn). Si la taille du POST dépasse une certaine limite, le POST est enregistré dans un fichier temporaire (c'est la directive [`client_body_buffer_size`](http://wiki.nginx.org/HttpCoreModule#client_body_buffer_size)). Autant vous le dire tout de suite, dès que vous aurez un POST un peu conséquent, même s'il ne contient pas de fichier, il sera écrit sur le disque.

Bon, Nginx écrit notre requête sur le disque, pourquoi pas, il faut bien que le fichier soit stocké quelque part.

Une fois que Nginx a reçu tout le contenu du POST (le navigateur a tout envoyé et maintenant il attend une réponse), Nginx va renvoyer ce même POST vers le backend.

#### Gunicorn

Gunicorn va donc recevoir également un POST énorme contenant notre fichier volumineux. Et que va-t-il faire ? Comme son ami Nginx, bufferiser la requête dans un fichier temporaire.

Si Nginx et Gunicorn sont sur la même machine, il s'agit ni plus ni moins que d'une copie d'un fichier de manière inefficace (ben oui, passer par HTTP et Python c'est forcement moins rapide qu'un bête `cp`). Dans le cas où Nginx et Gunicorn seraient sur deux machines séparées, il y aurait un transfert réseau et une écriture sur le serveur Gunicorne.

#### Flaskup

Et maintenant entre en jeu Flaskup. Gunicorn a bien reçu notre POST, il passe la main à Flaskup. Flaskup utilisant le framework [Flask](http://flask.pocoo.org/), lui-même basé sur [Werkzeug](http://werkzeug.pocoo.org/), il voit arriver un objet [`FileStorage`](http://werkzeug.pocoo.org/docs/datastructures/#werkzeug.datastructures.FileStorage) représentant notre fichier uploadé. Pour sauvegarder le fichier dans sa destination finale (là où on souhaite qu'il soit stocké), l'objet `FileStorage` a une méthode appelée [`save(dst)`](http://werkzeug.pocoo.org/docs/datastructures/#werkzeug.datastructures.FileStorage.save). Et que fait cette méthode ? Elle copie notre fichier vers sa destination finale.

#### Conclusion

Au final, on se retrouve avec trois copies identiques de notre fichier, dont deux copies effectuées pendant que notre navigateur attend sa réponse. Si le fichier commence à être un peu volumineux (plusieurs centaines de Mo) et que le serveur hébergeant Flaskup à des I/O pas terrible (merci la virtualisation !), on peut très vite perdre quelques dizaines de secondes à plusieurs minutes entre la fin de l'upload et la réponse du serveur.


### Utilisation du module Upload

Pour avoir un comportement utilisable (c'est-à-dire que le serveur doit répondre rapidement), il est absolument indispensable d'éviter toute copie du POST ou du fichier. Et, Ôh miracle, c'est exactement ce que nous propose le [module Upload](http://www.grid.net.ru/nginx/upload.en.html) d'Nginx.

Le principe de fonctionnement de ce module est le suivant :

1. intercepter la requête du navigateur
2. streamer le contenu du fichier (pas le POST en entier, juste le fichier) dans un emplacement défini
3. modifier le POST pour remplacer le contenu du fichier par divers informations sur celui-ci (sa taille, son emplacement sur le disque, etc.)

Gunicorn et Flaskup reçoivent donc un POST très léger ne contenant plus que quelques champs. Charge ensuite à l'application de *déplacer* le fichier vers sa destination finale. Le terme "déplacer" est très important, c'est une opération beaucoup moins coûteuse qu'une copie.

#### Configuration de module

La configuration ne se fait pas automagiquement, il faut indiquer au module sur quelle URL il doit intercepter les POSTs et quels champs doivent être modifiés.

Dans le cas de Flaskup, la configuration ressemble à ceci:

    ::nginx
    server {

            [...]

            location = /upload {
                    upload_pass     @upstream;
                    upload_store    /path/to/some_folder;
                    upload_store_access     user:rw;

                    upload_set_form_field   $upload_field_name.name "$upload_file_name";
                    upload_set_form_field   $upload_field_name.path "$upload_tmp_path";

                    upload_pass_form_field "^myemail$|^mycontacts$";
                    upload_cleanup 400-599;
            }
    }

- le module Upload traite les POSTs arrivant sur l'URL `/upload`
- le champ contenant le fichier uploadé est remplacé dans deux nouveaux champs contenant le nom (`$upload_field_name.name`)et le chemin (`$upload_field_name.path`)
- les champs `myemail` et `mycontacts` sont conservés et ne sont pas modifiés
- tout autre champ du POST est supprimé

Il est important que la valeur de `upload_store` indique un emplacement au plus proche (physiquement) de la destination finale du fichier, et si possible sur la même partition. Ceci permet d'éviter une copie lors du déplacement final du fichier.

#### Modifications dans Flaskup

Pour pouvoir utiliser le POST modifié par le module Upload, il faut également modifier le code de l'application. Pour Flaskup, ça c'est fait assez rapidement (un peu trop même :p) : voir le [commit correspondant](http://git.deltalima.net/flaskup/commit/?id=335e6387704bc1cb0d4da7718773c265f27278d9).

#### Conclusion

Nginx (via le module Upload) va tranquillement streamer le contenu du fichier vers `upload_store` (pendant l'upload) et il n'y aura qu'un déplacement d'effectué à la fin. Et donc, une seule copie du fichier et très peu d'I/O. Le serveur répond maintenant instantanément.

Well done!

### Et la sécurité ?

Et oui, on n'y pense pas tout de suite... On vient d'ajouter une fonctionnalité trop classe, le serveur répond de manière instantanée, tout fonctionne et on est super content. Sauf que, si on ne vérifie pas ce qui nous arrive, on laisse la possibilité à n'importe qui de déplacer n'importe quel fichier dans un emplacement plus ou moins prévisible (et accessible).

Imaginez qu'on reçoive un POST avec le champ `myfile.path` valant `/etc/passwords`. Notre application va gentillement déplacer ce fichier et le rendre accessible. Oups...

Il faut donc ajouter des contrôles sur ce qui nous arrive. Ce qui a fait l'objet d'un [second commit](http://git.deltalima.net/flaskup/commit/?id=a44fe298413f18dff75888460ba966829d81900e) pour Flaskup (maintenant vous comprenez mon "un peu trop même" juste au dessus...).

- il faut préciser dans la configuration que le module Upload est utilisé
- le fichier à déplacer doit se situer dans un emplacement spécifié, les fichiers en dehors de cet emplacement ne seront pas déplacés

De toute façon, il faut *TOUJOURS* vérifier les données reçues. S'il n'y a qu'un conseil à donner, c'est bien celui-là.
