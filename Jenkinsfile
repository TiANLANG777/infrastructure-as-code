pipeline {
    agent { label 'langtian' } 

    environment {
        ANSIBLE_HOST_KEY_CHECKING = "False"
        // 注意：这里删除了全局 SSH_KEY_PATH，因为我们会动态生成路径
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
                    withCredentials([file(credentialsId: 'YC_KEY_FILE', variable: 'MY_KEY')]) {
                        sh 'terraform init'
                        sh 'terraform apply -var=yc_key_path=$MY_KEY -auto-approve'
                    }
                }
                sh 'kubectl apply -f postgres-deployment.yaml'
                sh 'kubectl apply -f deployment.yaml'
                sh 'kubectl rollout restart deployment/tianlang-app'
            }
        }

        stage('OpenStack: Provision VM') {
            steps {
                dir('openstack') {
                    withCredentials([file(credentialsId: 'OPENSTACK_RC', variable: 'RC_FILE')]) {
                        sh '''
                            . "$RC_FILE"
                            
                            # ⬇️⬇️⬇️ 新增：自动生成 SSH 密钥对 ⬇️⬇️⬇️
                            # 如果密钥不存在，就现造一个
                            if [ ! -f tianlang_key ]; then
                                echo "Generating new SSH key pair..."
                                ssh-keygen -t rsa -b 2048 -f tianlang_key -N ""
                                chmod 600 tianlang_key
                            fi
                            
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
                    
                    // ⬇️⬇️⬇️ 修改：获取刚才生成的私钥的绝对路径
                    def keyPath = "${env.WORKSPACE}/openstack/tianlang_key"
                    
                    sh """
                        mkdir -p ansible
                        echo "[openstack_vm]" > ansible/inventory.ini
                        # 指向我们刚生成的 keyPath
                        echo "${vmIp} ansible_user=ubuntu ansible_ssh_private_key_file=${keyPath}" >> ansible/inventory.ini
                    """
                    
                    sh 'ansible-playbook -i ansible/inventory.ini ansible/playbook.yml'
                }
            }
        }
    stage('Debug: Check Bot Health') {
            steps {
                script {
                    dir('openstack') {
                        // 1. 获取虚拟机 IP
                        def vmIp = sh(script: "terraform output -raw vm_ip", returnStdout: true).trim()
                        echo "🔍 正在诊断虚拟机: ${vmIp}"

                        withCredentials([file(credentialsId: 'OPENSTACK_RC', variable: 'RC_FILE')]) {
                             // 使用刚才生成的私钥远程执行命令
                             // 注意：StrictHostKeyChecking=no 是为了防止第一次连接询问 yes/no 卡住
                            sh """
                                echo "1️⃣ --- 测试网络连通性 (能连上 Telegram 吗?) ---"
                                ssh -o StrictHostKeyChecking=no -i tianlang_key ubuntu@${vmIp} 'curl -I -m 5 https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/getMe || echo "❌ 连不上 Telegram API"'
                                
                                echo "\n2️⃣ --- 抓取机器人报错日志 ---"
                                ssh -o StrictHostKeyChecking=no -i tianlang_key ubuntu@${vmIp} 'sudo docker logs --tail 50 tianlang-app_app_1'
                            """
                        }
                    }
                }
            }
        }
    } // stages 结束
} // pipeline 结束