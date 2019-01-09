#!/bin/bash
# My first script

sudo
echo "Creating setup for Ubuntu - All in 1 script- WARNING - be SUDO !"
sudo apt-add-repository -y  universe
sudo apt-get -y dist-upgrade 
sudo apt-get -y update
sudo apt-get -y install build-essential 

echo "Very low-level installs"
sudo apt-get -y install checkinstall cmake automake autoconf libtool pkg-config libcurl4-openssl-dev intltool libxml2-dev libgtk2.0-dev libnotify-dev libglib2.0-dev libevent-de

echo "Here is the part for desktop usage"
#sudo apt-get -y install open office

echo "Installing Java"
sudo apt-get -y install default-jre
sudo apt-get -y install default-jdk

echo "Useful programs"
sudo apt-get -y install htop
sudo add-apt-repository -y ppa:mystic-mirage/pycharm
sudo add-apt-repository -y ppa:kilian/f.lux
sudo apt-get -y update
sudo snap install pycharm-community --classic
# sudo apt-get -y install fluxgui
# sudo apt-get -y install wireshark
sudo apt-get -y install nautilus-dropbox
sudo apt-get -y install filezilla 
sudo apt-get -y install xournal
sudo apt-get -y install flashplugin-installer

echo "Chrome"
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get -y update
sudo apt-get -y install google-chrome-stable

echo "Firefox"
sudo apt-get -y update
sudo apt-get -y install firefox

echo "Photo and video softwares - "
sudo add-apt-repository -y ppa:videolan/stable-daily
sudo apt-get -y update
sudo apt-get -y install shotwell
sudo apt-get -y install gimp 

echo "Sublime Text and associating all text files to sublime text2"

wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
sudo apt-get install apt-transport-https
 
# Si vous souhaitez installer la version stable :
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update && sudo apt-get install sublime-text

#sudo add-apt-repository -y ppa:webupd8team/sublime-text-2 && sudo apt-get update && sudo apt-get -y install sublime-text
sudo sed -i 's/gedit.desktop/sublime-text-3.desktop/g' /etc/gnome/defaults.list  

echo "If you want Number Lock turned on when Ubuntu starts"
sudo apt-get -y install numlockx
sudo sed -i 's|^exit 0.*$|# Numlock enable\n[ -x /usr/bin/numlockx ] \&\& numlockx on\n\nexit 0|' /etc/rc.local

echo "Privacy please"
sudo add-apt-repository -y ppa:nerdherd/cloud && sudo apt-get update
sudo apt-get -y install tor-browser
sudo apt-get -y install tor

echo "Install Terminator"
sudo apt-get -y install terminator

echo "Modifying themes"
sudo apt-get -y install unity-tweak-tool

echo "Apps to investigate"
echo "Backup - http://www.code42.com/crashplan/"
echo "Windows emulator - https://appdb.winehq.org/  -  https://www.virtualbox.org/"

echo "Getting to the end of it"
sudo apt-get -y update

echo "Done"
