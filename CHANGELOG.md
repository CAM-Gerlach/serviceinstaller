# ServiceInstaller Changelog


## Version 0.1.3 (2020-04-23)

Bugfix release to fix various issues:

* Fix issue with timeout being set too short for low-end systems (eg RPi Zero)



## Version 0.1.2 (2020-03-10)

Bugfix release to fix various issues:

* Fix serious bug when filename, services_enable or services_disable is None
* Minor refinements to setup.py
* Ensure full project is pylint-clean and add .pylintrc



## Version 0.1.1 (2019-10-28)

Minor bugfix release to fix a one significant bug on Debian:

* Don't add group name to avoid issues where group doesn't exist, e.g. Debian



## Version 0.1.0 (2019-10-06)

Initial deployed release for Brokkr and Sindri, with the following features:

* Automatically generate service unit file for Systemd
* Reload daemon and enable service
* Enable and disable other services as needed
* Detailed, controllable logging and error handling
* Extensible to other service systems
