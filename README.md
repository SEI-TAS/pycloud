# pycloud
pycloud is the Python-based Cloudlet Server component of KD-Cloudlet, an infrastructure for VM-based cyber-foraging. The three main components of pycloud are:
* Cloudlet Server: runtime component that manages computation offload requests from mobile devices. It includes capabilities to provide cloudlet metadata to cloudlet clients for use in cloudlet selection algorithms.
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
* client-lib
* client-lib-android
* slf-4j-android-logger
* speech-server (Test server: Speech Recognition Server based on Sphinx)
* speech-client (Test client: Speech Recognition Client)
pycloud