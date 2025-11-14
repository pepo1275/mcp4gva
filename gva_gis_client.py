"""
Cliente para acceder a la API de GVA GIS - Suelo de Actividades
https://gvagis.icv.gva.es/server/rest/services/Hosted/Suelo_actividades/FeatureServer/2
"""

import requests
import json
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode


class GVAGISClient:
    """Cliente para acceder a la API de GVA GIS FeatureServer"""

    BASE_URL = "https://gvagis.icv.gva.es/server/rest/services/Hosted/Suelo_actividades/FeatureServer"
    LAYER_ID = 2

    def __init__(self, timeout: int = 30):
        """
        Inicializa el cliente GVA GIS

        Args:
            timeout: Timeout en segundos para las peticiones HTTP
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
        })

    def get_layer_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la capa (metadatos, campos, etc.)

        Returns:
            Dict con la información de la capa
        """
        url = f"{self.BASE_URL}/{self.LAYER_ID}"
        params = {'f': 'json'}

        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def query(
        self,
        where: str = "1=1",
        out_fields: str = "*",
        return_geometry: bool = True,
        out_sr: Optional[int] = None,
        geometry: Optional[str] = None,
        geometry_type: Optional[str] = None,
        spatial_rel: Optional[str] = None,
        result_offset: Optional[int] = None,
        result_record_count: Optional[int] = None,
        order_by_fields: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Realiza una consulta a la capa de FeatureServer

        Args:
            where: Cláusula WHERE SQL (ej: "1=1" para todos, "MUNICIPIO='Valencia'")
            out_fields: Campos a devolver separados por coma (ej: "MUNICIPIO,SUPERFICIE" o "*")
            return_geometry: Si devolver geometría
            out_sr: Sistema de referencia espacial de salida (WKID)
            geometry: Geometría para filtro espacial (formato JSON)
            geometry_type: Tipo de geometría (esriGeometryPoint, esriGeometryPolygon, etc.)
            spatial_rel: Relación espacial (esriSpatialRelIntersects, esriSpatialRelContains, etc.)
            result_offset: Offset para paginación
            result_record_count: Número máximo de registros a devolver
            order_by_fields: Campos para ordenar (ej: "MUNICIPIO ASC")
            **kwargs: Parámetros adicionales de la API

        Returns:
            Dict con los features resultantes
        """
        url = f"{self.BASE_URL}/{self.LAYER_ID}/query"

        params = {
            'where': where,
            'outFields': out_fields,
            'returnGeometry': str(return_geometry).lower(),
            'f': 'json'
        }

        # Agregar parámetros opcionales
        if out_sr is not None:
            params['outSR'] = out_sr
        if geometry is not None:
            params['geometry'] = geometry
        if geometry_type is not None:
            params['geometryType'] = geometry_type
        if spatial_rel is not None:
            params['spatialRel'] = spatial_rel
        if result_offset is not None:
            params['resultOffset'] = result_offset
        if result_record_count is not None:
            params['resultRecordCount'] = result_record_count
        if order_by_fields is not None:
            params['orderByFields'] = order_by_fields

        # Agregar parámetros adicionales
        params.update(kwargs)

        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def get_all_features(
        self,
        where: str = "1=1",
        out_fields: str = "*",
        batch_size: int = 1000,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los features usando paginación automática

        Args:
            where: Cláusula WHERE SQL
            out_fields: Campos a devolver
            batch_size: Tamaño de lote para paginación
            **kwargs: Parámetros adicionales para query()

        Returns:
            Lista de todos los features
        """
        all_features = []
        offset = 0

        while True:
            result = self.query(
                where=where,
                out_fields=out_fields,
                result_offset=offset,
                result_record_count=batch_size,
                **kwargs
            )

            features = result.get('features', [])
            if not features:
                break

            all_features.extend(features)
            offset += len(features)

            # Si recibimos menos features que el batch_size, hemos terminado
            if len(features) < batch_size:
                break

        return all_features

    def query_by_municipality(self, municipality: str, **kwargs) -> Dict[str, Any]:
        """
        Consulta features por municipio

        Args:
            municipality: Nombre del municipio
            **kwargs: Parámetros adicionales para query()

        Returns:
            Dict con los features del municipio
        """
        where = f"MUNICIPIO='{municipality}'"
        return self.query(where=where, **kwargs)

    def count_features(self, where: str = "1=1") -> int:
        """
        Cuenta el número de features que cumplen una condición

        Args:
            where: Cláusula WHERE SQL

        Returns:
            Número de features
        """
        url = f"{self.BASE_URL}/{self.LAYER_ID}/query"
        params = {
            'where': where,
            'returnCountOnly': 'true',
            'f': 'json'
        }

        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        result = response.json()
        return result.get('count', 0)

    def get_unique_values(self, field: str, where: str = "1=1") -> List[Any]:
        """
        Obtiene valores únicos de un campo

        Args:
            field: Nombre del campo
            where: Cláusula WHERE SQL para filtrar

        Returns:
            Lista de valores únicos
        """
        result = self.query(
            where=where,
            out_fields=field,
            return_geometry=False,
            order_by_fields=f"{field} ASC"
        )

        features = result.get('features', [])
        unique_values = set()

        for feature in features:
            value = feature.get('attributes', {}).get(field)
            if value is not None:
                unique_values.add(value)

        return sorted(list(unique_values))

    def export_to_geojson(
        self,
        where: str = "1=1",
        out_fields: str = "*",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Exporta features a formato GeoJSON

        Args:
            where: Cláusula WHERE SQL
            out_fields: Campos a devolver
            **kwargs: Parámetros adicionales para query()

        Returns:
            FeatureCollection en formato GeoJSON
        """
        result = self.query(
            where=where,
            out_fields=out_fields,
            return_geometry=True,
            **kwargs
        )

        features = result.get('features', [])

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

        return geojson


def main():
    """Ejemplo de uso del cliente"""
    client = GVAGISClient()

    print("=== Información de la capa ===")
    try:
        info = client.get_layer_info()
        print(f"Nombre: {info.get('name')}")
        print(f"Tipo de geometría: {info.get('geometryType')}")
        print(f"\nCampos disponibles:")
        for field in info.get('fields', []):
            print(f"  - {field.get('name')} ({field.get('type')})")
    except Exception as e:
        print(f"Error obteniendo información: {e}")

    print("\n=== Contando features ===")
    try:
        count = client.count_features()
        print(f"Total de features: {count}")
    except Exception as e:
        print(f"Error contando: {e}")

    print("\n=== Consultando primeros 5 features ===")
    try:
        result = client.query(result_record_count=5)
        for i, feature in enumerate(result.get('features', []), 1):
            print(f"\nFeature {i}:")
            print(json.dumps(feature.get('attributes', {}), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error en consulta: {e}")


if __name__ == "__main__":
    main()
