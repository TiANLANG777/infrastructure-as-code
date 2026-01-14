pipeline {
    agent { label 'langtian' } # 确保这里和你之前的 Label 一致，通常是 l1 或 build-node

    environment {
        ANSIBLE_HOST_KEY_CHECKING = "False"
        SSH_KEY_PATH = "/home/ubuntu/id_rsa_elk_tf" # 参考同学的路径 [cite: 1]
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // --- 任务 2: 部署到 Yandex K8s ---
        stage('Build & Push Image (For K8s)') {
            steps {
                script {
                    // 构建镜像用于 K8s
                    sh 'docker build -t 192.168.199.142:5000/tianlang-app:latest .'
                    sh 'docker push 192.168.199.142:5000/tianlang-app:latest'
                }
            }
        }

        stage('Deploy to Yandex K8s') {
            steps {
                // 这里复用你原来的 Yandex Terraform 逻辑，假设在 yandex_lab5 文件夹
                dir('yandex_lab5') {
                    withCredentials([file(credentialsId: 'tianlang', variable: 'MY_KEY')]) {
                        sh 'terraform init'
                        sh 'terraform apply -var=yc_key_path=$MY_KEY -auto-approve'
                    }
                }
                // 更新 K8s
                sh 'kubectl apply -f deployment.yaml'
                // 强制重启 Pod 以拉取最新镜像
                sh 'kubectl rollout restart deployment/tianlang-app'
            }
        }

        // --- 任务 1: 部署到 OpenStack ---
        stage('OpenStack: Provision VM') {
            steps {
                dir('openstack') {
                    sh '''
                        # 使用同学的脚本加载凭证 [cite: 7]
                        . /home/ubuntu/openrc-jenkins.sh
                        
                        # 清理旧环境 (如果有)
                        terraform init
                        terraform apply -auto-approve
                    '''
                }
            }
        }

        stage('OpenStack: Wait for SSH') {
            steps {
                script {
                    // 获取 OpenStack VM 的 IP [cite: 12]
                    def vmIp = sh(script: "cd openstack && terraform output -raw vm_ip", returnStdout: true).trim()
                    echo "OpenStack VM IP: ${vmIp}"
                    
                    // 等待 SSH 启动 [cite: 13, 14, 15]
                    sh """
                        for i in \$(seq 1 30); do
                            if nc -z -w 5 ${vmIp} 22; then
                                echo "SSH is UP!"
                                exit 0
                            fi
                            echo "Waiting for SSH..."
                            sleep 10
                        done
                        exit 1
                    """
                }
            }
        }

        stage('OpenStack: Deploy App (Ansible)') {
            steps {
                script {
                    def vmIp = sh(script: "cd openstack && terraform output -raw vm_ip", returnStdout: true).trim()
                    
                    // 生成 Ansible Inventory [cite: 23]
                    sh """
                        mkdir -p ansible
                        echo "[openstack_vm]" > ansible/inventory.ini
                        echo "${vmIp} ansible_user=ubuntu ansible_ssh_private_key_file=${SSH_KEY_PATH}" >> ansible/inventory.ini
                    """
                    
                    // 运行 Playbook
                    sh 'ansible-playbook -i ansible/inventory.ini ansible/playbook.yml'
                }
            }
        }
    }
}