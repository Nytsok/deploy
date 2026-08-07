# Barre de tâches
<img width="1174" height="76" alt="image" src="https://github.com/user-attachments/assets/5aadd0ca-bfa9-49e0-8e5b-f422c47d12cb" />

# Exécution complète AVEC reboot automatique (interactif)
ansible-playbook -K playbook.yml

# Exécution complète en mode NON-INTERACTIF (CI/cron) — pas de pause avant reboot
ansible-playbook -K playbook.yml -e auto_confirm=true

# Exécution SANS reboot (ignore la section reboot)
ansible-playbook -K playbook.yml --skip-tags reboot

# Installer sans exegold
ansible-playbook -K playbook.yml -e install_exegold=false

# Appliquer uniquement les couleurs du terminal
ansible-playbook -K playbook.yml --tags terminal

# Purger le trousseau GNOME (destructif, opt-in explicite)
ansible-playbook -K playbook.yml --tags keyring-wipe

# Notes importantes

- **Exécution LOCALE uniquement.** Le playbook redémarre NetworkManager et applique
  `autoconnect=off` sur tous les profils. Lancé via SSH il tuerait la session.
- **Après reboot, aucune connexion active.** Volontaire : anti-corrélation +
  pas d'auto-join des réseaux connus. Établir la connexion manuellement.
- **Hostname remplacé par `ubuntu`.** Empêche toute fuite d'identifiant unique.
- **Balises Canonical / vendeurs neutralisées** (motd-news, apt-daily,
  fwupd-refresh, connectivity-check). Les mises à jour restent possibles à la
  demande via l'alias `update` du shell.
