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
                    // ⬇️⬇️⬇️ 修复点：这里改成了 sshUserPrivateKey
                    withCredentials([sshUserPrivateKey(credentialsId: 'tianlang', keyFileVariable: 'MY_KEY', usernameVariable: 'SSH_USER')]) {
                        sh 'terraform init'
                        // Terraform 会读取 MY_KEY 变量里的私钥文件路径
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
                        # 加载 OpenStack 凭证 (确保这个文件在 Jenkins 机器上存在)
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
                    
                    // 循环检查 SSH 是否通了
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
                    
                    // 动态生成 Ansible 配置
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