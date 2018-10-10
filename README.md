# ANPR-Pakistan-Plate
Automatic Number Plate Recognition System on Pakistan Plate.

# Install Libraries 
Ubuntu 16.04 #
python 2.7 #
pip install opencv-python==2.4.9 
sudo apt-get install python-qt4

# Compile Latest Version Openalpr Library
sudo apt-get install libopencv-dev libtesseract-dev git cmake build-essential libleptonica-dev
sudo apt-get install liblog4cplus-dev libcurl3-dev

sudo apt-get install beanstalkd

git clone https://github.com/openalpr/openalpr.git

cd openalpr/src
mkdir build
cd build

cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ..

make
sudo make install



