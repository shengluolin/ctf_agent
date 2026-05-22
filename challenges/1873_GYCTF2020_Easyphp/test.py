import requests

url = "http://38b5f744-d805-465d-9f56-30bcce267c94.node5.buuoj.cn:81"

# Test various action parameters
actions = ["index", "home", "main", "test", "debug", "source", "code", "file", "path", 
           "include", "page", "template", "view", "show", "display", "read", "write",
           "delete", "edit", "update", "create", "add", "remove", "backup", "restore",
           "export", "import", "download", "upload", "copy", "move", "rename", "chmod",
           "chown", "mkdir", "rmdir", "touch", "cat", "more", "less", "head", "tail",
           "grep", "find", "locate", "whereis", "which", "whoami", "id", "pwd", "ls",
           "dir", "list", "scan", "check", "verify", "validate", "authenticate", "authorize"]

for action in actions:
    r = requests.get(f"{url}/index.php?action={action}")
    if r.text and "login" not in r.text and "redirect" not in r.text.lower():
        print(f"[+] Found: {action}")
        print(r.text[:500])
        print("---")
