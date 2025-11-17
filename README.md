# test_agent_ia
Agent IA pour la classification des emails
Développer un agent de traitement automatique de tickets par e-mail








Objectif général
Vous allez développer un agent logiciel capable de :
Lire automatiquement des e-mails contenant des tickets (envoyés via une API Gmail ou toute autre interface fournie).


Analyser et interpréter le contenu de chaque message.


Classer les tickets dans la bonne catégorie.


Mettre à jour un Google Sheet associé au même compte que la boîte mail, en écrivant les informations importantes de chaque ticket dans l’onglet correspondant à sa catégorie.


Cet exercice simule le fonctionnement d’un système professionnel de gestion de tickets automatisé.













Données fournies
Vous disposez d’une boîte mail : 
Identifiants : 
Mail : ticketsdata5@gmail.com
Mot de passe : Azerty12345!
Celle-ci contient 549 e-mails, chacun étant un ticket structuré selon un format spécifique.
 Chaque ticket contient :
un sujet
un contenu (texte du mail)


Ces emails ont été générés pour représenter un large éventail de cas :
Problème technique informatique
Demande administrative
Problème d’accès / authentification
Demande de support utilisateur
Bug ou dysfonctionnement d’un service
Tu dois  aussi répartir les 5 mails sur plusieurs niveaux d’urgence, du plus trivial à l’extrêmement urgent :
Critique : impact majeur, opération impossible, nécessite intervention immédiate
Élevée : impact important, forte gêne, traitement prioritaire
Modérée : gêne notable mais non bloquante
Faible : problème mineur
Anodine : demande simple, aucun enjeu d’urgence

Structure du Google Sheet
Un Google Sheet est associé au même compte que la boîte mail.
Il contient 5 feuilles, chacune correspondant à l’une des catégories de tickets.
Dans chaque feuille, vous devez alimenter automatiquement un tableau comportant les colonnes suivantes :
Sujet
Urgence
Synthèse
(texte)
(Anodine → Critique)
(résumé du mail)



