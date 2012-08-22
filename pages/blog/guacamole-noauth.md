title: Supprimer la page d'authentification de Guacamole
layout: blog_post
tags:
- java
- guacamole
published_date: 2012-08-22
screenshots:
- screenshot-guacamole-noauth.png
attachments:
- guacamole-noauth-0.1.tar.gz
- guacamole-noauth-0.1.0.jar
links:
- name: Guacamole
  href: http://guac-dev.org/
- name: guacamole-noauth
  href: http://git.deltalima.net/guacamole-noauth/


Pour le premier article technique, on va commencer doucement avec un peu de Java (une fois n'est pas coutume). Nous allons voir comment supprimer la page d'authentification de [Guacamole](http://guac-dev.org/) pour permettre aux utilisateurs d'arriver directement sur la fenêtre de prise en main à distance.

### Guacamole ?

Ok mais, quel est le rapport entre [un accompagnement à base d'avocats](http://fr.wikipedia.org/wiki/Guacamole) et la prise en main à distance ? Et bien le guacamole ne sert pas juste à accompagner vos fajitas, c'est également un _HTML5 Clientless Remote Desktop_. Pour résumer, c'est une interface web qui permet d'accéder à des serveurs [VNC](http://fr.wikipedia.org/wiki/Virtual_Network_Computing) et [RDP](http://fr.wikipedia.org/wiki/Remote_Desktop_Protocol) en utilisant uniquement un navigateur web compatible HTML5 (rien à installer de plus, pas de plugin). Le navigateur web se connecte au serveur Guamacole qui fait office de proxy entre le navigateur et les vrais serveurs VNC et RDP.

En pratique, on va retrouver plusieurs composants :

- l'interface web en HTML5 / Javascript
- une application J2EE à faire tourner dans un Tomcat
- un démon guacd
- et bien sûr votre serveur VNC ou RDP

Le cheminement est le suivant : navigateur web → Tomcat → guacd → VNC ou RDP.

Pour accéder à Guacamole, les utilisateurs doivent tout d'abord s'authentifier dans l'interface web avant d'accéder à l'interface de prise en main à distance. Sur le principe, je ne trouve rien à redire, l'accès aux ressources VNC et RDP est protégée et il faut un compte pour y accéder. Sauf que dans mon cas, j'ai un unique serveur RDP en backend (géré par [xrdp](http://www.xrdp.org/)) qui demande lui aussi une authentification avant d'ouvrir une session. Pour accéder à mon bureau à distance, je me retrouve donc avec deux systèmes d'authentification à la suite : Guacamole et xrdp. Pas insurmontable, mais quand même très gênant pour mes utilisateurs. D'où l'idée de développer un petit truc rapidement en Java pour supprimer l'authentification de Guacamole et ainsi arriver directement sur la fenêtre de login de xrdp.

Par chance, Guacamole nous permet de changer facilement la méthode pour authentifier les utilisateurs (comme le monde est bien fait !). Il suffit d'écrire une nouvelle classe Java qui implémente l'interface [AuthenticationProvider](http://guac-dev.org/doc/guacamole-ext/net/sourceforge/guacamole/net/auth/AuthenticationProvider.html). Il y a une unique fonction à implémenter : getAuthorizedConfigurations(). Cette fonction récupère en paramètre un objet [Credentials](http://guac-dev.org/doc/guacamole-ext/net/sourceforge/guacamole/net/auth/Credentials.html) que nous allons royalement ignorer pour renvoyer la liste des configurations disponibles.

Tout le code est présent dans le [dépôt git public](http://git.deltalima.net/guacamole-noauth/), et l'unique fichier intéressant est [NoAuthenticationProvider.java](http://git.deltalima.net/guacamole-noauth/tree/src/main/java/net/deltalima/guacamole/NoAuthenticationProvider.java).

Bon, trêve de blabla, nous allons voir maintenant comment intégrer [guacamole-noauth](http://git.deltalima.net/guacamole-noauth/) à votre serveur Guacamole. La procédure est assez simple :

1. récupérer et compiler guacamole-noauth
2. l'installer dans Tomcat
3. modifier la configuration de Guacamole
4. Profit!

### Compiler guacamole-noauth

Le projet guacamole-noauth est disponible sur [un dépôt git public](http://git.deltalima.net/guacamole-noauth/), vous pouvez souhaite cloner le dépôt :

    :::bash
    $ git clone http://git.deltalima.net/guacamole-noauth/
    $ cd guacamole-noauth
    $ git tag -l
    $ git checkout v0.1

soit récupérer une archive déjà prête :

    :::bash
    $ wget http://git.deltalima.net/guacamole-noauth/snapshot/guacamole-noauth-0.1.tar.gz
    $ tar xzf guacamole-noauth-0.1.tar.gz
    $ cd guacamole-noauth-0.1

Pour compiler guacamole-noauth, vous aurez besoin de [Maven](http://maven.apache.org/). Une fois installé, une simple commande suffit pour générer un jar.

    :::bash
    $ mvn package

Si tout se passe bien, vous devriez voir un **BUILD SUCCESS** vers la fin de la sortie de la commande. Sinon, cherchez les messages d'erreur et essayez de les corriger...

Bon, la compilation est finie, vous avez maintenant un joli fichier _guacamole-noauth-0.1.0.jar_ dans le dossier target.

Pour les réfractaires à la compilation, à Java ou à Maven, [un jar précompilé de la v0.1 est disponible](/static/guacamole-noauth-0.1.0.jar).

### Installer guacamole-noauth

Pour installer guacamole-noauth, il suffit de copier le jar dans le bon dossier. Obvious ? Pas tant que ça...

J'ai essayé de placer ce jar dans plusieurs dossiers de Tomcat (common/lib/ et shared/lib/ en premier), mais le seul emplacement qui convient est le dossier **webapps/guacamole/WEB-INF/lib/**. Pourquoi ? Aucune idée... Si quelqu'un à une explication, [je suis preneur](mailto:laurent@deltalima.net).

### Configurer Guacamole

Le fichier de configuration de Guacamole est _/etc/guacamole/guacamole.properties_. Il faut éditer ce fichier pour avoir quelque chose qui ressemble à ceci :

    # Hostname and port of guacamole proxy
    guacd-hostname: localhost
    guacd-port:     4822

    # Auth provider class (authenticates user/pass combination, needed if using the provided login screen)
    #auth-provider: net.sourceforge.guacamole.net.basic.BasicFileAuthenticationProvider
    #basic-user-mapping: /etc/guacamole/user-mapping.xml

    auth-provider: net.deltalima.guacamole.NoAuthenticationProvider
    noauth-config: /etc/guacamole/noauth-config.xml

Nous avons donc remplacer le _auth-provider_ par défaut par notre nouvelle classe _NoAuthenticationProvider_. La liste des serveurs VNC et RDP se trouve maintenant dans le fichier de configuration défini par _noauth-config_.

Créons notre fichier __/etc/guacamole/noauth-config.xml__ avec le contenu suivant (à adapter) :

    :::xml
    <configs>
        <config name="my-rdp-server" protocol="rdp">
            <param name="hostname" value="my-rdp-server-hostname" />
            <param name="port" value="3389" />
        </config>
    </configs>

### Profit!

Il ne reste plus qu'à redémarrer Tomcat et vous devriez maintenant pouvoir accéder à votre serveur RDP sans avoir besoin de vous authentifier dans Guacamole.
