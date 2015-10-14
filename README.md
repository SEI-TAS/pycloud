# pycloud
pycloud is the Python-based Cloudlet Server component of KD-Cloudlet, an infrastructure for VM-based cyber-foraging. The three main components of pycloud are:
* Cloudlet API: runtime component that manages computation offload requests from mobile devices. It includes capabilities to provide cloudlet metadata to cloudlet clients for use in cloudlet selection algorithms.
* Cloudlet Manager: web-based application for visualizing and managing Service VMs on a cloudlet
    * Service VM creation, edit and deletion
    * Service VM import and export
    * Service VM instance start, stop and migration
    * Cloudlet-ready app repository (i.e., app store)
* Discovery Service: cloudlet broadcast mechanism based on zeroconf

Cloudlets are discoverable, generic, stateless servers located in single-hop proximity of mobile devices, that can operate in disconnected mode and are virtual-machine (VM) based to promote flexibility, mobility, scalability, and elasticity. In our implementation of cloudlets, applications are statically partitioned into a very thin client that runs on the mobile device and a computation-intensive Server that runs inside a Service VM. Read more about cloudlets at http://sei.cmu.edu/mobilecomputing/research/tactical-cloudlets/.

KD-Cloudlet comprises a total of 7 GitHub projects:

* pycloud (Cloudlet Server)
* cloudlet-client (Cloudlet Client)
* client-lib-android (Library for Cloudlet-Ready Apps)
* client-lib (Java REST Client Library)
* android-logger (SLF4J Logger for Android)
* speech-server (Test server: Speech Recognition Server based on Sphinx)
* speech-android (Test client: Speech Recognition Client)

Building and Installation information in https://github.com/SEI-AMS/pycloud/wiki. 

# Project Contents

 * debian/: files needed to create a .deb installer.
 * discovery/: configuration files to enable Cloudlet discovery through avahi-daemon.
 * libusb/: configuration files needed to enable USB communication.
 * pycloud/: the actual code for the Cloudlet Manager and API.
 * radius/: configuration files needed for FreeRADIUS to auto-reload when certain configurations change.
 * scripts/: scripts for setting up the environment for development. full_dev_setup.sh is the main one. Execute this
             way from inside the scripts/ folder: "bash full_dev_setup.sh" (do NOT call with sudo).
             NOTE: these scripts assume Ubuntu 14.0.4 or higher is being used.
 * testing/: some test scripts.
 * tls/: scripts to set up a CA and to set up scripts for libvirt.
 * upstart/: Upstart script configurations for the Manager and API services.
 * bootstrap.py: script for starting the server while developing (called by bash script below).
 * dev_tips.txt: some hints for developing parts of the system.
 * development_api.ini: config file used while developing the API.
 * development_manager.ini: config file used while developing the Manager. 
 * pycloud_api.ini: API config file used when installing the server.
 * pycloud_manager.ini: Manager config file used when installing the server. 
 * LICENSE: license for this software.
 * MANIFEST.in, requirements.txt and setup.py: config files for creating the egg for this python package.
 * README.md this file.
 * start_dev_api.sh: script to start API when developing, after env has been set up.
 * start_dev_manager.sh: script to start Manager when developing, after env has been set up.
 
 Packaging and installation instructions are available at https://github.com/SEI-AMS/pycloud/wiki

