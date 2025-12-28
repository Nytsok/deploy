# Exécution complète AVEC reboot automatique
ansible-playbook playbook.yml

# Exécution SANS reboot (ignore la section reboot)
ansible-playbook playbook.yml --skip-tags reboot

# Installer uniquement certains composants sans reboot
ansible-playbook playbook.yml --tags docker,zsh --skip-tags reboot
