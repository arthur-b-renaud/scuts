echo 'Installing theme and icons for Ubuntu'
sudo apt-add-repository ppa:numix/ppa -y 
sudo apt-add-repository ppa:tista/adapta -y  
sudo apt-get -y update  
sudo apt -y install adapta-gtk-theme  
sudo apt-get -y install numix-icon-theme-circle
