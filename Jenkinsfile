pipeline {
    agent { label 'langtian' } 

    environment {
        ANSIBLE_HOST_KEY_CHECKING = "False"
        SSH_KEY_PATH = "/home/ubuntu/id_rsa_elk_tf"
    }

    stages {
        stage('Checkout') {
            steps {
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
                    // 这里使用的是 Yandex 的 JSON 密钥
                    withCredentials([file(credentialsId: 'YC_KEY_FILE', variable: 'MY_KEY')]) {
                        sh 'terraform init'
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
                    // ⬇️⬇️⬇️ 重点修改：让代码读取你刚才上传的 OPENSTACK_RC 凭证 ⬇️⬇️⬇️
                    withCredentials([file(credentialsId: 'OPENSTACK_RC', variable: 'RC_FILE')]) {
                        sh '''
                            # 加载凭证 (不再读取本地不存在的文件，而是读取 Jenkins 注入的变量)
                            . "$RC_FILE"
                            
                            terraform init
                            terraform apply -auto-approve
                        '''
                    }
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
                    
                    // 生成 Ansible 配置
                    sh """
                        mkdir -p ansible
                        echo "[openstack_vm]" > ansible/inventory.ini
                        echo "${vmIp} ansible_user=ubuntu ansible_ssh_private_key_file=${SSH_KEY_PATH}" >> ansible/inventory.ini
                    """
                    
                    // 运行部署
                    sh 'ansible-playbook -i ansible/inventory.ini ansible/playbook.yml'
                }
            }
        }
    }
}