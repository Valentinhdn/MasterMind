# MasterMind — Python GUI Edition

Un jeu **MasterMind** moderne et élégant réalisé en **Python** avec **PySide6 (Qt)**.  
Jouez en local à la célèbre énigme de logique où vous devez **deviner la combinaison secrète de couleurs** en un nombre limité d’essais.

---

## Fonctionnalités

- Interface graphique **moderne et fluide** (avec PySide6)  
- **Animations, dégradés et effets visuels** façon jeu vidéo  
- Palette de **6 couleurs** par défaut, entièrement personnalisable  
- **Historique des essais** avec affichage clair des pions :
  - 🟢 **Vert** = bonne couleur et bien placée  
  - 🟡 **Jaune** = bonne couleur mais mauvaise position  
- Affichage **graphique de la combinaison secrète** à la fin de la partie  
- **Raccourcis clavier** :
  - `1–6` : sélection rapide d’une couleur  
  - `Entrée` : valider un essai  
  - `Backspace` : effacer la dernière couleur  
- Boutons **Nouvelle partie**, **Valider**, **Abandonner**  
- Option **Indice** : révèle visuellement une couleur correcte 🕵️‍♂️

---

## Règles du jeu

1. Une combinaison secrète de 4 couleurs est générée aléatoirement.  
2. À chaque tour, vous proposez une combinaison.  
3. Le jeu vous donne des indices :
   - 🟢 Une couleur bien placée.
   - 🟡 Une couleur correcte mais mal placée.  
4. Trouvez la combinaison avant d’épuiser vos 10 essais !

---

## Installation

Assurez-vous d’avoir **Python 3.9+** installé.

```bash
git clone https://github.com/Valentinhdn/MasterMind.git
cd MasterMind
pip install PySide6
```

## Compiler en .exe

Dans un terminal, entrer la commande suivante : 
```bash
python3 -m PyInstaller --onefile --windowed main.py
```
### Pour ajouter un logo à l'app :
```bash
python3 -m PyInstaller --onefile --windowed --icon=MasterMind.ico main.py

```


