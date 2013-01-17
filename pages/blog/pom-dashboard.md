title: POM Dashboard
layout: projet
published_date: 2012-08-14
tags:
- projets
- php
- jquery
- json
screenshots:
- logo_POM_by_exo.jpg
- pom-dashboard-01.png
summary: Développement d'un tableau de bord (dashboard) pour intégration dans la solution POM (Plateforme Ouverte de Monitoring). Le dashboard permet aux utilisateurs de construire leurs propres interfaces, adaptées à leurs besoins.

La société [Exosec](http://www.exosec.fr) développe un outil nommé [POM (Plateforme Ouverte de Monitoring)](http://www.exosec.fr/POM-plateforme-open-source-monitoring.html). POM est un outil de monitoring basé sur le célèbre Nagios et enrichi par Exosec de nombreux modules complémentaires pour en accélèrer la mise en service, en faciliter l’utilisation quotidienne et apporter de nombreuses fonctionnalités dédiées aux exploitants. 

La prochaine version de POM sortira en septembre 2012 en version 2.8. Cette nouvelle version ajoutera un nouveau module nommé **Dashboard**. Le dashboard a pour but de présenter à l'utilisateur les informations qu'il aura lui-même sélectionnées. Il peut ainsi se construire son propre tableau de bord adapté à ses besoins : un DBA se concentrera sur ses bases de données, alors qu'un administrateur réseau souhaite voir l'état de ses routers et switchs. Le choix des informations à afficher se fait via l'utilisation de widgets dont la disposition se change d'un simple drag'n drop.

D'un point de vue technique, ce projet est très intéressant car il regroupe à la fois des défis côté serveur et côté client. L'interface web est en grande partie pilotée en Javascript avec les bibliothèques [jQuery](http://www.jquery.com) et [jQuery UI](http://www.jqueryui.com/). Sur le serveur, on retrouve le classique [PHP](http://www.php.net) couplé à une base de données [SQLite](http://www.sqlite.org/). Les échanges entre le navigateur et le serveur se font intégralement en [JSON](http://en.wikipedia.org/wiki/JSON). Nous avons voulu reprendre le principe de la _[single-page application](http://en.wikipedia.org/wiki/Single-page_application)_ pour proposer aux utilisateurs des interactions plus fluides et plus naturelles.

L'aspect sécurité a également été prise en compte. Les dashboards pouvant être soit à usage privé, soit partagés avec un groupe d'utilisateurs spécifiques, ou finalement public (accessible sans authentification à toutes personnes connaissant son URL). Le système de droits sur les dashboards a été intégré avec le système de permissions présents dans POM, il est ainsi possible à un administrateur de partager un dashboard avec uniquement certains profils d'utilisateurs, ces actions étant directement possibles depuis l'interface de configuration de POM. La gestion des permissions ne s'arrête pas là, les informations contenues dans les widgets sont également soumises aux droits de l'utilisateur : un utilisateur ne pourra pas afficher des serveurs ou des services qui ne lui sont pas accessibles.

Mes contributions sur ce projet :

-  participation à la rédaction des spécifications techniques et fonctionnelles
-  développement du code PHP côté serveur
-  développement de l'interface cliente en Javascript
-  proposition du style graphique du Dashboard
-  rédaction de la documentation technique et transfert de compétences vers l'équipe d'Exosec
