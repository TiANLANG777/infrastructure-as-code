resource "openstack_compute_instance_v2" "k8s_node" {
  name            = "tianlang-k8s-master"
  image_name      = "Ubuntu 22.04"
  flavor_name     = "m1.medium"
}
