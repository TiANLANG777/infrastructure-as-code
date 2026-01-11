# 1. 动态获取最新的 Ubuntu 20.04 镜像，避免 Image ID 失效报错
data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2004-lts"
}

# 2. 创建 VPC 网络
resource "yandex_vpc_network" "lab-net" {
  name = "tianlang-net"
}

# 3. 创建子网
resource "yandex_vpc_subnet" "lab-subnet" {
  name           = "tianlang-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.lab-net.id
  v4_cidr_blocks = ["10.128.0.0/24"]
}

# 4. 创建虚拟机实例
resource "yandex_compute_instance" "vm-lab5" {
  name        = "tianlang-vm-final" 
  platform_id = "standard-v2"
  
  # 新增这一行，允许 Terraform 停止机器进行更新
  allow_stopping_for_update = true

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      # 如果想强制重建，可以把 size 改一下，比如从 20 改成 21
      size     = 25 
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.lab-subnet.id
    nat       = true # 开启公网 IP，供 Jenkins/Ansible 连接
  }

  metadata = {
    # 注意：用户名 ubuntu 后面有一个冒号，然后紧跟公钥
    ssh-keys = <<-EOF
      ubuntu:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDIOgHnFg2dD1A0GjruRV+kw/EYWh3soEtgFwELAKkKv8iHO6C98cakh6OLDkiLdWy7ZtpAqfE1Lue7cvQcLAwO/oCso8Ry3BqxgFqrfwRq9I3ZNvigjBY2+DsegtmOm6OkypM3bAis8CScsDZxLrzn/hMkCUKKIwbBEh9Q95cbfJcK5KLjMx6AddUwddrKbarbr/5VBeFP3wKAWgh70CZUjW16lcHzVy0x901TZXziii5umme3aiKMOLM2C+3ero4A6dldzEnV9RTNOzmcQncq51SmrFohQFYMme3OSeueNKrH4se8PL02cn3OomnAIL77obgSmmADUWAOUK2Pn7Yv
    EOF
  }
}

# 5. 定义变量（由 Jenkins 传入密钥路径）
variable "yc_key_path" {
  type        = string
  description = "Path to the authorized_key.json provided by Jenkins"
}

# 6. 输出虚拟机的公网 IP（方便在 Jenkins 日志中查看）
output "instance_ip" {
  value = yandex_compute_instance.vm-lab5.network_interface.0.nat_ip_address
}
