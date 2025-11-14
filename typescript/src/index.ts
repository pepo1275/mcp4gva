#!/usr/bin/env node
/**
 * MCP Server for GVA GIS ArcGIS API - TypeScript Implementation
 * Minimal implementation to access Suelo_actividades FeatureServer
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";

// API Configuration
const BASE_URL = "https://gvagis.icv.gva.es/server/rest/services/Hosted/Suelo_actividades/FeatureServer";
const LAYER_ID = 2;

// Types
interface RequestParams {
  [key: string]: string | number | boolean;
}

interface ApiResponse {
  [key: string]: any;
}

interface QueryArguments {
  where?: string;
  out_fields?: string;
  return_geometry?: boolean;
  result_record_count?: number;
  result_offset?: number;
}

interface CountArguments {
  where?: string;
}

interface ExportGeoJsonArguments {
  where?: string;
  out_fields?: string;
  result_record_count?: number;
}

/**
 * Make HTTP request to the API with browser-like headers
 */
async function makeRequest(url: string, params: RequestParams): Promise<ApiResponse> {
  const queryParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    queryParams.append(key, String(value));
  }

  const fullUrl = `${url}?${queryParams.toString()}`;

  const response = await fetch(fullUrl, {
    headers: {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "application/json, text/plain, */*",
      "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json() as ApiResponse;
}

/**
 * Create and configure the MCP server
 */
function createServer(): Server {
  const server = new Server(
    {
      name: "mcp4gva-typescript",
      version: "0.1.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: "gva_layer_info",
          description: "Get metadata information about the GVA GIS layer (fields, geometry type, spatial reference, extent)",
          inputSchema: {
            type: "object",
            properties: {},
            required: [],
          },
        },
        {
          name: "gva_query",
          description: "Query features from the GVA GIS layer with SQL-like WHERE clause and optional parameters",
          inputSchema: {
            type: "object",
            properties: {
              where: {
                type: "string",
                description: 'SQL WHERE clause (e.g., "1=1" for all, "MUNICIPIO=\'Valencia\'")',
                default: "1=1",
              },
              out_fields: {
                type: "string",
                description: "Comma-separated field names or '*' for all fields",
                default: "*",
              },
              return_geometry: {
                type: "boolean",
                description: "Whether to return geometry data",
                default: true,
              },
              result_record_count: {
                type: "number",
                description: "Maximum number of records to return",
                default: 10,
              },
              result_offset: {
                type: "number",
                description: "Offset for pagination",
                default: 0,
              },
            },
            required: [],
          },
        },
        {
          name: "gva_count",
          description: "Count features matching a WHERE clause",
          inputSchema: {
            type: "object",
            properties: {
              where: {
                type: "string",
                description: 'SQL WHERE clause (e.g., "1=1" for all)',
                default: "1=1",
              },
            },
            required: [],
          },
        },
        {
          name: "gva_export_geojson",
          description: "Export features to GeoJSON format",
          inputSchema: {
            type: "object",
            properties: {
              where: {
                type: "string",
                description: "SQL WHERE clause to filter features",
                default: "1=1",
              },
              out_fields: {
                type: "string",
                description: "Comma-separated field names or '*' for all",
                default: "*",
              },
              result_record_count: {
                type: "number",
                description: "Maximum number of features to export",
                default: 100,
              },
            },
            required: [],
          },
        },
      ] as Tool[],
    };
  });

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case "gva_layer_info": {
          // Get layer metadata
          const url = `${BASE_URL}/${LAYER_ID}`;
          const params = { f: "json" };
          const data = await makeRequest(url, params);

          // Format response
          const result = {
            name: data.name,
            type: data.type,
            geometryType: data.geometryType,
            spatialReference: data.spatialReference,
            extent: data.extent,
            fields: data.fields || [],
          };

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case "gva_query": {
          // Query features
          const queryArgs = args as QueryArguments;
          const url = `${BASE_URL}/${LAYER_ID}/query`;
          const params: RequestParams = {
            where: queryArgs.where || "1=1",
            outFields: queryArgs.out_fields || "*",
            returnGeometry: String(queryArgs.return_geometry ?? true).toLowerCase(),
            resultRecordCount: queryArgs.result_record_count || 10,
            resultOffset: queryArgs.result_offset || 0,
            f: "json",
          };

          const data = await makeRequest(url, params);

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(data, null, 2),
              },
            ],
          };
        }

        case "gva_count": {
          // Count features
          const countArgs = args as CountArguments;
          const url = `${BASE_URL}/${LAYER_ID}/query`;
          const params: RequestParams = {
            where: countArgs.where || "1=1",
            returnCountOnly: "true",
            f: "json",
          };

          const data = await makeRequest(url, params);
          const count = data.count || 0;

          return {
            content: [
              {
                type: "text",
                text: `Total features matching query: ${count}`,
              },
            ],
          };
        }

        case "gva_export_geojson": {
          // Export to GeoJSON
          const exportArgs = args as ExportGeoJsonArguments;
          const url = `${BASE_URL}/${LAYER_ID}/query`;
          const params: RequestParams = {
            where: exportArgs.where || "1=1",
            outFields: exportArgs.out_fields || "*",
            returnGeometry: "true",
            resultRecordCount: exportArgs.result_record_count || 100,
            f: "json",
          };

          const data = await makeRequest(url, params);

          // Convert to GeoJSON
          const features = (data.features || []).map((feature: any) => ({
            type: "Feature",
            properties: feature.attributes || {},
            geometry: feature.geometry || {},
          }));

          const geojson = {
            type: "FeatureCollection",
            features,
          };

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(geojson, null, 2),
              },
            ],
          };
        }

        default:
          return {
            content: [
              {
                type: "text",
                text: `Unknown tool: ${name}`,
              },
            ],
            isError: true,
          };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`Error in ${name}:`, errorMessage);

      return {
        content: [
          {
            type: "text",
            text: `Error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  });

  return server;
}

/**
 * Main entry point
 */
async function main() {
  const server = createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);

  console.error("MCP4GVA TypeScript server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
