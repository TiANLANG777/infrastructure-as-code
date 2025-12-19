FROM eclipse-temurin:17-jdk-alpine
# 假设你的 jar 包名字叫 app.jar，或者根据实际情况修改
COPY *.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
