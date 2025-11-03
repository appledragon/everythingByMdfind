[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Español](README_ES.md)

<img width="3836" height="2026" alt="image" src="https://github.com/user-attachments/assets/d86c3d6b-6fd4-4cfe-b64f-67c465bb3d3c" /><img width="3832" height="2024" alt="image" src="https://github.com/user-attachments/assets/a91d2b13-07ac-4cae-ab33-506f1fa3bca6" />

# Everything by mdfind

Un outil de recherche de fichiers puissant et efficace pour macOS, exploitant le moteur natif Spotlight pour des résultats ultra-rapides.

## Caractéristiques principales

*   **Recherche ultra-rapide :** Utilise l'index Spotlight de macOS pour une recherche de fichiers quasi instantanée.
*   **Options de recherche flexibles :** Recherchez par nom de fichier ou contenu pour localiser rapidement les fichiers dont vous avez besoin.
*   **Filtrage avancé :** Affinez vos recherches avec une variété de filtres :
    *   Plage de taille de fichier (taille minimale et maximale en octets)
    *   Extensions de fichier spécifiques (par exemple, `pdf`, `docx`)
    *   Correspondance sensible à la casse
    *   Options de correspondance complète ou partielle
*   **Recherche spécifique au répertoire :** Limitez votre recherche à un répertoire spécifique pour des résultats ciblés.
*   **Aperçu enrichi :** Prévisualisez divers types de fichiers directement dans l'application :
    *   Fichiers texte avec détection d'encodage
    *   Images (JPEG, PNG, GIF avec support d'animation, BMP, WEBP, HEIC)
    *   Fichiers SVG avec mise à l'échelle et centrage appropriés
    *   Fichiers vidéo avec contrôles de lecture
    *   Fichiers audio
*   **Lecteur multimédia intégré :**
    *   Lecture vidéo et audio avec contrôles standard
    *   Fenêtre de lecteur autonome pour les fichiers multimédia
    *   Mode de lecture continue
    *   Contrôle du volume et option de mise en sourdine
*   **Favoris :** Accès rapide aux recherches courantes :
    *   Fichiers volumineux (>50 Mo)
    *   Fichiers vidéo
    *   Fichiers audio
    *   Images
    *   Archives
    *   Applications
*   **Résultats triables :** Organisez les résultats de recherche par nom, taille, date de modification ou chemin.
*   **Opérations multi-fichiers :** Effectuez des actions sur plusieurs fichiers simultanément :
    *   Sélectionnez plusieurs fichiers à l'aide des touches Shift ou Command (⌘)
    *   Opérations par lots : Ouvrir, Supprimer, Copier, Déplacer, Renommer
    *   Menu contextuel pour des opérations supplémentaires
*   **Interface de recherche multi-onglets :** Travaillez avec plusieurs sessions de recherche simultanément :
    *   Créez de nouveaux onglets pour différentes requêtes de recherche
    *   Fermez, réorganisez et gérez les onglets avec le menu contextuel du clic droit
    *   Résultats de recherche et paramètres indépendants par onglet
    *   Expérience d'onglets similaire à Chrome avec boutons de défilement pour de nombreux onglets
*   **Interface personnalisable :**
    *   6 magnifiques thèmes au choix :
        *   Clair et Sombre (par défaut du système)
        *   Tokyo Night et Tokyo Night Storm
        *   Chinolor Dark et Chinolor Light (couleurs traditionnelles chinoises)
    *   Thématisation de la barre de titre système qui correspond à votre thème sélectionné
    *   Afficher/masquer le panneau d'aperçu
    *   Historique de recherche configurable
*   **Exportation multi-formats :** Exportez les résultats de recherche vers plusieurs formats :
    *   JSON - Format de données structurées
    *   Excel (.xlsx) - Feuille de calcul avec mise en forme
    *   HTML - Format de tableau prêt pour le Web
    *   Markdown - Format compatible documentation
    *   CSV - Format classique à valeurs séparées par des virgules
*   **Chargement paresseux :** Gère efficacement les grands ensembles de résultats en chargeant les éléments par lots au fur et à mesure du défilement.
*   **Glisser-déposer :** Faites glisser les fichiers directement vers des applications externes.
*   **Opérations de chemin :** Copiez le chemin du fichier, le chemin du répertoire ou le nom du fichier dans le presse-papiers.

## Installation

1.  **Prérequis :**
    *   Python 3.6+
    *   PyQt6

2.  **Cloner le dépôt :**

    ```bash
    git clone https://github.com/appledragon/everythingByMdfind
    cd everythingByMdfind
    ```

3.  **Installer les dépendances :**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancer l'application :**

    ```bash
    python everything.py
    ```

## Télécharger l'application pré-compilée

Vous pouvez télécharger l'application macOS prête à l'emploi (.dmg) directement depuis la page [GitHub Releases](https://github.com/appledragon/everythingByMdfind/releases).

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des pull requests ou à ouvrir des issues pour des corrections de bugs, des demandes de fonctionnalités ou des améliorations générales.

## Licence

Ce projet est sous licence Apache License 2.0 - voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.

## Auteur

Apple Dragon

## Version

1.3.7

## Remerciements

*   Merci à l'équipe PyQt6 pour avoir fourni un framework GUI puissant et polyvalent.
*   Inspiration d'autres excellents outils de recherche de fichiers.
