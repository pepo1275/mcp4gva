"""
Ejemplos de uso del cliente GVA GIS
"""

from gva_gis_client import GVAGISClient
import json


def example_basic_query():
    """Ejemplo 1: Consulta básica"""
    print("=" * 60)
    print("EJEMPLO 1: Consulta básica - Primeros 10 registros")
    print("=" * 60)

    client = GVAGISClient()

    result = client.query(
        where="1=1",
        out_fields="*",
        result_record_count=10
    )

    print(f"Número de features: {len(result.get('features', []))}")
    print("\nPrimer feature:")
    if result.get('features'):
        print(json.dumps(result['features'][0], indent=2, ensure_ascii=False))


def example_count_features():
    """Ejemplo 2: Contar features"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Contar features totales")
    print("=" * 60)

    client = GVAGISClient()

    total = client.count_features()
    print(f"Total de features en la capa: {total}")


def example_filter_by_field():
    """Ejemplo 3: Filtrar por campo específico"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Filtrar por municipio (si existe el campo)")
    print("=" * 60)

    client = GVAGISClient()

    # Primero, obtener información de campos
    info = client.get_layer_info()
    fields = [f['name'] for f in info.get('fields', [])]
    print(f"Campos disponibles: {', '.join(fields)}")

    # Ejemplo de consulta con filtro
    # Ajusta el nombre del campo según lo que veas arriba
    if 'MUNICIPIO' in fields:
        result = client.query(
            where="MUNICIPIO='Valencia'",
            out_fields="*",
            result_record_count=5
        )
        print(f"\nFeatures encontrados: {len(result.get('features', []))}")


def example_pagination():
    """Ejemplo 4: Paginación de resultados"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Obtener features con paginación")
    print("=" * 60)

    client = GVAGISClient()

    # Obtener features de 10 en 10
    batch_size = 10
    max_batches = 3

    for i in range(max_batches):
        offset = i * batch_size
        result = client.query(
            where="1=1",
            out_fields="OBJECTID",
            result_offset=offset,
            result_record_count=batch_size,
            return_geometry=False
        )

        features = result.get('features', [])
        if not features:
            break

        print(f"\nBatch {i + 1} (offset {offset}): {len(features)} features")
        ids = [f['attributes']['OBJECTID'] for f in features if 'OBJECTID' in f['attributes']]
        print(f"  IDs: {ids}")


def example_get_all_features():
    """Ejemplo 5: Obtener todos los features automáticamente"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Obtener todos los features (paginación automática)")
    print("=" * 60)

    client = GVAGISClient()

    print("Obteniendo todos los features...")
    all_features = client.get_all_features(
        where="1=1",
        out_fields="OBJECTID",
        return_geometry=False,
        batch_size=100
    )

    print(f"Total de features obtenidos: {len(all_features)}")


def example_spatial_query():
    """Ejemplo 6: Consulta espacial con geometría"""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: Consulta espacial (ejemplo de bbox)")
    print("=" * 60)

    client = GVAGISClient()

    # Ejemplo de bounding box (ajusta las coordenadas a tu área de interés)
    # Formato: xmin, ymin, xmax, ymax
    bbox = json.dumps({
        'xmin': -0.5,
        'ymin': 39.3,
        'xmax': -0.3,
        'ymax': 39.5,
        'spatialReference': {'wkid': 4326}
    })

    result = client.query(
        where="1=1",
        geometry=bbox,
        geometry_type="esriGeometryEnvelope",
        spatial_rel="esriSpatialRelIntersects",
        result_record_count=10
    )

    print(f"Features dentro del bbox: {len(result.get('features', []))}")


def example_export_geojson():
    """Ejemplo 7: Exportar a GeoJSON"""
    print("\n" + "=" * 60)
    print("EJEMPLO 7: Exportar a GeoJSON")
    print("=" * 60)

    client = GVAGISClient()

    geojson = client.export_to_geojson(
        where="1=1",
        result_record_count=5
    )

    print(f"FeatureCollection con {len(geojson['features'])} features")

    # Guardar a archivo
    output_file = "output.geojson"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"GeoJSON guardado en: {output_file}")


def example_get_unique_values():
    """Ejemplo 8: Obtener valores únicos de un campo"""
    print("\n" + "=" * 60)
    print("EJEMPLO 8: Valores únicos de un campo")
    print("=" * 60)

    client = GVAGISClient()

    # Primero ver qué campos hay
    info = client.get_layer_info()
    fields = [f['name'] for f in info.get('fields', []) if f['type'] in ['esriFieldTypeString', 'esriFieldTypeInteger']]

    if fields:
        field_name = fields[0]  # Tomar el primer campo disponible
        print(f"Obteniendo valores únicos del campo: {field_name}")

        # Limitar a primeros 100 registros para el ejemplo
        result = client.query(
            where="1=1",
            out_fields=field_name,
            result_record_count=100,
            return_geometry=False
        )

        unique_values = set()
        for feature in result.get('features', []):
            value = feature.get('attributes', {}).get(field_name)
            if value is not None:
                unique_values.add(value)

        print(f"Valores únicos encontrados: {sorted(list(unique_values))}")


def example_layer_info():
    """Ejemplo 9: Información detallada de la capa"""
    print("\n" + "=" * 60)
    print("EJEMPLO 9: Información detallada de la capa")
    print("=" * 60)

    client = GVAGISClient()

    info = client.get_layer_info()

    print(f"Nombre: {info.get('name')}")
    print(f"Tipo: {info.get('type')}")
    print(f"Geometría: {info.get('geometryType')}")
    print(f"Tiene Z: {info.get('hasZ')}")
    print(f"Tiene M: {info.get('hasM')}")

    print(f"\nSistema de referencia espacial:")
    sr = info.get('spatialReference', {})
    print(f"  WKID: {sr.get('wkid')}")
    print(f"  Latest WKID: {sr.get('latestWkid')}")

    print(f"\nExtensión:")
    extent = info.get('extent', {})
    print(f"  xmin: {extent.get('xmin')}")
    print(f"  ymin: {extent.get('ymin')}")
    print(f"  xmax: {extent.get('xmax')}")
    print(f"  ymax: {extent.get('ymax')}")

    print(f"\nCampos ({len(info.get('fields', []))}):")
    for field in info.get('fields', []):
        nullable = "nullable" if field.get('nullable') else "not null"
        print(f"  - {field.get('name'):30} {field.get('type'):25} ({nullable})")


def main():
    """Ejecutar todos los ejemplos"""
    client = GVAGISClient()

    try:
        # Verificar conexión
        print("Verificando conexión a la API...")
        info = client.get_layer_info()
        print(f"✓ Conexión exitosa a: {info.get('name')}\n")

        # Ejecutar ejemplos
        example_layer_info()
        example_count_features()
        example_basic_query()
        example_filter_by_field()
        example_pagination()
        example_get_unique_values()
        example_spatial_query()
        example_export_geojson()

        print("\n" + "=" * 60)
        print("Ejemplos completados")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        print("\nAsegúrate de que tienes acceso a la API desde tu ubicación.")


if __name__ == "__main__":
    main()
