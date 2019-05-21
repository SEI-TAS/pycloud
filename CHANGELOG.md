# Change Log

## [3.0.3] - 2019-05-21

### Fixed
- Updated dead and buggy pycrypto lib to newer pycryptodome, which uses same namespaces and objects.
- Updated M2Crypto and Requests versions to avoid vulnerabilities.
- Fixed handling of qemu saved states to support changes in newer qemu versions, where a new header value is used.
- Fixed minor issues in env setup (with libvirt group names and pip warnings).

## [3.0.2] - 2018-04-27
### Fixed
- Updated setup scripts to be compatible with systemd and changes in pip 10.
- Changed VNC connections to ServiceVMs to be local only.

## [3.0.1] - 2018-04-12
### Fixed
- Fixed bug that was preventing importing a CSVM file with a zero-length memory image file.
- Fixed bug in use of nmcli, which changed in version 0.9.10.

## [3.0.0] - 2016-12-28
### Added
- Added support for using Fully-Qualified Domain Names (FQDNs) instead of IP addresses to access Service VMs (SVMs), to allow for easier migration. If enabled, when a new SVM  is started, a FQDN will be returned to the Cloudlet-Ready App, instead of an IP address. If the cloudlet app uses this FQDN to communicate to the Service VM, migration will be transparent. Disabled by default.
- Added a DNS server to handle FQDN resolution, if enabled. Disabled by default.
- Added a Cloudlet Pairing process, similar to the existing Device Pairing, to allow cloudlets to trust each other. This can be later used to migrate device credentials from one cloudlet to another.
- Added a manually-triggered feature to find nearby cloudlet Wi-Fi networks from a cloudlet, to find a migration target.
- Added a new migration message to the migration process that, if security is enabled, requests new credentials for the target cloudlet for devices that will migrate along with a an SVM. This allows devices to end up paired to the target cloudlet where an SVM will be migrated to without following the physical pairing process. Depends on the target cloudlet already trusting the source one through the Cloudlet Pairing process.
- Added generic mailboxes for devices, where a cloudlet can leave a message/command for a device. Devices will constantly poll the cloudlet through a new API request for new messages.
- Added a new mailbox message for devices to notify them when a SVM migration has ocurred, and to deliver to them their new credentials to connect to the cloudlet where the SVM was migrated to.
- Added support for importing a .CSVM file without a saved state/VM info file (.lqs file).
- Tested that OSv-based VMs work properly with the system. Speech repo now has scripts to easliy create an OSv-based SVM as an importable .csvm file.

### Fixed
- Various bug fixes, including several ones related to creation of a new Service VM.
