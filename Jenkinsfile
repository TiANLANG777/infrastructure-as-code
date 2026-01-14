pipeline {
    agent { label 'langtian' } 

    environment {
        ANSIBLE_HOST_KEY_CHECKING = "False"
        SSH_KEY_PATH = "/home/ubuntu/id_rsa_elk_tf"
    }

    stages {
        stage('Checkout') {
            steps {
                // Git 拉取代码依然用 SSH 私钥 (tianlang)
                checkout scm
            }
        }

        stage('Build & Push Image (For K8s)') {
            steps {
                script {
                    sh 'docker build -t 192.168.199.142:5000/tianlang-app:latest .'
                    sh 'docker push 192.168.199.142:5000/tianlang-app:latest'
                }
            }
        }

        stage('Deploy to Yandex K8s') {
            steps {
                dir('yandex_lab5') {
                    // ⬇️⬇️⬇️ 重点修改：这里使用了你截图里的凭证 ID 'YC_KEY_FILE'
                    withCredentials([file(credentialsId: 'YC_KEY_FILE', variable: 'MY_KEY')]) {
                        sh 'terraform init'
                        // Terraform 会读取这个 JSON 文件
                        sh 'terraform apply -var=yc_key_path=$MY_KEY -auto-approve'
                    }
                }
                sh 'kubectl apply -f deployment.yaml'
                sh 'kubectl rollout restart deployment/tianlang-app'
            }
        }

        stage('OpenStack: Provision VM') {
            steps {
                dir('openstack') {
                    sh '''
                        # OpenStack 配置保持不变
                        . /home/ubuntu/openrc-jenkins.sh
                        
                        terraform init
                        terraform apply -auto-approve
                    '''
                }
            }
        }

        stage('OpenStack: Wait for SSH') {
            steps {
                script {
                    def vmIp = sh(script: "cd openstack && terraform output -raw vm_ip", returnStdout: true).trim()
                    echo "OpenStack VM IP: ${vmIp}"
                    
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
                    
                    sh """
                        mkdir -p ansible
                        echo "[openstack_vm]" > ansible/inventory.ini
                        echo "${vmIp} ansible_user=ubuntu ansible_ssh_private_key_file=${SSH_KEY_PATH}" >> ansible/inventory.ini
                    """
                    
                    sh 'ansible-playbook -i ansible/inventory.ini ansible/playbook.yml'
                }
            }
        }
    }
}