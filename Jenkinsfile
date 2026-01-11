pipeline {
    // 任务 2: 指定在你的 lang-tian 节点运行
    agent { label 'langtian' }

    environment {
        REGISTRY = "192.168.199.142:5000"
        IMAGE_NAME = "tianlang-app"
        // 这里定义你在 Jenkins 中创建的凭据 ID
        YC_CREDENTIALS_ID = "YC_KEY" 
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
                // withCredentials 会将密钥文件下载到临时路径并存入 MY_KEY 变量
                withCredentials([file(credentialsId: "${YC_CREDENTIALS_ID}", variable: 'MY_KEY')]) {
                    sh """
                        cd yandex_lab5
                        terraform init
                        # 传入凭据路径和自动确认执行
                        terraform apply -var="yc_key_path=${MY_KEY}" -auto-approve
                    """
                }
            }
        }

        // 任务 4 & 6: 构建镜像
        stage('Step 3: Build & Push Image') {
            steps {
                sh "/usr/bin/docker build -t ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER} ."
                sh "/usr/bin/docker push ${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }

        // 任务 7: 交付到 Kubernetes
        stage('Step 4: Deploy to K8s') {
            steps {
                // 实验 5/6 通常要求这里部署到新生成的云资源上
                sh "kubectl apply -f deployment.yaml"
                sh "kubectl get pods"
            }
        }
    }
}
