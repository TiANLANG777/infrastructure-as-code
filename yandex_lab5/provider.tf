terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  # 这些 ID 来自于你之前的控制台截图
  service_account_key_file = var.yc_key_path 
  cloud_id                 = "b1g19f5102t4no376gjh"
  folder_id                = "b1g1mbc29v77v98dkloi"
  zone                     = "ru-central1-a"
}
