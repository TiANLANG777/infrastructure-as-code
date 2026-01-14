terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

# --- 1. 智能搜索镜像 ---
data "openstack_images_image_v2" "ubuntu" {
  # 正则表达式：查找名字里包含 "ubuntu" (不区分大小写) 的镜像
  # 如果你的环境没有 22.04，它会自动找最新的 Ubuntu
  name_regex  = "(?i)ubuntu" 
  most_recent = true
  visibility  = "public"
}

# --- 2. 变量定义 ---
variable "flavor_name" { default = "m1.medium" }
variable "network_name" { default = "students-net" } 
variable "key_pair_name" { default = "tianlang-auto-key" }

# --- 3. 创建密钥对 ---
resource "openstack_compute_keypair_v2" "keypair" {
  name       = var.key_pair_name
  # 读取 Jenkins 现场生成的公钥
  public_key = file("tianlang_key.pub") 
}

# --- 4. 创建虚拟机 ---
resource "openstack_compute_instance_v2" "vm" {
  name            = "tianlang-bot-vm"
  # 使用搜索到的镜像 ID
  image_id        = data.openstack_images_image_v2.ubuntu.id
  
  flavor_name     = var.flavor_name
  key_pair        = openstack_compute_keypair_v2.keypair.name
  security_groups = ["default"]

  network {
    name = var.network_name
  }
}

# --- 5. 输出 IP ---
output "vm_ip" {
  value = openstack_compute_instance_v2.vm.access_ip_v4
}