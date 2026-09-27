FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip \
    perl git ca-certificates curl \
    libnet-ssleay-perl libwhisker2-perl \
    libjson-perl libxml-writer-perl \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install security tools
RUN python3 -m venv /opt/security-tools \
    && /opt/security-tools/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/security-tools/bin/pip install --no-cache-dir \
        bandit \
        semgrep \
        detect-secrets \
        pip-audit \
    && ln -s /opt/security-tools/bin/bandit /usr/local/bin/bandit \
    && ln -s /opt/security-tools/bin/semgrep /usr/local/bin/semgrep \
    && ln -s /opt/security-tools/bin/detect-secrets /usr/local/bin/detect-secrets \
    && ln -s /opt/security-tools/bin/pip-audit /usr/local/bin/pip-audit

USER jenkins
