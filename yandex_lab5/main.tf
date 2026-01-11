resource "yandex_compute_instance" "vm-lab5" {
  name = "tianlang-yandex-vm"

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      image_id = "fd87tmbvcv1tdm9o2huv" # Ubuntu 20.04 LTS 镜像ID
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.lab-subnet.id
    nat       = true # 必须开启，否则 Jenkins 和 Ansible 连不上
  }

  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}" # 替换为你的公钥内容
  }
}

resource "yandex_vpc_network" "lab-net" {}

resource "yandex_vpc_subnet" "lab-subnet" {
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.lab-net.id
  v4_cidr_blocks = ["10.128.0.0/24"]
}
