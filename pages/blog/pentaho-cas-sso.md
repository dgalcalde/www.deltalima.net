title: Pentaho + Authentification CAS
layout: blog_post
tags:
- sécurité
- pentaho
- CAS
published_date: 2012-11-09
links:
- name: Pentaho
  href: http://www.pentaho.com/
- name: CAS
  href: http://www.jasig.org/cas
attachments:
- InstallCert.java
- spring-security-cas-client-2.0.7.RELEASE.jar
- cas-client-core-3.2.1.jar
- applicationContext-spring-security-cas.xml
- applicationContext-spring-security-cas.properties


Dans cet article, nous allons voir comment utiliser le système d'authentification [CAS (Central Authentication Service)](http://www.jasig.org/cas) avec l'application [Pentaho](http://www.pentaho.com/).

Avant d'entrer dans le vif du sujet, juste deux mots sur CAS : c'est un système de [SSO](http://fr.wikipedia.org/wiki/Authentification_unique) pour les applications web. Il permet aux utilisateurs de s'authentifier une seule fois, puis d'être reconnus automatiquement sur toutes les applications web branchées sur CAS. Si vous l'utilisez, ce sont vos utilisateurs qui vous diront merci : une seule authentification, un seul identifiant et un seul mot de passe.

Quant à Pentaho, si vous êtes arrivés sur cette page c'est que vous le connaissez sûrement déjà. Sinon, c'est une application web de [Business Intelligence](http://fr.wikipedia.org/wiki/Business_Intelligence).

<!-- BODY -->

### Principe

CAS, comme son nom l'indique, est un service d'authentification. Il ne gère pas du tout la partie autorisation qui restera à la charge de Pentaho. Et comme vous connaissez bien Pentaho, vous savez que, dans la configuration par défaut, les autorisations se gèrent dans la console d'administration : on affecte des rôles à des utilisateurs.

- authentification avec CAS : permet de connaitre l'utilisateur connecté, la seule information qu'on aura sera le login de l'utilisateur
- autorisation avec Pentaho : le login récupéré avec CAS doit correspondre à un utilisateur connu de Pentaho auquel on aura associé un ou plusieurs rôles dans la console d'administration

Et donc, pour qu'un utilisateur ait accès à Pentaho, il doit réunir les deux conditions suivantes :

- être authentifié avec CAS
- avoir au minimum le rôle *Authenticated* dans Pentaho

### Ajout du certificat dans la JVM

Pendant la phase d'authentification, notre Pentaho va dialoguer avec le serveur CAS (entre autre pour valider un ticket et connaitre le login de l'utilisateur). Pour des raisons évidentes de sécurité, ces échanges se font exclusivement en HTTPS (ne cherchez pas à le faire fonctionner en HTTP, vous allez vous faire jeter comme un malpropre).

Vous connaissez tous le protocole HTTPS, ça fonctionne à base de certificats et de chaines de confiance. Et justement, pour que notre Pentaho puisse faire confiance au serveur CAS, on va ajouter à la JVM de Pentaho le certificat du serveur CAS.

Alors, pour faire ça, vous avez la solution compliquée avec les outils comme [OpenSSL](http://www.openssl.org/docs/apps/openssl.html) et [keytool](http://docs.oracle.com/javase/6/docs/technotes/tools/solaris/keytool.html) pour récupérer, transformer et ajouter le certificat. Ou sinon, la solution simple avec une petite appli Java kifaitou. Oui, rassurez-vous, on va choisir la deuxième solution. :)

Cette petite appli merveilleuse, c'est un simple fichier Java qui se nomme [InstallCert.java](http://code.google.com/p/java-use-examples/source/browse/trunk/src/com/aw/ad/util/InstallCert.java).

    ::bash
    wget http://java-use-examples.googlecode.com/svn/trunk/src/com/aw/ad/util/InstallCert.java
    javac InstallCert.java
    java InstallCert mon-serveur-cas.ma-petite-entreprise.fr
      [accepter les choix par défaut]

Ceci va créer un fichier *jssecacerts* dans le dossier actuel. Il ne reste plus qu'à copier ce fichier dans l'arborescence de votre JDK.

    cp jssecacerts $JAVA_HOME/jre/lib/security/cacerts

Et voilà, ça c'est fait. On peut passer à la suite.


### Installer les JAR pour CAS

Il y a deux JARs à installer dans Pentaho :

- [spring-security-cas-client-2.0.7.RELEASE.jar](/static/spring-security-cas-client-2.0.7.RELEASE.jar) : pour ajouter la gestion de CAS au [framework Spring](http://www.springsource.org). Attention, pour Pentaho 4.5.0, il faut récupérer le JAR de la version 2.0.7 de Spring. Pour les autres versions de Pentaho, je vous laisse vérifier.
- [cas-client-core-3.2.1.jar](/static/cas-client-core-3.2.1.jar) : le [client CAS Java](http://www.jasig.org/cas/client-integration) issu du projet [Jasig](http://www.jasig.org/).

Une fois récupérés, il faut placer ces deux fichiers dans le dossier *biserver-ce/tomcat/webapps/pentaho/WEB-INF/lib/*.


### Fichiers de configuration

On ajoute le fichier XML [*applicationContext-spring-security-cas.xml*](/static/applicationContext-spring-security-cas.xml) dans le dossier *biserver-ce/pentaho-solutions/system/*

On crée le fichier *applicationContext-spring-security-cas.properties* dans le dossier *biserver-ce/pentaho-solutions/system/* avec le contenu suivant :

    ::properties
    # URL of your CAS server
    cas.server_url=https://my-cas.somewhere.net

    # URL of your Pentaho server
    cas.pentaho_url=http://the-pentaho-server.elsewhere.com/pentaho


Et on édite le fichier *biserver-ce/pentaho-solutions/system/pentaho-spring-beans.xml* pour charger notre fichier de configuration CAS :

    ::xml
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE beans PUBLIC "-//SPRING//DTD BEAN//EN" "http://www.springsource.org/dtd/spring-beans.dtd">
    <beans>
        <import resource="pentahoSystemConfig.xml" />
        <import resource="adminPlugins.xml" />
        <import resource="systemListeners.xml" />
        <import resource="sessionStartupActions.xml" />
        <import resource="applicationContext-spring-security.xml" />
        <import resource="applicationContext-spring-security-cas.xml" />
        <import resource="applicationContext-common-authorization.xml" />
        <import resource="applicationContext-spring-security-hibernate.xml" />
        <import resource="applicationContext-pentaho-security-hibernate.xml" />
        <import resource="pentahoObjects.spring.xml" />
    </beans>

Attention, l'ordre est important, il faut que l'import de *applicationContext-spring-security-cas.xml* soit entre *applicationContext-spring-security.xml* et *applicationContext-common-authorization.xml*.


Et voilà, tout est en place, il ne reste plus qu'à redémarrer Pentaho et à tester


### Au secours, ça marche pas !

Oui, c'est possible, c'est assez capricieux à mettre en place et on peut se louper facilement. Malheureusement, je n'ai pas de réponse toute faite à vous donner, juste quelques pistes de recherche :

- vérifier que vous avez bien ajouté le rôle *Authenticated* à votre utilisateur dans la console d'administration
- aller faire un tour dans les logs de Pentaho et de CAS
- si vous n'avez rien dans les logs, il faut passer [l'authentification en DEBUG](http://wiki.pentaho.com/display/ServerDoc2x/Turning+on+Security+Logging) pour avoir un maximum d'informations (et bon courage parce que ça va cracher pas mal de lignes de log...)


### Et pour les clients lourds ?

Bonne question !

Alors, comment ça se passe pour la publication de rapports depuis un client lourd ? C'est simple : comme avant, rien n'a changé.

CAS est un système d'authentification *uniquement* pour les applications web, il ne fonctionne pas pour tout ce qui est en dehors de votre navigateur. Et donc, pour la publication depuis un client lourd, Pentaho authentifiera l'utilisateur comme si CAS n'était pas présent, en utilisant votre backend préféré (hibernate, ldap, jdbc, etc.).


