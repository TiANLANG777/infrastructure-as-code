pipeline {
    // 任务 2: 指定在你的 lang-tian 节点运行
    agent { label 'lang-tian' }

    environment {
        REGISTRY = "192.168.199.142:5000"
        IMAGE_NAME = "tianlang-app"
    }

    stages {
        // 任务 3: 自动拉取代码 (SCM 模式会自动执行此步，但定义出来更清晰)
        stage('Step 1: Checkout Git') {
            steps {
                checkout scm
            }
        }

        // 任务 5: IaC 基础设施逻辑 (Terraform/Ansible)
        stage('Step 2: Infra Logic') {
            steps {
                echo "Running Terraform/Ansible logic from repository..."
                // 这里可以放入你的 terraform apply 或 ansible-playbook 命令
                sh "ls -l main.tf playbook.yml" 
            }
        }

        // 任务 4 & 6: 构建镜像
        stage('Step 3: Build & Push Image') {
            steps {
                // 使用绝对路径规避之前的 Permission denied 问题
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
