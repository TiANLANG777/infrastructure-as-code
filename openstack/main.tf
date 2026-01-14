terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

# 这里的变量通常由 Jenkins 注入，或者使用默认值
variable "image_name" { default = "ubuntu-22.04" } 
variable "flavor_name" { default = "m1.medium" }
variable "network_name" { default = "students-net" } # 注意检查这里是不是 students-net
variable "key_pair_name" { default = "tianlang-key" }

resource "openstack_compute_keypair_v2" "keypair" {
  name       = "tianlang-auto-key"       # 改个名字确保不冲突
  public_key = file("tianlang_key.pub")  # ✅ 正确：读取当前目录下自动生成的公钥
}

resource "openstack_compute_instance_v2" "vm" {
  name            = "tianlang-bot-vm"
  image_name      = var.image_name
  flavor_name     = var.flavor_name
  key_pair        = openstack_compute_keypair_v2.keypair.name
  security_groups = ["default"]

  network {
    name = var.network_name
  }
}

output "vm_ip" {
  value = openstack_compute_instance_v2.vm.access_ip_v4
}