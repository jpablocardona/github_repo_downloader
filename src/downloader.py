#!/usr/bin/env python3

import argparse
import os
import sys
from typing import List, Optional
from urllib.parse import urlparse

from github import Github
from git import Repo
from tqdm import tqdm


def parse_args():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Descarga o actualiza repositorios de GitHub"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Archivo de texto con la lista de repositorios"
    )
    parser.add_argument(
        "--output",
        default="./repos",
        help="Directorio de salida para los repositorios"
    )
    parser.add_argument(
        "--token",
        help="Token de acceso personal de GitHub"
    )
    return parser.parse_args()


def read_repos_file(file_path: str) -> List[str]:
    """Lee el archivo de repositorios y retorna la lista de repos."""
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        sys.exit(1)


def get_repo_name_from_url(url: str) -> str:
    """Extrae el nombre del repositorio de una URL SSH o HTTPS."""
    parsed = urlparse(url)
    if parsed.scheme == "git":
        # Formato SSH: git@github.com:usuario/repo.git
        path = parsed.path.split(":")[-1]
    else:
        # Formato HTTPS: https://github.com/usuario/repo.git
        path = parsed.path

    # Eliminar .git del final si existe
    if path.endswith(".git"):
        path = path[:-4]

    return path


def get_default_branch(git_repo: Repo) -> Optional[str]:
    """Obtiene la rama por defecto del repositorio."""
    try:
        remote = git_repo.remote()
        remote.fetch()
        return remote.refs[0].name.replace("origin/", "")
    except Exception:
        try:
            return git_repo.active_branch.name
        except Exception:
            return None


def clean_untracked_files(git_repo: Repo) -> None:
    """Elimina archivos y carpetas no rastreados en el repositorio local."""
    try:
        git_repo.git.clean("-fd")
    except Exception as e:
        print(f"Error al limpiar archivos no rastreados: {str(e)}")


def process_repository(
    github_client: Github,
    repo_url: str,
    output_dir: str
) -> None:
    """Procesa un repositorio: lo descarga si no existe o lo actualiza si ya existe."""
    try:
        repo_name = get_repo_name_from_url(repo_url)
        repo_dir = os.path.join(output_dir, repo_name.replace("/", "_"))
        
        if os.path.exists(repo_dir):
            print(f"\nActualizando {repo_name}...")
            git_repo = Repo(repo_dir)
            remote = git_repo.remote()
            remote.fetch()
            remote.fetch(tags=True)
            default_branch = get_default_branch(git_repo)
            for ref in remote.refs:
                if ref.name != "origin/HEAD":
                    try:
                        branch_name = ref.name.replace("origin/", "")
                        clean_untracked_files(git_repo)
                        git_repo.git.checkout(branch_name)
                        git_repo.git.pull("origin", branch_name)
                    except Exception as e:
                        print(f"Error al actualizar la rama {branch_name}: {str(e)}")
            if default_branch:
                clean_untracked_files(git_repo)
                git_repo.git.checkout(default_branch)
        else:
            os.makedirs(repo_dir, exist_ok=True)
            print(f"\nDescargando {repo_name}...")
            Repo.clone_from(repo_url, repo_dir)
            git_repo = Repo(repo_dir)
            remote = git_repo.remote()
            default_branch = get_default_branch(git_repo)
            for ref in remote.refs:
                if ref.name != "origin/HEAD":
                    try:
                        branch_name = ref.name.replace("origin/", "")
                        if branch_name != default_branch:
                            clean_untracked_files(git_repo)
                            git_repo.git.checkout("-b", branch_name, ref.name)
                    except Exception as e:
                        print(f"Error al descargar la rama {branch_name}: {str(e)}")
            remote.fetch(tags=True)
            if default_branch:
                clean_untracked_files(git_repo)
                git_repo.git.checkout(default_branch)
        print(f"✅ Repositorio {repo_name} procesado exitosamente")
    except Exception as e:
        print(f"❌ Error al procesar {repo_url}: {str(e)}")
        # No detener el script, continuar con el siguiente repo


def main() -> None:
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    github_client = Github(args.token) if args.token else Github()
    repos = read_repos_file(args.input)
    for repo in tqdm(repos, desc="Procesando repositorios"):
        process_repository(
            github_client,
            repo,
            args.output
        )


if __name__ == "__main__":
    main() 