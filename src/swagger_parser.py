from typing import Dict, Any, List
from pydantic import BaseModel

class EndpointInfo(BaseModel):
    path: str
    method: str
    summary: str = ""
    description: str = ""
    parameters: List[Dict[str, Any]] = []
    request_body: Dict[str, Any] = {}
    responses: Dict[str, Any] = {}

class SwaggerParser:
    def __init__(self, swagger_content: Dict[str, Any]):
        self.swagger_content = swagger_content
        self.base_path = swagger_content.get('basePath', '')
        self.endpoints = self._parse_endpoints()

    def _parse_endpoints(self) -> List[EndpointInfo]:
        """Parse all endpoints from the swagger specification"""
        endpoints = []
        paths = self.swagger_content.get('paths', {})
        
        for path, path_info in paths.items():
            for method, method_info in path_info.items():
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                
                endpoint = EndpointInfo(
                    path=path,
                    method=method.upper(),
                    summary=method_info.get('summary', ''),
                    description=method_info.get('description', ''),
                    parameters=method_info.get('parameters', []),
                    request_body=method_info.get('requestBody', {}),
                    responses=method_info.get('responses', {})
                )
                endpoints.append(endpoint)
        
        return endpoints

    def get_endpoint_details(self, path: str, method: str) -> EndpointInfo:
        """Get detailed information about a specific endpoint"""
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method.lower() == method.lower():
                return endpoint
        raise ValueError(f"Endpoint not found: {method.upper()} {path}")

    def get_endpoint_summary(self) -> List[Dict[str, str]]:
        """Get a summary of all endpoints"""
        return [
            {
                'path': endpoint.path,
                'method': endpoint.method,
                'summary': endpoint.summary
            }
            for endpoint in self.endpoints
        ]
