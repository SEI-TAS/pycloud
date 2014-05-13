__author__ = 'jdroot'

import libvirt

# URI used to connect to the local hypervisor.
_HYPERVISOR_URI = "qemu:///session"
_hypervisor = None


################################################################################################################
# Returns the hypervisor connection and will auto connect if the connection is null
################################################################################################################
def hypervisor():
    global _hypervisor
    if not _hypervisor:
        _hypervisor = libvirt.open(_HYPERVISOR_URI)
    return _hypervisor


def get_virtual_machine(uuid):
    return hypervisor().lookupByUUIDString(uuid)


################################################################################################################
# Helper to convert normal uuid to string
################################################################################################################
def uuidstr(rawuuid):
    hx = ['0', '1', '2', '3', '4', '5', '6', '7',
          '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    uuid = []
    for i in range(16):
        uuid.append(hx[((ord(rawuuid[i]) >> 4) & 0xf)])
        uuid.append(hx[(ord(rawuuid[i]) & 0xf)])
        if i == 3 or i == 5 or i == 7 or i == 9:
            uuid.append('-')
    return "".join(uuid)


################################################################################################################
# Will destroy all virtual machines that are running
################################################################################################################
def destroy_all_vms():
    print 'Shutting down all running virtual machines:'
    vm_ids = hypervisor().listDomainsID()
    for vm_id in vm_ids:
        print '\tShutting down \'VM-%s\'' % uuidstr(vm.UUID())
        vm = hypervisor().lookupByID(vm_id)
        vm.destroy()
    print 'All machines shutdown'