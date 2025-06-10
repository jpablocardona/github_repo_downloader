# GitHub Repository Downloader

Herramienta Python para descargar y mantener actualizados repositorios de GitHub de manera masiva. Incluye funcionalidades para listar repositorios de organizaciones y procesar múltiples repositorios con todas sus ramas y tags.

## Estructura del Proyecto

```
github_repo_downloader/
├── src/
│   ├── list_org_repos.py      # Lista todos los repositorios de una organización
│   └── downloader.py          # Descarga/actualiza repositorios desde archivo de entrada
├── requirements.txt           # Dependencias de Python
├── repos.txt                 # Archivo de ejemplo con URLs de repositorios
├── CLAUDE.md                 # Guía para Claude Code
└── README.md                 # Esta documentación
```

## Características Principales

- **Listado de organizaciones**: Obtiene todos los repositorios de una organización de GitHub
- **Descarga masiva**: Procesa múltiples repositorios desde un archivo de entrada
- **Actualización inteligente**: Detecta repositorios existentes y los actualiza automáticamente
- **Soporte completo**: Descarga todas las ramas, tags y referencias
- **Progreso visual**: Barras de progreso con `tqdm` para seguimiento en tiempo real
- **Manejo de errores**: Continúa procesando aunque falle un repositorio individual
- **Formatos flexibles**: Soporte para URLs SSH y HTTPS

## Requisitos

- Python 3.8 o superior
- Git instalado en el sistema
- Token de acceso personal de GitHub (recomendado para evitar límites de API)
- Clave SSH configurada para GitHub (para URLs SSH)

## Instalación

1. Clonar este repositorio:
```bash
git clone <url-del-repositorio>
cd github_repo_downloader
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### 1. Listar repositorios de una organización

Genera una lista de todos los repositorios de una organización:

```bash
python src/list_org_repos.py --org nombre_organizacion --token tu_token_github
```

**Opciones:**
- `--org`: Nombre de la organización (requerido)
- `--token`: Token de acceso personal de GitHub (requerido)
- `--output`: Archivo donde guardar la lista (opcional, por defecto muestra en pantalla)

**Ejemplo:**
```bash
# Mostrar en pantalla
python src/list_org_repos.py --org microsoft --token ghp_xxxxxxxxxxxx

# Guardar en archivo
python src/list_org_repos.py --org microsoft --token ghp_xxxxxxxxxxxx --output microsoft_repos.txt
```

### 2. Descargar/actualizar repositorios

Procesa múltiples repositorios desde un archivo de entrada:

```bash
python src/downloader.py --input repos.txt --output ./repos --token tu_token_github
```

**Opciones:**
- `--input`: Archivo con lista de repositorios (requerido)
- `--output`: Directorio de destino (opcional, por defecto: `./repos`)
- `--token`: Token de GitHub (opcional, pero recomendado)

**Formato del archivo de entrada:**
```
git@github.com:usuario/repo1.git
https://github.com/usuario/repo2.git
git@github.com:org/repo3.git
```

## Comportamiento del Sistema

### Procesamiento de Repositorios

1. **Repositorios nuevos**: Clona completamente con todas las ramas y tags
2. **Repositorios existentes**: 
   - Actualiza todas las ramas remotas
   - Descarga nuevos tags
   - Limpia archivos no rastreados
   - Mantiene la rama por defecto activa

### Nomenclatura de Directorios

Los repositorios se guardan usando el formato: `usuario_repositorio`
- `microsoft/vscode` → `microsoft_vscode/`
- `facebook/react` → `facebook_react/`

### Manejo de Errores

- Los errores en repositorios individuales no detienen el proceso completo
- Se muestran mensajes descriptivos para cada error
- El script continúa con el siguiente repositorio automáticamente

## Dependencias

```
PyGithub>=1.59.0    # Interacción con la API de GitHub
GitPython>=3.1.0    # Operaciones Git en Python
tqdm>=4.64.0        # Barras de progreso
```

## Casos de Uso Típicos

### Backup de Organización Completa
```bash
# 1. Listar todos los repos de la organización
python src/list_org_repos.py --org mi-org --token $GITHUB_TOKEN --output mi-org-repos.txt

# 2. Descargar todos los repositorios
python src/downloader.py --input mi-org-repos.txt --output ./backup-org --token $GITHUB_TOKEN
```

### Sincronización Regular
```bash
# Actualizar repositorios existentes (ejecutar periódicamente)
python src/downloader.py --input repos.txt --output ./repos --token $GITHUB_TOKEN
```

### Migración de Repositorios
```bash
# Descargar repositorios específicos para migración
python src/downloader.py --input repositorios-a-migrar.txt --output ./migracion
```

## Notas Importantes

- **Tokens de GitHub**: Recomendado para evitar límites de rate limiting
- **Claves SSH**: Necesarias para URLs en formato `git@github.com:...`
- **Espacio en disco**: Considera el tamaño total antes de descargar organizaciones grandes
- **Conectividad**: Requiere conexión estable a Internet para operaciones Git
- **Permisos**: El token debe tener permisos de lectura para repositorios privados

## Solución de Problemas

### Error de autenticación SSH
```bash
# Verificar configuración SSH
ssh -T git@github.com
```

### Límites de API
```bash
# Usar token para aumentar límites
export GITHUB_TOKEN=tu_token_aqui
python src/downloader.py --input repos.txt --token $GITHUB_TOKEN
```

### Repositorios grandes
```bash
# Ejecutar en lotes más pequeños para organizaciones muy grandes
head -10 todos-los-repos.txt > lote1.txt
python src/downloader.py --input lote1.txt --output ./repos
``` 