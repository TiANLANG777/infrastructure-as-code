pipeline {
    // 任务 2: 指定在你的 langtian-updated 节点运行
    agent { label 'langtian' }

    environment {
        REGISTRY = "192.168.199.142:5000"
        IMAGE_NAME = "tianlang-app"
        // 对应 image_2306ed.png 中显示的 ID
        YC_CREDENTIALS_ID = "YC_KEY_FILE" 
        TF_CLI_CONFIG_FILE = "/home/ubuntu/.terraform.d/filesystem_mirror.tfrc"
    }

    stages {
        // 任务 3: 自动拉取代码
        stage('Step 1: Checkout Git') {
            steps {
                checkout scm
            }
        }

        stage('Step 2: Infra Logic') {
            steps {
                echo "Initializing and Applying Terraform for Yandex Cloud..."
                withCredentials([file(credentialsId: "${YC_CREDENTIALS_ID}", variable: 'MY_KEY')]) {
                    sh """
                        cd yandex_lab5
                        terraform init
                        terraform apply -var="yc_key_path=\$MY_KEY" -auto-approve
                        
                        VM_IP=\$(terraform output -raw instance_ip)
                        echo "Target VM IP: \${VM_IP}"
                        
                        # 增加 -w 5 等待 SSH 服务完全启动（防止刚创建完连不上）
                        sleep 10 

                        export ANSIBLE_HOST_KEY_CHECKING=False
                        
                        # 修改点：增加 --private-key 参数
                        # 请确保路径 /home/ubuntu/.ssh/id_rsa 是正确的
                        ansible-playbook -u ubuntu \\
                            -i "\${VM_IP}," \\
                            --private-key /home/ubuntu/.ssh/id_rsa \\
                            ../playbook.yml
                    """
                }
            }
        }
        // 任务 4 & 6: 构建并推送镜像
        stage('Step 3: Build & Push Image') {
            steps {
                sh "/usr/bin/docker build -t ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} ."
                sh "/usr/bin/docker push ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }

        // 任务 7: 交付到 Kubernetes
        stage('Step 4: Deploy to K8s') {
            steps {
                sh "kubectl apply -f deployment.yaml"
                sh "kubectl get pods"
            }
        }
    }
}
