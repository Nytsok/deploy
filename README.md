# Exécution complète AVEC reboot automatique
ansible-playbook -K playbook.yml

# Exécution SANS reboot (ignore la section reboot)
ansible-playbook -K playbook.yml --skip-tags reboot

# Installer uniquement certains composants sans reboot
ansible-playbook -K playbook.yml --tags docker,zsh --skip-tags reboot
