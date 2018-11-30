
Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/xenial64"
    config.vm.provider "virtualbox" do |vb|
        vb.memory = "1024"
    end
    config.vm.hostname = "staging.engineeringdiplomats.org"
    config.vm.synced_folder ".", "/home/vagrant/workspace", :owner => 'vagrant', :mount_options => ['dmode=775', 'fmode=775']
    config.vm.network "forwarded_port", guest: 8080, host: 8080
    config.vm.network "forwarded_port", guest: 80, host: 80
    config.vm.network "forwarded_port", guest: 443, host: 443
    
end
