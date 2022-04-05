FROM openjdk:11.0-jre-slim

ENV JAVA_OPTIONS=-Xmx4G
ENV OTP_VERSION=2.0.0
ENV OTP_OPTIONS="--build --serve --port 8080 /data"

ENV OTP_URL="https://repo1.maven.org/maven2/org/opentripplanner"

RUN apt-get update -q \
 && apt-get install wget -y \
 && wget ${OTP_URL}/otp/${OTP_VERSION}/otp-${OTP_VERSION}-shaded.jar \
  -qO /otp.jar \
 && chmod +x /otp.jar

EXPOSE 8080

CMD java ${JAVA_OPTIONS} -jar ./otp.jar ${OTP_OPTIONS}
