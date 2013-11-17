title: "Comment utiliser une image disque"
layout: blog_post
published_date: 2013-11-16
tags:
 - system



Le titre n'étant pas très parlant, et comme je ne trouvais rien de mieux sans faire une longue tirade, on va tout de suite définir de quoi nous allons parler. Une image disque est tout simplement une copie d'un disque (ça peut être un disque dur, ou un DVD, ou ce que vous voulais) dans un fichier. Nous allons voir dans cet article ce qu'il est possible de faire avec une image disque, et surtout comment le faire.

### À quoi ça sert ?

Il existe beaucoup de cas d'utilisation d'une image disque, il faut voir une image disque comme l'équivalent d'un disque dur mais avec l'énorme avantage de tenir dans un fichier. À partir de là, on peut en faire ce qu'on veut.

Il existe toutefois des utilisations courantes des images disques :

- un disque dur pour une machine virtuel
- sauvegarder le contenu d'un disque dur pour archivage
- échanger le contenu d'un disque dur

Par exemple, le projet [Cubian](http://cubian.org/) (Debian pour [Cubieboard](http://cubieboard.org/)) fournit une image disque prête à être installée sur une carte SD. L'image disque contient un bootloader spécifique au Cubieboard, ainsi qu'une partition contenant une Debian. Il suffit de copier l'image disque sur une carte SD et de la mettre dans le Cubieboard, on peut difficilement faire plus simple.


### Créer une image disque

Vu que c'est un fichier comme un autre, n'importe quel outil permettant de créer un fichier fera l'affaire. Il faut juste garder à l'esprit que la taille du fichier est l'équivalent de la taille du disque que l'on souhaite obtenir. Si vous faites un `touch image_disque.img` vous obtenez un disque de taille zéro, ce qui n'est pas très utile... Heureusement, il existe d'autres outils plus efficaces.

Vous connaissez tous la commande `dd`, elle permet d'indiquer le nombre d'octets qui seront copiés vers la destination. En utilisant `/dev/zero` comme source, on peut se créer facilement un fichier rempli de zéros.

    ::shell
    # création d'un fichier de 10Go
    $ dd if=/dev/zero of=image_disque.img bs=1M count=10240
    10240+0 records in
    10240+0 records out
    10737418240 bytes (11 GB) copied, 104,14 s, 103 MB/s

    # on vérifie
    $ ls -lh image_disque.img
    -rw-rw-r--    1 laurent laurent  10G 16 nov.  14:24 image_disque.img

Encore mieux, si votre système de fichiers gère les [sparse files](http://en.wikipedia.org/wiki/Sparse_file), la création devient instantanée.

    ::shell
    # on utilise l'option seek de dd
    $ dd of=image_disque.img bs=10G count=0 seek=1
    0+0 records in
    0+0 records out
    0 bytes (0 B) copied, 4,4632e-05 s, 0,0 kB/s

Si, comme moi, vous trouvez la syntaxe de `dd` pas forcément très clair, il existe `truncate` qui fait exactement la même chose mais avec une syntaxe humainement compréhensible.

    # c'est plus simple non ?
    $ truncate -s 10G image_disque.img

Et voilà, nous avons l'équivalent d'un disque dur de 10Go dans le fichier `image_disque.img`. Et que fait-on avec un disque dur ? On crée des partition.

### Partitionner une image disque

Ça va simple et rapide : on utilise les mêmes outils que pour un disque dur classique.

    ::shell
    # exemple d'utilisation avec fdisk
    # - création d'une partition de 6Go
    # - création d'une seconde partition utilisant le reste des 10Go

    $ fdisk image_disque.img

    Command (m for help): n
    Partition type:
    p   primary (0 primary, 0 extended, 4 free)
    e   extended
    Select (default p):
    Using default response p
    Partition number (1-4, default 1):
    First sector (2048-20971519, default 2048):
    Using default value 2048
    Last sector, +sectors or +size{K,M,G} (2048-20971519, default 20971519): +6G
    Partition 1 of type Linux and of size 6 GiB is set

    Command (m for help): n
    Partition type:
    p   primary (1 primary, 0 extended, 3 free)
    e   extended
    Select (default p):
    Using default response p
    Partition number (2-4, default 2):
    First sector (12584960-20971519, default 12584960):
    Using default value 12584960
    Last sector, +sectors or +size{K,M,G} (12584960-20971519, default 20971519):
    Using default value 20971519
    Partition 2 of type Linux and of size 4 GiB is set

    Command (m for help): w
    The partition table has been altered!

    Syncing disks.

J'ai utilisé `fdisk`, mais rien n'empêche d'utiliser d'autres outils comme `cfdisk` ou `cgdisk` (si vous avez besoin d'une table des partitions au format [GPT](http://en.wikipedia.org/wiki/GUID_Partition_Table)).


### Monter une partition

Autant les deux premières étapes sont simples et peuvent être réalisées avec un utilisateur quelconque (on ne faisait qu'écrire dans un fichier après tout !), autant maintenant il va falloir sortir le compte `root` et bidouiller dans `/dev`. Donc faites attention à ce que vous faites, c'est rapide de se tromper de device dans `/dev` et de perdre le contenu de son disque dur (le vrai, celui où vous avez toute votre vie au format numérique). Mais comme vous faites des sauvegardes, on peut y aller sans remord (euh, vous faites bien des sauvegardes hein ?).

Première chose, pour monter une partition il faut que le noyau la connaisse. En gros, il faut qu'elle apparaisse dans `/proc/partitions`. Pour le moment, elle n'y est pas.

    ::shell
    $ cat /proc/partitions
    major minor  #blocks  name

       8        0  488386584 sda
       8        1     512000 sda1
       8        2  487873536 sda2
      11        0    1048575 sr0

Pour se faire, on va utiliser la commande `partx` qui indique au noyau de lire la table des partitions présente sur un device et d'ajouter les partitions au niveau du noyau. Et comme on a de la chance, `partx` permet de lire soit un device, soit une image disque (chance !).

    ::shell
    # on liste les partitions présentes sur notre image disque
    $ partx -l image_disque.img
    # 1:      2048- 12584959 ( 12582912 sectors,   6442 MB)
    # 2:  12584960- 20971519 (  8386560 sectors,   4293 MB)

Et voilà nos deux partitions créés avec fdisk, il ne reste plus qu'à les ajouter au noyau.

    ::shell
    # ajoute nos deux partitions
    $ partx -a image_disque.img

    # vérification
    $ cat /proc/partitions
    major minor  #blocks  name

       7        0   10485760 loop0
     259        0    6291456 loop0p1
     259        1    4193280 loop0p2
       8        0  488386584 sda
       8        1     512000 sda1
       8        2  487873536 sda2
      11        0    1048575 sr0

Nos deux partitions sont disponibles en tant que `/dev/loop0p1` et `/dev/loop0p2`. Quand `partx` est utilisé sur un fichier classique (notre image disque), il utilise `losetup` pour monter notre image disque en tant que block device dans `/dev` (dans notre cas `/dev/loop0`). Le device `/dev/loop0` est un device particulier qui redirige les I/O vers `image_disque.img`.

    ::shell
    $ losetup
    NAME       SIZELIMIT OFFSET AUTOCLEAR RO BACK-FILE
    /dev/loop0         0      0         0  0 /home/laurent/image_disque.img

Le noyau est maintenant au courant qu'il y a deux partitions dans notre image disque, mais on ne peut pas encore les monter : les partitions ne sont pas formatées.

    ::shell
    # NE PAS SE TROMPER DE DEVICE !!!
    $ mkfs.btrfs /dev/loop0p1

    # NE PAS SE TROMPER DE DEVICE !!!
    $ mkfs.ext4 /dev/loop0p2

C'est presque fini, il ne reste plus qu'à les monter comme des partitions classiques.

    ::shell
    # monte les partitions
    $ mkdir /mnt/p1 /mnt/p2
    $ mount /dev/loop0p1 /mnt/p1
    $ mount /dev/loop0p2 /mnt/p2

    # vérification
    $ df -h
    [...]
    /dev/loop0p1                   6.0G   56K  5.4G   1% /tmp/p1
    /dev/loop0p2                   3.9G  8.0M  3.7G   1% /tmp/p2


### On range tout, c'est fini

Voilà, vous avez monté vos deux partitions, vous pouvez maintenant y ajouter des fichiers. C'est bien, mais comment faire pour tout supprimer ? Si on supprime directement le fichier `image_disque.img`, le noyau ne risque pas d'aimer ça beaucoup (je vous rappelle que les deux partitions sont toujours montées). Pour ne risquer aucune corruption de données dans l'image disque, on va tout simplement refaire toutes les étapes précédentes, mais dans l'ordre inverse.

    ::shell
    # on démonter les deux partitions
    $ umount /mnt/p1
    $ umount /mnt/p2

    # on indique au noyau qu'il peut "oublier" les deux partitions
    $ partx -d /dev/loop0

    # on libère le device /dev/loop0
    $ losetup -d /dev/loop0

Et c'est fini. Le fichier `image_disque.img` contient maintenant deux partitions et les quelques fichiers que vous y avaient placés. Si vous remontez les partitions, les fichiers y seront toujours présents.

### Astuce 1

Il est possible de copier notre image disque sur un device externe (un disque dur ou une clé usb). Si vous avez une clé usb dont la taille est supérieure à la taille de l'image disque, vous pouvez tenter ceci :

    ::shell
    # démontez TOUTES les partitions de la clé usb
    $ umount blabla...

    # copiez l'image disque vers la clé usb
    # ATTENTION :
    #   1. toutes les données de la clé usb seront perdues
    #   2. ne vous trompez pas de device pour la destination `of=/dev/sdX`
    $ dd if=image_disque.img of=/dev/sdX bs=4k ; sync

Une fois la copie terminée, débranchez puis rebranchez la clé et vous y trouverez les deux partitions et leurs contenus.

### Astuce 2

Si vous vous rendez compte que la taille de l'image disque n'est pas bonne (trop grande ou trop petite), il est possible de changer sa taille. L'opération se fait lorsque l'image disque n'est pas utilisée (après un `losetup -d /dev/loop0` par exemple).

Par exemple, pour augmenter sa taille :

    ::shell
    # ajoute 4Go
    $ truncate -s +4G image_disque.img

    # édite la table des partitions - ajoute une nouvelle partition ou change
    # la taille d'une partition déjà présente
    $ fdisk image_disque.img

Pour réduire la taille, c'est un peu plus compliqué. Il faut d'abord réduire les FS, puis les partitions, puis en dernier la taille de l'image disque. C'est trop long pour être présenté ici, il faudrait un article dédié.

Quoiqu'il en soit, dès le moment où on est amené à modifier des partitions, il y a trois règles :

- faire des sauvegardes
- savoir de quoi on parle et être bon en math (pour additionner ou soustraire des octets, des blocks et des secteurs)
- faire des sauvegardes (si si !)
