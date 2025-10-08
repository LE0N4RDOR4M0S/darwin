FROM maven:3.9.4-eclipse-temurin-21 AS build
WORKDIR /workspace/app

COPY pom.xml .
COPY .mvn .mvn
COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:21-jre-jammy
ARG JAVA_OPTS=""
WORKDIR /app

COPY --from=build /workspace/app/target/*.jar app.jar

RUN groupadd -r spring && useradd -r -g spring -s /sbin/nologin spring
USER spring

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar /app/app.jar"]