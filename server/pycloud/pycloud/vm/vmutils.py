__author__ = 'jdroot'

import libvirt

HYPERVISOR_URI = "qemu:///system"

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
    hypervisor = libvirt.open(HYPERVISOR_URI)
    vm_ids = hypervisor.listDomainsID()
    for vm_id in vm_ids:
        vm = hypervisor.lookupByID(vm_id)
        print '\tShutting down \'VM-%s\'' % uuidstr(vm.UUID())
        vm.destroy()
    print 'All machines shutdown'
