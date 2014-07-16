# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
Vagrant::Config.run do |config|
  # Base box to build off, and download URL for when it doesn't exist on the user's system already
  config.vm.box = "chembiocrunch"
  #v 0.1.0 box URL config.vm.box_url = "https://vagrantcloud.com/strets123/centos65/version/1/provider/centos-65.box"
  config.vm.box_url = "file:///home/astretton/vagrant_box_files/package.box"
  # As an alternative to precise32, VMs can be built from the 'django-base' box as defined at
  # https://github.com/torchbox/vagrant-django-base , which has more of the necessary server config
  # baked in and thus takes less time to initialise. To go down this route, you will need to build
  # and host django-base.box yourself, and substitute your own URL below.
  #config.vm.box = "django-base-v2.1"
  #config.vm.box_url = "http://vmimages.torchbox.com/django-base-v2.1.box"  # Torchbox-internal URL to django-base.box
  
  # Boot with a GUI so you can see the screen. (Default is headless)
  # config.vm.boot_mode = :gui
  
  # Assign this VM to a host only network IP, allowing you to access it
  # via the IP.
  # config.vm.network "33.33.33.10"
  
  # Forward a port from the guest to the host, which allows for outside
  # computers to access the VM, whereas host only networking does not.
  config.vm.forward_port 8000, 8111
  
  # Share an additional folder to the guest VM. The first argument is
  # an identifier, the second is the path on the guest to mount the
  # folder, and the third is the path on the host to the actual folder.
  config.vm.share_folder "project", "/home/vagrant/chembiocrunch", "."
  
  # Enable provisioning with a shell script.
  config.vm.provision :shell, :path => "etc/install/install.sh", :args => "chembiocrunch"
end