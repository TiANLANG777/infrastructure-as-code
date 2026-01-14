terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

# --- 1. 自动查找镜像 ---
data "openstack_images_image_v2" "ubuntu" {
  name_regex  = "(?i)ubuntu" 
  most_recent = true
  visibility  = "public"
}

# --- 2. 自动查找网络 (关键修改) ---
data "openstack_networking_network_v2" "net" {
  # 正则表达式：
  # 1. (?i) 不区分大小写
  # 2. 匹配 "student" (正确的) 或 "sutdent" (你系统里错的) 或 "net"
  # 这样无论它怎么拼，只要带 "net" 或者那一串字符，都能被抓住！
  name_regex = "(?i)(student|sutdent|net)"
}

# --- 3. 变量定义 ---
variable "flavor_name" { default = "m1.medium" }
variable "key_pair_name" { default = "tianlang-auto-key" }

# --- 4. 创建密钥对 ---
resource "openstack_compute_keypair_v2" "keypair" {
  name       = var.key_pair_name
  public_key = file("tianlang_key.pub") 
}

# --- 5. 创建虚拟机 ---
resource "openstack_compute_instance_v2" "vm" {
  name            = "tianlang-bot-vm"
  image_id        = data.openstack_images_image_v2.ubuntu.id
  flavor_name     = var.flavor_name
  key_pair        = openstack_compute_keypair_v2.keypair.name
  security_groups = ["default"]

  network {
    # 使用搜索到的 ID
    uuid = data.openstack_networking_network_v2.net.id
  }
}

# --- 6. 输出 IP ---
output "vm_ip" {
  value = openstack_compute_instance_v2.vm.access_ip_v4
}