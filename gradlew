#!/usr/bin/env sh

set -e

DIR=$(cd "$(dirname "$0")/.." && pwd)

if [ ! -d "$DIR/gradle/wrapper" ]; then
  mkdir -p "$DIR/gradle/wrapper"
fi

cat > "$DIR/gradle/wrapper/gradle-wrapper.properties" << EOF
#Sun Jan 01 00:00:00 UTC 2023
gradle.wrapper.version=7.4.2
gradle.distribution.url=https\://services.gradle.org/distributions/gradle-7.4.2-bin.zip
EOF

cat > "$DIR/gradlew" << 'EOF'
#!/usr/bin/env sh

set -e

APP_NAME=$(basename "$0")

if [ ! -f "$DIR/gradle/wrapper/gradle-wrapper.jar" ]; then
  echo "The Gradle wrapper jar file is missing. Please run 'gradle wrapper' to fix this."
  exit 1
fi

# Execute the Gradle wrapper
java -jar "$DIR/gradle/wrapper/gradle-wrapper.jar" "$@"
EOF

chmod +x "$DIR/gradlew"
