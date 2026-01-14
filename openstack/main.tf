terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

# --- 1. 自动查找镜像 (这个支持正则，保留) ---
data "openstack_images_image_v2" "ubuntu" {
  name_regex  = "(?i)ubuntu" 
  most_recent = true
  visibility  = "public"
}

# --- 2. 查找网络 (这个不支持正则，必须精确匹配) ---
data "openstack_networking_network_v2" "net" {
  # 直接使用你确认过的那个名字 (带拼写错误的那个)
  name = "sutdents-net"
}

# --- 3. 变量定义 ---
variable "flavor_name" { default = "m1.medium" }
variable "key_pair_name" { default = "tianlang-auto-key" }

# --- 4. 创建密钥对 (读取 Jenkins 现场生成的公钥) ---
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
    # 使用找到的网络 UUID
    uuid = data.openstack_networking_network_v2.net.id
  }
}

# --- 6. 输出 IP ---
output "vm_ip" {
  value = openstack_compute_instance_v2.vm.access_ip_v4
}