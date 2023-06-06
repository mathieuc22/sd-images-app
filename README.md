# SD Images

Ce projet est une galerie qui permet de gérer les images générées avec Stable Diffusion. Ce README contient des instructions pour installer, exécuter et déployer l'application.

## Prérequis

- Python 3.7 ou supérieur
- Git (optionnel, pour cloner le dépôt)

## Installation

1. Clonez ce dépôt (ou téléchargez-le manuellement) :

```
git clone https://github.com/mathieuc22/sd-images-app.git
```

2. Accédez au répertoire du projet :

```
cd sd-images-app
```

3. Créez un environnement virtuel pour isoler les dépendances de votre projet :

```
python -m venv venv
```

4. Activez l'environnement virtuel :

- Sous Linux et macOS :

```
source venv/bin/activate
```

- Sous Windows :

```
venv\Scripts\activate
```

5. Installez les dépendances :

```
pip install -r requirements.txt
```

## Utilisation

1. Exécutez l'application via le script de démarrage :

```
python run.py
```

2. Accédez à l'accueil :

```
http://127.0.0.1:5000/
```

## Déploiement

Pour déployer cette application sur un serveur ou un service cloud, suivez les instructions spécifiques à la plateforme choisie.

## Licence

Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.
