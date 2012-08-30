title: Stripe CTF 2.0
layout: blog_post
tags:
- sécurité
published_date: 2012-08-30
links:
- name: Stripe CTF
  href: https://stripe-ctf.com


[Stripe](https://stripe.com/) a organisé le concours [Capture The Flag 2.0](https://stripe-ctf.com), c'est un challenge dans le domaine de la sécurité des applications web. Le concours est divisé en 9 niveaux (de 0 à 8) dont le but est de trouver un mot de passe à chaque niveau permettant de passer au suivant. C'est la deuxième édition de Stripe CTF (d'où le 2.0), la première s'étant déroulée en début d'année autour de technos beaucoup plus bas niveau (et autrement plus difficile).

Stripe CTF 2.0 est maintenant fini. Si vous n'êtes pas allés jusqu'au bout, les niveaux restant sont définitivement bloqués. Pour ma part, je suis allé jusqu'au dernier niveau sur lequel je suis resté bloqué (et je n'aurai pas mon t-shirt :p).

<span class="center">![Stripe CTF 2.0 final results](/static/img/stripe-ctf-2.0-results.png "Stripe CTF 2.0 final results")</span>

Si les premiers niveaux se passent assez facilement, on arrive rapidement sur des énigmes plutôt tordues qui demandent plus de réflexion. Par exemple, j'ai perdu pas mal de temps à trouver une solution pour écrire du JavaScript sans guillemets simple ou double (les caractères **'** et **"**).

Niveau technos utilisées, on trouve les classiques PHP, Python, Ruby, JavaScript et SQL. Pour les exploits des premiers niveaux, ce sont des techniques connues comme du [SQL injection](http://en.wikipedia.org/wiki/SQL_injection), des [XSS](http://en.wikipedia.org/wiki/Cross-site_scripting) et l'upload de scripts PHP directement dans le DocumentRoot. Par la suite, ça se corse un peu avec des trucs plus tordus où il faut jouer avec deux serveurs différents (oui, level 5, je pense à toi !) ou utiliser les faiblesses d'une [fonction de hashage](http://en.wikipedia.org/wiki/Hash_function). Bref, le challenge était très intéressant, j'ai même appris quelques nouvelles techniques (comme le [padding](http://en.wikipedia.org/wiki/Padding_%28cryptography%29) de signature SHA1). J'en garde un excellent souvenir, vivement le prochain !

Effet secondaire, je suis encore plus parano qu'avant ! Si à la lecture du code des premiers niveaux on voit rapidement la faille, il n'est pas évident de les trouver dans les derniers niveaux. Une simple lecture ne suffit pas, il faut vraiment entrer dans le code et comprendre les interactions entre les différents composants pour trouver un début de réponse. On cherche, on essaie différentes techniques, on insiste ... on sait qu'il y a une faille et on doit la trouver. Et là, je vous le demande, passerait-on autant de temps à examiner du code censé être correct pour trouver des failles ? Pas forcément... En tout cas, moi je vous laisse, j'ai quelques lignes de code à vérifier :)

