terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  # 这里的变量 yc_key_path 会由 Jenkins 注入，指向你的 authorized_key.json
  service_account_key_file = var.yc_key_path 
  cloud_id                 = "b1g19f5102t4no376gjh"  # 确认和你截图一致
  folder_id                = "b1g1mbc29v77v98dkloi"  # 确认和你截图一致
  zone                     = "ru-central1-a"         # 建议选这个区
}

variable "yc_key_path" {
  type        = string
  description = "Path to the authorized_key.json"
}
