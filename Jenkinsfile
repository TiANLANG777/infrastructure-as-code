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

        // 任务 5: IaC 基础设施逻辑 (适配 Yandex Cloud)
        stage('Step 2: Infra Logic') {
            steps {
                echo "Initializing and Applying Terraform for Yandex Cloud..."
                // withCredentials 将授权 JSON 文件挂载到临时路径
                withCredentials([file(credentialsId: "${YC_CREDENTIALS_ID}", variable: 'MY_KEY')]) {
                    sh """
                        # 进入你新建的 yandex_lab5 文件夹
                        cd yandex_lab5
                        
                        terraform init
                        
                        # 传入凭据路径，自动批准执行
                        terraform apply -var="yc_key_path=${MY_KEY}" -auto-approve
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
