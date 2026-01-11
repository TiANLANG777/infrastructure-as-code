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
  name        = "tianlang-yandex-vm-v5" # 再次改名以防万一
  platform_id = "standard-v2"          # 强制物理机架构变更，这会强制触发重建

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      # 使用上面 data 模块动态获取的镜像 ID
      image_id = data.yandex_compute_image.ubuntu.id
      type     = "network-hdd"
      size     = 20
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.lab-subnet.id
    nat       = true # 开启公网 IP，供 Jenkins/Ansible 连接
  }

  metadata = {
    # 你的 SSH 公钥，用于自动化登录
    ssh-keys = "ubuntu:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC6jYQ9MkfYN5zM6xwXrfw9xBq/KlkBTqaJcXEa8TzRE0DuwNO7+2JONOLA8NWsuiF7VrYsiwqofMILr8s6Vd01gW+qvEiO96d/RCUB3LBy2n+52RmcE/Fm5VApRuFIeulP81aY/OZbHsIDO9EoX7mN/1APReNcXV0dESCaH4KC1Iur9nJwa9PYZv4HeIJq1vGAY5Z2lVMcyBf0Ego6YQrkmJsL4zfJ7Ynr9WUNwgWwR8Mum34xX4CBQi+Ej/NO5bKUVWC5F7LnjArET00WlfS8n1wfqoo2WXqybwU8car2eCccOPCU/PTs7f6KBMGX3XX2g47O0cq8QnE47kji061D ubuntu@lang-tian"
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
