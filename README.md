# MCP4GVA - MCP Server para GVA GIS

Servidor MCP (Model Context Protocol) mínimo para acceder a la API de GVA GIS (Generalitat Valenciana) - Servicio de Suelo de Actividades.

**Endpoint:** `https://gvagis.icv.gva.es/server/rest/services/Hosted/Suelo_actividades/FeatureServer/2`

## ¿Qué es esto?

Un servidor MCP que expone la API de ArcGIS REST de la Generalitat Valenciana para que Claude Desktop (y otras aplicaciones MCP) puedan consultar datos de suelo de actividades directamente.

## Instalación

### Requisito previo: Instalar `uv`

Primero necesitas tener `uv` instalado:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# O con pip
pip install uv
```

### Opción 1: Usar con `uvx` (RECOMENDADO)

Esta es la forma más simple - no requiere instalación local. Claude Desktop descargará y ejecutará automáticamente.

#### Configurar Claude Desktop

Edita el archivo de configuración de Claude Desktop:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Añade esta configuración:

```json
{
  "mcpServers": {
    "mcp4gva": {
      "command": "uvx",
      "args": ["mcp4gva"]
    }
  }
}
```

**Nota:** Para usar esta opción, el paquete debe estar publicado en PyPI. Para desarrollo local, usa la Opción 2.

### Opción 2: Desarrollo local con `uvx`

Si estás desarrollando o modificando el código:

```bash
# 1. Clonar/navegar al repositorio
cd mcp4gva

# 2. Configurar Claude Desktop con ruta local
```

En `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp4gva": {
      "command": "uvx",
      "args": [
        "--from",
        "/ruta/completa/a/mcp4gva",
        "mcp4gva"
      ]
    }
  }
}
```

### Opción 3: Instalación tradicional con pip

```bash
# Instalación en desarrollo
cd mcp4gva
pip install -e .

# Configuración en Claude Desktop
{
  "mcpServers": {
    "mcp4gva": {
      "command": "python",
      "args": ["-m", "mcp4gva.server"]
    }
  }
}
```

### 3. Reiniciar Claude Desktop

Reinicia Claude Desktop para que cargue el nuevo servidor MCP.

## Herramientas Disponibles

El servidor expone 4 herramientas que Claude puede usar:

### 1. `gva_layer_info`

Obtiene metadatos de la capa (campos, tipo de geometría, sistema de referencia, extensión).

**Parámetros:** Ninguno

**Ejemplo en Claude:**
```
Usa la herramienta gva_layer_info para ver qué campos tiene la capa de GVA GIS
```

### 2. `gva_query`

Consulta features de la capa con filtros SQL.

**Parámetros:**
- `where` (string, default: "1=1"): Cláusula SQL WHERE
- `out_fields` (string, default: "*"): Campos a devolver (separados por coma o "*")
- `return_geometry` (boolean, default: true): Devolver geometría
- `result_record_count` (integer, default: 10): Máximo de registros
- `result_offset` (integer, default: 0): Offset para paginación

**Ejemplo en Claude:**
```
Usa gva_query para obtener los primeros 5 registros donde MUNICIPIO='Valencia'
```

### 3. `gva_count`

Cuenta features que cumplen una condición.

**Parámetros:**
- `where` (string, default: "1=1"): Cláusula SQL WHERE

**Ejemplo en Claude:**
```
Cuenta cuántos registros hay en total con gva_count
```

### 4. `gva_export_geojson`

Exporta features a formato GeoJSON.

**Parámetros:**
- `where` (string, default: "1=1"): Filtro SQL
- `out_fields` (string, default: "*"): Campos a incluir
- `result_record_count` (integer, default: 100): Máximo de features

**Ejemplo en Claude:**
```
Exporta a GeoJSON los primeros 20 registros
```

## Ejemplos de Uso en Claude Desktop

Una vez configurado, puedes pedirle a Claude cosas como:

1. **Explorar la capa:**
   ```
   ¿Qué información tiene la capa de GVA GIS?
   ```

2. **Consultar datos:**
   ```
   Obtén 10 registros de la capa de suelo de actividades
   ```

3. **Filtrar por campo:**
   ```
   Muéstrame todos los registros del municipio de Valencia
   ```

4. **Contar registros:**
   ```
   ¿Cuántos registros hay en total en la capa?
   ```

5. **Exportar datos:**
   ```
   Exporta a GeoJSON los primeros 50 registros
   ```

## Estructura del Proyecto

```
mcp4gva/
├── mcp4gva/
│   ├── __init__.py
│   └── server.py          # Servidor MCP principal
├── pyproject.toml         # Configuración del paquete
├── requirements.txt       # Dependencias (legacy)
├── claude_desktop_config.json  # Ejemplo de configuración
├── gva_gis_client.py     # Cliente Python standalone (opcional)
├── examples.py           # Ejemplos de uso del cliente (opcional)
└── README.md
```

## Uso Standalone (sin MCP)

También incluye un cliente Python que puedes usar directamente:

```python
from gva_gis_client import GVAGISClient

