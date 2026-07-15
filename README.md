# Barre de tâches
<img width="1174" height="76" alt="image" src="https://github.com/user-attachments/assets/5aadd0ca-bfa9-49e0-8e5b-f422c47d12cb" />

# Exécution complète AVEC reboot automatique
ansible-playbook -K playbook.yml

# Exécution SANS reboot (ignore la section reboot)
ansible-playbook -K playbook.yml --skip-tags reboot

# Installer sans exegold
ansible-playbook playbook.yml --skip-tags exegold

# Appliquer uniquement les couleurs du terminal
ansible-playbook -K playbook.yml --tags terminal
