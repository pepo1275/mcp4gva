# MCP4GVA - TypeScript Implementation

MCP server for GVA GIS ArcGIS API - TypeScript/Node.js implementation.

**Endpoint:** `https://gvagis.icv.gva.es/server/rest/services/Hosted/Suelo_actividades/FeatureServer/2`

## Installation

### Prerequisites

- Node.js 18 or higher
- npm or npx

### Option 1: Use with `npx` (RECOMMENDED)

No installation needed! Claude Desktop will download and run automatically.

#### Configure Claude Desktop

Edit your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "mcp4gva-ts": {
      "command": "npx",
      "args": ["-y", "mcp4gva-typescript"]
    }
  }
}
```

**Note:** For published packages. For local development, use Option 2.

### Option 2: Local Development

If you're developing or modifying the code:

```bash
# 1. Clone/navigate to the repository
cd typescript

# 2. Install dependencies
npm install

# 3. Build the project
npm run build

# 4. Configure Claude Desktop
```

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp4gva-ts": {
      "command": "node",
      "args": ["/absolute/path/to/mcp4gva/typescript/build/index.js"]
    }
  }
}
```

### Option 3: Install Globally

```bash
# Install globally
cd typescript
npm install -g .

# Configure Claude Desktop
{
  "mcpServers": {
    "mcp4gva-ts": {
      "command": "mcp4gva-ts"
    }
  }
}
```

### Restart Claude Desktop

Restart Claude Desktop to load the new MCP server.

## Available Tools

The server exposes 4 tools that Claude can use:

### 1. `gva_layer_info`

Get layer metadata (fields, geometry type, spatial reference, extent).

**Parameters:** None

**Example in Claude:**
```
Use gva_layer_info to see what fields the GVA GIS layer has
```

### 2. `gva_query`

Query features from the layer with SQL filters.

**Parameters:**
- `where` (string, default: "1=1"): SQL WHERE clause
- `out_fields` (string, default: "*"): Fields to return (comma-separated or "*")
- `return_geometry` (boolean, default: true): Return geometry
- `result_record_count` (number, default: 10): Maximum records
- `result_offset` (number, default: 0): Offset for pagination

**Example in Claude:**
```
Use gva_query to get the first 5 records where MUNICIPIO='Valencia'
```

### 3. `gva_count`

Count features matching a condition.

**Parameters:**
- `where` (string, default: "1=1"): SQL WHERE clause

**Example in Claude:**
```
Count how many records there are in total with gva_count
```

### 4. `gva_export_geojson`

Export features to GeoJSON format.

**Parameters:**
- `where` (string, default: "1=1"): SQL filter
- `out_fields` (string, default: "*"): Fields to include
- `result_record_count` (number, default: 100): Maximum features

**Example in Claude:**
```
Export the first 20 records to GeoJSON
```

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Watch mode (rebuild on changes)
npm run watch

# Run locally
npm run dev
```

## Debugging

To test the server manually:

```bash
# Option 1: Run with npx
npx -y mcp4gva-typescript

# Option 2: Run built version
npm run build
node build/index.js

# Option 3: Run with npm
npm run dev
```

The server communicates via stdio. You should see JSON output if it's working correctly.

### Verify Node.js version

```bash
node --version  # Should be 18 or higher
npm --version
```

## Project Structure

```
typescript/
├── src/
│   └── index.ts         # Main MCP server implementation
├── build/               # Compiled JavaScript (generated)
├── package.json         # Node.js package configuration
├── tsconfig.json        # TypeScript configuration
└── README.md
```

## Comparison with Python Version

| Aspect | Python (uvx) | TypeScript (npx) |
|--------|-------------|------------------|
| **Runtime** | Python 3.10+ | Node.js 18+ |
| **Package Manager** | uv/pip | npm/npx |
| **SDK** | mcp (Python) | @modelcontextprotocol/sdk |
| **Type Safety** | Type hints | Full TypeScript |
| **Build Step** | No | Yes (tsc) |
| **Startup** | Slightly faster | Fast |
| **Dependencies** | requests | node-fetch |

## SQL Query Examples

### Basic operators
```sql
CAMPO = 'value'
CAMPO > 100
CAMPO >= 100 AND CAMPO <= 200
CAMPO IN ('value1', 'value2')
CAMPO LIKE '%text%'
CAMPO IS NULL
CAMPO IS NOT NULL
```

### Logical operators
```sql
CAMPO1 = 'A' AND CAMPO2 > 10
CAMPO1 = 'A' OR CAMPO1 = 'B'
NOT (CAMPO = 'value')
```

## Troubleshooting

### Server doesn't appear in Claude Desktop

1. Verify Node.js is installed: `node --version`
2. Check that config file is in the correct location
3. Validate JSON syntax
4. Restart Claude Desktop **completely**
5. Check Claude Desktop logs:
   - **macOS:** `~/Library/Logs/Claude/`
   - **Windows:** `%APPDATA%\Claude\logs\`
   - **Linux:** `~/.config/Claude/logs/`

### Test server manually

```bash
# From the typescript directory
npm run dev
```

You should see the process start and wait for JSON input on stdin.

### Error: "command not found: npx"

Install Node.js from https://nodejs.org/ or use nvm:

```bash
# With nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

### Build errors

```bash
# Clean and rebuild
rm -rf build node_modules
npm install
npm run build
```

### Error 403 / Access Denied from API

The API has geographic restrictions. Ensure your IP has access (typically works from Spain).

### Package not found with npx

For local development, use the full path:

```json
{
  "command": "node",
  "args": ["/absolute/path/to/typescript/build/index.js"]
}
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [ArcGIS REST API Docs](https://developers.arcgis.com/rest/)
- [GVA GIS API](https://gvagis.icv.gva.es/server/rest/services)
- [Instituto Cartográfico Valenciano](https://icv.gva.es/)

## License

This project is open source. Data belongs to Generalitat Valenciana.