client = GVAGISClient()

# Obtener info
info = client.get_layer_info()

# Consultar
result = client.query(where="1=1", result_record_count=10)

# Contar
count = client.count_features()
```

Ver `examples.py` para más ejemplos.

## Parámetros de Consulta SQL

### Operadores básicos
```sql
CAMPO = 'valor'
CAMPO > 100
CAMPO >= 100 AND CAMPO <= 200
CAMPO IN ('valor1', 'valor2')
CAMPO LIKE '%texto%'
CAMPO IS NULL
CAMPO IS NOT NULL
```

### Operadores lógicos
```sql
CAMPO1 = 'A' AND CAMPO2 > 10
CAMPO1 = 'A' OR CAMPO1 = 'B'
NOT (CAMPO = 'valor')
```

## Debugging

Para ver los logs del servidor MCP y probar que funciona:

```bash
# Opción 1: Ejecutar con uvx (recomendado)
uvx mcp4gva

# Opción 2: Ejecutar con uvx desde directorio local
uvx --from . mcp4gva

# Opción 3: Ejecutar directamente con Python
python -m mcp4gva.server

# Opción 4: Con logging detallado
PYTHONPATH=. python -m mcp4gva.server
```

Los logs aparecerán en la salida estándar. El servidor MCP se comunica por stdio, así que verás JSON si funciona correctamente.

### Verificar que uv/uvx está instalado

```bash
uv --version
uvx --version
```

## Limitaciones

- La API puede tener restricciones geográficas (IP)
- Timeout de 30 segundos por petición
- Límite de registros por consulta (usar paginación para grandes datasets)

## Solución de Problemas

### El servidor no aparece en Claude Desktop

1. Verifica que `uv` esté instalado: `uvx --version`
2. Verifica que el archivo de configuración esté en la ubicación correcta
3. Revisa que la sintaxis JSON sea válida (usa un validador JSON)
4. Reinicia Claude Desktop **completamente** (no solo cerrar ventana)
5. Revisa los logs de Claude Desktop:
   - **macOS:** `~/Library/Logs/Claude/`
   - **Windows:** `%APPDATA%\Claude\logs\`
   - **Linux:** `~/.config/Claude/logs/`

### Probar el servidor manualmente

```bash
# Desde el directorio del proyecto
uvx --from . mcp4gva
```

Deberías ver que el proceso se inicia y espera entrada JSON en stdin. Si ves un error, revísalo.

### Error: "command not found: uvx"

Necesitas instalar `uv`:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Luego reinicia tu terminal o ejecuta:
source ~/.bashrc  # o ~/.zshrc si usas zsh
```

### Error 403 / Access Denied desde la API

La API tiene restricciones geográficas. Asegúrate de que tu IP tiene acceso (normalmente funciona desde España).

### El paquete no se encuentra con uvx

Si usas desarrollo local, asegúrate de usar `--from`:

```json
{
  "command": "uvx",
  "args": ["--from", "/ruta/absoluta/a/mcp4gva", "mcp4gva"]
}
```

### Verificar dependencias

```bash
# Con uvx (crea entorno temporal y verifica)
uvx --from . mcp4gva --help

# Con pip (si instalaste localmente)
python -c "import mcp; import requests; print('Dependencias OK')"
```

## Recursos

- [Documentación MCP](https://modelcontextprotocol.io/)
- [Documentación ArcGIS REST API](https://developers.arcgis.com/rest/)
- [API GVA GIS](https://gvagis.icv.gva.es/server/rest/services)
- [Instituto Cartográfico Valenciano](https://icv.gva.es/)

## Licencia

Este proyecto es código abierto. Los datos pertenecen a la Generalitat Valenciana.
