glusterweb
==========

Simple Gluster Management UI


## Installation:

glusterfs-web depends on glusterfs-tools

    git clone https://github.com/aravindavk/glusterfs-tools.git
    cd glusterfs-tools
    sudo python setup.py install


    git clone https://github.com/aravindavk/glusterfs-web.git
    cd glusterfs-web
    sudo python setup.py install

Once installed, we need to run the setup to install glusterfs hooks scripts required for monitoring.

    sudo glusternodestate setup

Similarly run cleanup if you need to cleanup/remove all the hooks scripts and database.

    sudo glusternodestate cleanup


NOTE: This is a experimental project and it is not really usable. 
