#!/usr/bin/env python3
"""
MCP Server for GVA GIS ArcGIS API
Minimal implementation to access Suelo_actividades FeatureServer
"""

import json
import logging
from typing import Any
import requests

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp4gva")

# API Configuration
BASE_URL = "https://gvagis.icv.gva.es/server/rest/services/Hosted/Suelo_actividades/FeatureServer"
LAYER_ID = 2

# Create server instance
app = Server("mcp4gva")


def make_request(url: str, params: dict) -> dict:
    """Make HTTP request to the API with browser-like headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="gva_layer_info",
            description="Get metadata information about the GVA GIS layer (fields, geometry type, spatial reference, extent)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="gva_query",
            description="Query features from the GVA GIS layer with SQL-like WHERE clause and optional parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "where": {
                        "type": "string",
                        "description": "SQL WHERE clause (e.g., '1=1' for all, 'MUNICIPIO=\"Valencia\"')",
                        "default": "1=1"
                    },
                    "out_fields": {
                        "type": "string",
                        "description": "Comma-separated field names or '*' for all fields",
                        "default": "*"
                    },
                    "return_geometry": {
                        "type": "boolean",
                        "description": "Whether to return geometry data",
                        "default": True
                    },
                    "result_record_count": {
                        "type": "integer",
                        "description": "Maximum number of records to return",
                        "default": 10
                    },
                    "result_offset": {
                        "type": "integer",
                        "description": "Offset for pagination",
                        "default": 0
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gva_count",
            description="Count features matching a WHERE clause",
            inputSchema={
                "type": "object",
                "properties": {
                    "where": {
                        "type": "string",
                        "description": "SQL WHERE clause (e.g., '1=1' for all)",
                        "default": "1=1"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gva_export_geojson",
            description="Export features to GeoJSON format",
            inputSchema={
                "type": "object",
                "properties": {
                    "where": {
                        "type": "string",
                        "description": "SQL WHERE clause to filter features",
                        "default": "1=1"
                    },
                    "out_fields": {
                        "type": "string",
                        "description": "Comma-separated field names or '*' for all",
                        "default": "*"
                    },
                    "result_record_count": {
                        "type": "integer",
                        "description": "Maximum number of features to export",
                        "default": 100
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    try:
        if name == "gva_layer_info":
            # Get layer metadata
            url = f"{BASE_URL}/{LAYER_ID}"
            params = {'f': 'json'}
            data = make_request(url, params)

            # Format response
            result = {
                "name": data.get("name"),
                "type": data.get("type"),
                "geometryType": data.get("geometryType"),
                "spatialReference": data.get("spatialReference"),
                "extent": data.get("extent"),
                "fields": data.get("fields", [])
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        elif name == "gva_query":
            # Query features
            url = f"{BASE_URL}/{LAYER_ID}/query"
            params = {
                'where': arguments.get('where', '1=1'),
                'outFields': arguments.get('out_fields', '*'),
                'returnGeometry': str(arguments.get('return_geometry', True)).lower(),
                'resultRecordCount': arguments.get('result_record_count', 10),
                'resultOffset': arguments.get('result_offset', 0),
                'f': 'json'
            }

            data = make_request(url, params)

            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2, ensure_ascii=False)
            )]

        elif name == "gva_count":
            # Count features
            url = f"{BASE_URL}/{LAYER_ID}/query"
            params = {
                'where': arguments.get('where', '1=1'),
                'returnCountOnly': 'true',
                'f': 'json'
            }

            data = make_request(url, params)
            count = data.get('count', 0)

            return [TextContent(
                type="text",
                text=f"Total features matching query: {count}"
            )]

        elif name == "gva_export_geojson":
            # Export to GeoJSON
            url = f"{BASE_URL}/{LAYER_ID}/query"
            params = {
                'where': arguments.get('where', '1=1'),
                'outFields': arguments.get('out_fields', '*'),
                'returnGeometry': 'true',
                'resultRecordCount': arguments.get('result_record_count', 100),
                'f': 'json'
            }

            data = make_request(url, params)

            # Convert to GeoJSON
            features = data.get('features', [])
            geojson_features = []

            for feature in features:
                geojson_feature = {
                    'type': 'Feature',
                    'properties': feature.get('attributes', {}),
                    'geometry': feature.get('geometry', {})
                }
                geojson_features.append(geojson_feature)

            geojson = {
                'type': 'FeatureCollection',
                'features': geojson_features
            }

            return [TextContent(
                type="text",
                text=json.dumps(geojson, indent=2, ensure_ascii=False)
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Entry point for the server"""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run()
