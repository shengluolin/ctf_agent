FROM --platform=amd64 kalilinux/kali-rolling:latest

# Force Aliyun mirror ONLY - disable redirects, backups, and proxy for apt
RUN rm -rf /etc/apt/sources.list.d/* && \
    echo "deb [trusted=yes] http://mirrors.aliyun.com/kali kali-rolling main non-free contrib" > /etc/apt/sources.list && \
    echo "Acquire::http::Redirect::Warn \"false\";" > /etc/apt/apt.conf.d/99-no-redirect && \
    echo "Acquire::AllowInsecureRepositories \"true\";" >> /etc/apt/apt.conf.d/99-no-redirect && \
    echo "Acquire::http::Proxy \"false\";" > /etc/apt/apt.conf.d/99-no-proxy && \
    apt-get update

# Install basic tools first (including sudo, required before user creation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl wget gnupg sudo && \
    rm -rf /var/lib/apt/lists/*

# Create kali user with sudo access
RUN useradd -m -s /bin/bash kali && \
    echo "kali ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Kali full headless toolset - with robust fallback for package download failures
# Note: We continue even if some packages fail (like metasploit-framework)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y \
    -o DPkg::Options::="--force-confdef" \
    -o DPkg::Options::="--force-confold" \
    -o Acquire::http::Timeout=120 \
    -o Acquire::https::Timeout=120 \
    -o Acquire::Retries=5 \
    install kali-linux-headless || \
    (sleep 30 && apt-get update && apt-get -y install kali-linux-headless) || \
    (sleep 60 && apt-get update && apt-get -y --fix-broken install || true) && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER kali

# Extra security tools + npm
RUN sudo rm -rf /etc/apt/sources.list.d/* && \
    sudo apt-get update && \
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y \
    -o DPkg::Options::="--force-confdef" \
    -o DPkg::Options::="--force-confold" install \
    bsdextrautils npm jq iputils-ping sshpass ncat rlwrap \
    bloodyad coercer enum4linux-ng pwncat chisel-common-binaries \
    dirsearch yq krb5-user gitleaks naabu nikto netexec adb && \
    sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/* && \
    pip3 install pwntools pymongo --break-system-packages && \
    sudo npm install -g @playwright/cli@latest && \
    cd /tmp && playwright-cli install || true

# Download binary tools
RUN cd /tmp && \
    wget -q "https://github.com/projectdiscovery/katana/releases/download/v1.5.0/katana_1.5.0_linux_amd64.zip" -O katana.zip && \
    wget -q "https://github.com/projectdiscovery/nuclei/releases/download/v3.7.1/nuclei_3.7.1_linux_amd64.zip" -O nuclei.zip && \
    wget -q "https://github.com/hahwul/dalfox/releases/download/v2.12.0/dalfox-linux-amd64.tar.gz" -O dalfox.tar.gz && \
    wget -q "https://github.com/BishopFox/cloudfox/releases/download/v2.0.1/cloudfox-linux-amd64.zip" -O cloudfox.zip && \
    wget -q "https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64" -O kerbrute && \
    git clone --depth 1 "https://github.com/projectdiscovery/nuclei-templates.git" /home/kali/.local/nuclei-templates || true && \
    unzip -q katana.zip katana && sudo mv katana /usr/local/bin/ && \
    unzip -q nuclei.zip nuclei && sudo mv nuclei /usr/local/bin/ && \
    tar -xzf dalfox.tar.gz && sudo mv dalfox-linux-amd64 /usr/local/bin/dalfox && \
    unzip -q cloudfox.zip cloudfox/cloudfox && sudo mv cloudfox/cloudfox /usr/local/bin/ && \
    sudo cp kerbrute /usr/local/bin/ && \
    nuclei -ut 2>/dev/null || true && \
    sudo rm -rf /tmp/*

# Security knowledge repos (tolerate failures)
RUN mkdir -p /home/kali/knowledges && cd /home/kali/knowledges && \
    git clone --depth=1 https://github.com/swisskyrepo/PayloadsAllTheThings.git || true && \
    git clone --depth=1 https://github.com/swisskyrepo/InternalAllTheThings.git || true && \
    git clone --depth=1 https://github.com/HackTricks-wiki/hacktricks.git || true && \
    git clone --depth=1 https://github.com/HackTricks-wiki/hacktricks-cloud.git || true

# Exploit tools
RUN mkdir -p /home/kali/tools && cd /home/kali/tools && \
    wget -q "https://github.com/frohoff/ysoserial/releases/download/v0.0.6/ysoserial-all.jar" -O ysoserial.jar || true && \
    git clone --depth=1 https://github.com/ticarpi/jwt_tool.git || true && \
    (cd jwt_tool && pip3 install -r requirements.txt --break-system-packages) || true && \
    git clone --depth=1 https://github.com/IOActive/jdwp-shellifier.git || true

# PoC collections (tolerate failures)
RUN mkdir -p /home/kali/pocs && cd /home/kali/pocs && \
    git clone --depth=1 https://github.com/iSee857/CVE-PoC.git || true && \
    git clone --depth=1 https://github.com/zhzyker/exphub.git || true && \
    git clone --depth=1 https://github.com/passwa11/2023Hvv_.git || true && \
    git clone --depth=1 https://github.com/Threekiii/Awesome-POC.git || true && \
    git clone --depth=1 https://github.com/vulhub/vulhub.git || true

# ripgrep + fd
RUN cd /tmp && \
    wget -q "https://github.com/BurntSushi/ripgrep/releases/download/15.1.0/ripgrep_15.1.0-1_amd64.deb" -O ripgrep.deb && \
    wget -q "https://github.com/sharkdp/fd/releases/download/v10.4.2/fd_10.4.2-1_amd64.deb" -O fd.deb && \
    sudo apt-get install -y ./ripgrep.deb ./fd.deb && \
    sudo rm -rf /tmp/* && sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*

# Claude Code CLI
RUN sudo npm install -g @anthropic-ai/claude-code

RUN sudo chmod +x /usr/local/bin/kerbrute && \
    mkdir -p /home/kali/.config/nuclei && \
    echo "disable-update-check: true" >> /home/kali/.config/nuclei/config.yaml && \
    echo "update-template-dir: /home/kali/.local/nuclei-templates" >> /home/kali/.config/nuclei/config.yaml && \
    rm -rf /home/kali/nuclei-templates 2>/dev/null || true

RUN sudo rm -rf /usr/lib/llvm-*/build && \
    sudo chmod o+rx /usr/lib/mysql/plugin/auth_pam_tool_dir /etc/ssl/private 2>/dev/null || true

RUN printf '%s\n' 'PS1="${PS1%\\n*} \[\033[0;36m\]\D{%y-%m-%d} - \t\[\033[;32m\]\n${PS1##*\\n}"' >> /home/kali/.bashrc && \
    mkdir -p /home/kali/workspace && cd /home/kali/workspace && git init

ENV TZ=Asia/Shanghai
ENV PLAYWRIGHT_MCP_BROWSER=chromium
ENV CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
ENV PYTHONUNBUFFERED=1

# Copy CTF skills and CLAUDE.md into workspace
COPY .claude/skills/ /home/kali/workspace/.claude/skills/
COPY CLAUDE.md /home/kali/workspace/CLAUDE.md

WORKDIR /home/kali/workspace

# Entrypoint: run claude with the given prompt
ENTRYPOINT ["claude", "--dangerously-skip-permissions", "-p", "--"]