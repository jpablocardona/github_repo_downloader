#!/usr/bin/env python3

import argparse
import os
import sys
from typing import List

from dotenv import load_dotenv
from github import Github
from tqdm import tqdm


def parse_args():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Lista repositorios de una organización de GitHub"
    )
    parser.add_argument("--org", help="Nombre de la organización")
    parser.add_argument(
        "--output", help="Archivo de salida para guardar la lista de repositorios"
    )
    parser.add_argument("--token", help="Token de acceso personal de GitHub")
    return parser.parse_args()


def get_org_repos(github_client: Github, org_name: str) -> List[str]:
    """Obtiene la lista de repositorios de una organización."""
    try:
        org = github_client.get_organization(org_name)
        repos = []

        print(f"\nObteniendo repositorios de la organización {org_name}...")
        for repo in tqdm(org.get_repos(), desc="Procesando repositorios"):
            repos.append(f"git@github.com:{org_name}/{repo.name}.git")

        return repos

    except Exception as e:
        print(f"❌ Error al obtener repositorios: {str(e)}")
        sys.exit(1)


def save_repos_to_file(repos: List[str], output_file: str) -> None:
    """Guarda la lista de repositorios en un archivo."""
    try:
        with open(output_file, "w") as f:
            for repo in repos:
                f.write(f"{repo}\n")
        print(f"\n✅ Lista de repositorios guardada en {output_file}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {str(e)}")
        sys.exit(1)


def get_config_values(args) -> tuple[str, str]:
    """Obtiene los valores de configuración desde argumentos o variables de entorno."""
    # Cargar variables de entorno desde .env si existe
    load_dotenv()

    # Obtener token
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Error: Se requiere un token de GitHub.")
        print("   Proporciona --token o configura GITHUB_TOKEN en .env")
        sys.exit(1)

    # Obtener organización
    org = args.org or os.getenv("ORGANIZATION")
    if not org:
        print("❌ Error: Se requiere el nombre de la organización.")
        print("   Proporciona --org o configura ORGANIZATION en .env")
        sys.exit(1)

    return token, org


def main() -> None:
    """Función principal."""
    args = parse_args()

    token, org = get_config_values(args)

    github_client = Github(token)
    repos = get_org_repos(github_client, org)

    if args.output:
        save_repos_to_file(repos, args.output)
    else:
        print("\nRepositorios encontrados:")
        for repo in repos:
            print(repo)


if __name__ == "__main__":
    main()
