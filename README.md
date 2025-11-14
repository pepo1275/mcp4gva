# MCP4GVA - MCP Server para GVA GIS

Servidor MCP (Model Context Protocol) mínimo para acceder a la API de GVA GIS (Generalitat Valenciana) - Servicio de Suelo de Actividades.

**Endpoint:** `https://gvagis.icv.gva.es/server/rest/services/Hosted/Suelo_actividades/FeatureServer/2`

## ¿Qué es esto?

Un servidor MCP que expone la API de ArcGIS REST de la Generalitat Valenciana para que Claude Desktop (y otras aplicaciones MCP) puedan consultar datos de suelo de actividades directamente.

## Instalación

### 1. Instalar el paquete

```bash
# Opción 1: Instalación en desarrollo
cd mcp4gva
pip install -e .

# Opción 2: Instalar dependencias manualmente
pip install mcp>=0.9.0 requests>=2.31.0
```

### 2. Configurar Claude Desktop

Edita el archivo de configuración de Claude Desktop:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Añade la configuración del servidor MCP:

```json
{
  "mcpServers": {
    "mcp4gva": {
      "command": "python",
      "args": [
        "-m",
        "mcp4gva.server"
      ]
    }
  }
}
```

O si instalaste en modo desarrollo, puedes usar la ruta absoluta:

```json
{
  "mcpServers": {
    "mcp4gva": {
      "command": "python",
      "args": [
        "/ruta/completa/a/mcp4gva/mcp4gva/server.py"
      ]
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

Para ver los logs del servidor MCP:

```bash
# Ejecutar el servidor manualmente
python -m mcp4gva.server

# O con logging detallado
PYTHONPATH=. python -m mcp4gva.server
```

Los logs aparecerán en la salida estándar.

## Limitaciones

- La API puede tener restricciones geográficas (IP)
- Timeout de 30 segundos por petición
- Límite de registros por consulta (usar paginación para grandes datasets)

## Solución de Problemas

### El servidor no aparece en Claude Desktop

1. Verifica que el archivo de configuración esté en la ubicación correcta
2. Revisa que la sintaxis JSON sea válida
3. Reinicia Claude Desktop completamente
4. Verifica que `mcp` esté instalado: `pip show mcp`

### Error 403 / Access Denied

La API tiene restricciones geográficas. Asegúrate de que tu IP tiene acceso (normalmente funciona desde España).

### El comando no funciona

Verifica la instalación:
```bash
python -c "import mcp; import requests; print('OK')"
```

## Recursos

- [Documentación MCP](https://modelcontextprotocol.io/)
- [Documentación ArcGIS REST API](https://developers.arcgis.com/rest/)
- [API GVA GIS](https://gvagis.icv.gva.es/server/rest/services)
- [Instituto Cartográfico Valenciano](https://icv.gva.es/)

## Licencia

Este proyecto es código abierto. Los datos pertenecen a la Generalitat Valenciana.
