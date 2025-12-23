sudo sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo tee /etc/apt/trusted.gpg.d/google.asc >/dev/null
sudo apt update
sudo apt full-upgrade -y
sudo apt install tar bzip2 ansible libreoffice openfortivpn obs-studio python3-pip curl python3.12-venv google-chrome-stable -y
curl -fsSL "https://get.docker.com/" | sh
# add the sudo group to the user
sudo usermod -aG docker $(id -u -n)

git clone https://github.com/fsoc106/Exegold /home/user/Exegold
cd /home/user/Exegold
python3 -m pip install --break-system-packages --requirement "requirements.txt"
sudo ln -s "/home/user/Exegold/exegol.py" "/usr/local/bin/exegol"
cd /home/user/mydeploy
ansible-playbook -K playbook.yml
