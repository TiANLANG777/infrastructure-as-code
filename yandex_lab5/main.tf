resource "yandex_vpc_network" "lab-net" {
  name = "tianlang-net"
}

resource "yandex_vpc_subnet" "lab-subnet" {
  name           = "tianlang-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.lab-net.id
  v4_cidr_blocks = ["10.128.0.0/24"]
}

resource "yandex_compute_instance" "vm-lab5" {
  name = "tianlang-yandex-vm"

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      # Yandex Cloud Ubuntu 20.04 LTS 镜像 ID
      image_id = "fd87tmbvcv1tdm9o2huv" 
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.lab-subnet.id
    nat       = true # 必须开启，否则 Jenkins 连不上
  }

  metadata = {
    # 已经为你填好了公钥，用户名设为 ubuntu
    ssh-keys = "ubuntu:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC6jYQ9MkfYN5zM6xwXrfw9xBq/KlkBTqaJcXEa8TzRE0DuwNO7+2JONOLA8NWsuiF7VrYsiwqofMILr8s6Vd01gW+qvEiO96d/RCUB3LBy2n+52RmcE/Fm5VApRuFIeulP81aY/OZbHsIDO9EoX7mN/1APReNcXV0dESCaH4KC1Iur9nJwa9PYZv4HeIJq1vGAY5Z2lVMcyBf0Ego6YQrkmJsL4zfJ7Ynr9WUNwgWwR8Mum34xX4CBQi+Ej/NO5bKUVWC5F7LnjArET00WlfS8n1wfqoo2WXqybwU8car2eCccOPCU/PTs7f6KBMGX3XX2g47O0cq8QnE47kji061D ubuntu@lang-tian"
  }
}

variable "yc_key_path" {
  type        = string
  description = "Path to the authorized_key.json provided by Jenkins"
}

output "instance_ip" {
  value = yandex_compute_instance.vm-lab5.network_interface.0.nat_ip_address
}
