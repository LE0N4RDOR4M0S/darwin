from fastapi import FastAPI, Body
from datetime import datetime
import subprocess, os, tempfile, json, time, uuid

app = FastAPI(title="C\u00f3digo Vivo - Generator")

GENERATOR_WORKDIR = os.getenv("GENERATOR_WORKDIR", "/repo")


def run_cmd(cmd, cwd=None, check=False, env=None):
    print(f"RUN: {' '.join(cmd)} (cwd={cwd})")
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    print("RET", res.returncode)
    if res.stdout:
        print("OUT:", res.stdout)
    if res.stderr:
        print("ERR:", res.stderr)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{res.stderr}")
    return res


@app.post("/generate")
def generate_patch(payload: dict = Body(...)):
    """
    Gera um branch/patch, faz build e executa testes de carga para produzir candidate JSON.
    Retorna: { status, branch, candidate: {p95, error_rate} }
    """
    # allow payload to specify a path (absolute or relative to repo); default to common path under app/
    file_arg = payload.get("file")
    if not file_arg:
        file_arg = "app/src/main/java/com/leonardoramos/app/config/HttpClientConfig.java"
    branch_name = f"candidate_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    # Determine working repo: if GENERATOR_WORKDIR is not a git repo, try to clone from GIT_REMOTE
    working_repo = GENERATOR_WORKDIR
    use_temp_clone = False
    if not os.path.isdir(os.path.join(GENERATOR_WORKDIR, '.git')):
        git_remote = os.getenv('GIT_REMOTE')
        if git_remote:
            # clone remote into a temporary dir and operate there
            tmp_clone = tempfile.mkdtemp(prefix='repo_clone_')
            print(f"GENERATOR_WORKDIR has no .git; cloning {git_remote} into {tmp_clone}")
            run_cmd(["git", "clone", git_remote, tmp_clone], check=True)
            working_repo = tmp_clone
            use_temp_clone = True
        else:
            # initialize a local git repo so generator can create branches (push may fail)
            print(f"GENERATOR_WORKDIR has no .git; initializing local git repo in {GENERATOR_WORKDIR}")
            run_cmd(["git", "init"], cwd=GENERATOR_WORKDIR, check=True)
            try:
                run_cmd(["git", "add", "."], cwd=GENERATOR_WORKDIR, check=True)
                run_cmd(["git", "commit", "-m", "initial commit by generator"], cwd=GENERATOR_WORKDIR)
            except Exception as e:
                print("Warning: initial commit may have failed (no changes):", e)

    # Cria branch localmente
    run_cmd(["git", "checkout", "-b", branch_name], cwd=working_repo, check=True)

    # Resolve the actual file path inside the working_repo
    # We'll try a set of sensible candidates and also fall back to a recursive
    # search by basename to handle variations in layout or when the payload
    # provides a path relative to a different root.
    candidate_paths = []
    if os.path.isabs(file_arg):
        candidate_paths.append(file_arg)
        # also try interpreting absolute as relative to working_repo
        candidate_paths.append(os.path.join(working_repo, file_arg.lstrip('/')))
    else:
        candidate_paths.append(os.path.join(working_repo, file_arg))
        candidate_paths.append(os.path.join(working_repo, file_arg.lstrip('/')))
        candidate_paths.append(os.path.join(working_repo, 'app', file_arg))
        candidate_paths.append(os.path.join(working_repo, 'src', file_arg))
        # try common Java layout under app/
        if file_arg.startswith('src'):
            candidate_paths.append(os.path.join(working_repo, 'app', file_arg))
            candidate_paths.append(os.path.join(working_repo, 'app', file_arg.lstrip('/')))

    file_path = None
    tried = []
    for p in candidate_paths:
        tried.append(p)
        if os.path.exists(p):
            file_path = p
            print(f"Resolved file via candidate path: {p}")
            break

    # If not found yet, try a recursive search for the basename inside the repo
    if file_path is None:
        basename = os.path.basename(file_arg)
        print(f"File not found in candidate paths, searching for basename '{basename}' under {working_repo} ...")
        matches = []
        for root, dirs, files in os.walk(working_repo):
            if basename in files:
                matches.append(os.path.join(root, basename))
        if matches:
            # Prefer matches under src/main/java or app/ when possible
            preferred = None
            for m in matches:
                if os.path.join('src', 'main', 'java') in m.replace('\\', '/') or '/app/' in m.replace('\\', '/'):
                    preferred = m
                    break
            file_path = preferred or matches[0]
            print(f"Found candidate file(s) by basename search: {matches}; selected: {file_path}")
            tried.extend(matches)

    if file_path is None:
        # Provide a helpful diagnostic listing a few entries under the repo root to aid debugging
        sample = []
        try:
            for i, entry in enumerate(os.listdir(working_repo)):
                sample.append(entry)
                if i >= 20:
                    break
        except Exception:
            sample = ['<could not list working_repo>']
        raise RuntimeError(f"Arquivo especificado não encontrado. Tentei: {tried}. Entradas em {working_repo} (top 20): {sample}")

    # Aplica edição simples (frágil, mas OK para PoC)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Falha ao abrir arquivo {file_path}: {e}")

    new_content = content.replace("timeout = 1000", "timeout = 3000")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    run_cmd(["git", "add", "."], cwd=working_repo, check=True)

    # Ensure git identity is configured locally so commits do not fail inside containers
    try:
        email_res = run_cmd(["git", "config", "--get", "user.email"], cwd=working_repo, check=False)
        name_res = run_cmd(["git", "config", "--get", "user.name"], cwd=working_repo, check=False)
        email = (email_res.stdout or "").strip() if hasattr(email_res, 'stdout') else ''
        name = (name_res.stdout or "").strip() if hasattr(name_res, 'stdout') else ''
        if not email:
            email = os.getenv('GENERATOR_GIT_USER_EMAIL', 'leomatisa1000@gmail.com')
            run_cmd(["git", "config", "user.email", email], cwd=working_repo, check=True)
        if not name:
            name = os.getenv('GENERATOR_GIT_USER_NAME', 'Generator')
            run_cmd(["git", "config", "user.name", name], cwd=working_repo, check=True)
        print(f"Using git identity: {name} <{email}>")
    except Exception as e:
        print("Warning: failed to ensure git identity:", e)

    # Only commit if there are staged changes
    status_res = run_cmd(["git", "status", "--porcelain"], cwd=working_repo, check=False)
    status_out = (status_res.stdout or "").strip() if hasattr(status_res, 'stdout') else ''
    if status_out:
        run_cmd(["git", "commit", "-m", "Auto patch generated for hotspot"], cwd=working_repo, check=True)
    else:
        print("No changes to commit (working tree clean)")

    # Optional: push to origin if credentials are configured
    try:
        push_env = os.environ.copy()
        ssh_key = os.getenv('SSH_KEY_PATH')
        if ssh_key:
            # Use GIT_SSH_COMMAND to instruct git to use the mounted private key
            push_env['GIT_SSH_COMMAND'] = f"ssh -i {ssh_key} -o StrictHostKeyChecking=no"
        run_cmd(["git", "push", "origin", branch_name], cwd=working_repo, env=push_env)
    except Exception as e:
        print("Aviso: push falhou (provavelmente sem credenciais configuradas):", e)

    # Create a temp workdir to checkout and build
    with tempfile.TemporaryDirectory() as tmpdir:
        print("Checkout branch into", tmpdir)
        # clone from the working_repo (could be the mounted repo or a temp clone)
        run_cmd(["git", "clone", "--branch", branch_name, working_repo, tmpdir], check=True)

        # Locate where the Maven project (pom.xml) lives inside the clone.
        # Many repos have the actual Java project under an `app/` subfolder.
        build_dir = tmpdir
        pom_path = os.path.join(build_dir, 'pom.xml')
        if not os.path.exists(pom_path):
            print("pom.xml not at clone root, searching for pom.xml under clone...")
            found_poms = []
            for root, dirs, files in os.walk(tmpdir):
                if 'pom.xml' in files:
                    found_poms.append(os.path.join(root, 'pom.xml'))
            if found_poms:
                # Prefer app/pom.xml when present
                preferred = None
                for p in found_poms:
                    if os.path.join('app', 'pom.xml') in p.replace('\\', '/'):
                        preferred = p
                        break
                chosen = preferred or found_poms[0]
                build_dir = os.path.dirname(chosen)
                print(f"Using Maven project at: {build_dir}")
            else:
                raise RuntimeError(f"pom.xml not found in clone at {tmpdir}; looked for: {found_poms}")

        # Build with maven from the detected project dir
        run_cmd(["mvn", "-B", "-DskipTests", "package"], cwd=build_dir, check=True)

        # Find the jar under the build_dir/target
        target_dir = os.path.join(build_dir, "target")
        if not os.path.isdir(target_dir):
            raise RuntimeError(f"Maven build did not produce target/ directory in {build_dir}")
        jar_files = [f for f in os.listdir(target_dir) if f.endswith('.jar')]
        if not jar_files:
            raise RuntimeError(f"Jar não encontrado no target em {target_dir}")
        jar_path = os.path.join(target_dir, jar_files[0])

        # Run jar in background
        proc = subprocess.Popen(["java", "-jar", jar_path], cwd=tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            # Wait for app to start (naive sleep)
            time.sleep(5)

            # Generate a simple k6 script file
            k6_script = os.path.join(tmpdir, "k6_test.js")
            with open(k6_script, "w", encoding="utf-8") as f:
                f.write('''import http from "k6/http";\nimport { sleep } from "k6";\nexport let options = { vus: 5, duration: "10s" };\nexport default function () { http.get("http://127.0.0.1:8080/api/teste"); sleep(1); }\n''')

            # Run k6 and capture simple metrics (we'll parse stdout)
            k6_res = run_cmd(["k6", "run", "--summary-export=summary.json", k6_script], cwd=tmpdir, check=True)

            # Read summary.json
            summary_path = os.path.join(tmpdir, "summary.json")
            if os.path.exists(summary_path):
                with open(summary_path, "r", encoding="utf-8") as sf:
                    summary = json.load(sf)
                # Extract p95 from http_req_duration and error rate
                p95 = summary.get('metrics', {}).get('http_req_duration', {}).get('values', {}).get('p(95)', None)
                # error rate: based on http_req_failed
                error_rate = summary.get('metrics', {}).get('http_req_failed', {}).get('rate', 0)
            else:
                p95 = None
                error_rate = None

            candidate = {"p95": p95, "error_rate": error_rate}
        finally:
            # terminate the jar
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

    return {"status": "patch_generated_and_tested", "branch": branch_name, "candidate": candidate}
