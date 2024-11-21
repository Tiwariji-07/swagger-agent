import requests
from typing import Dict, Any, Optional
from swagger_parser import EndpointInfo

class APIInteraction:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def _build_url(self, path: str) -> str:
        """Build the full URL for the API request"""
        return f"{self.base_url}{path}"
    
    def _prepare_parameters(self, endpoint: EndpointInfo, parameters: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """Prepare parameters for different locations (query, path, header)"""
        query_params = {}
        path_params = {}
        headers = {}
        
        for param in endpoint.parameters:
            param_name = param['name']
            if param_name not in parameters:
                continue
                
            param_value = parameters[param_name]
            param_in = param['in']
            
            if param_in == 'query':
                query_params[param_name] = param_value
            elif param_in == 'path':
                path_params[param_name] = param_value
            elif param_in == 'header':
                headers[param_name] = param_value
                
        return query_params, path_params, headers
    
    def _substitute_path_parameters(self, path: str, path_params: Dict[str, Any]) -> str:
        """Substitute path parameters in the URL"""
        for param_name, param_value in path_params.items():
            path = path.replace(f"{{{param_name}}}", str(param_value))
        return path
    
    async def execute_request(
        self,
        endpoint: EndpointInfo,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Execute the API request"""
        # Prepare parameters
        query_params, path_params, headers = self._prepare_parameters(endpoint, parameters)
        
        # Build URL with path parameters
        path = self._substitute_path_parameters(endpoint.path, path_params)
        url = self._build_url(path)
        
        # Get request method
        method = endpoint.method.lower()
        
        # Prepare request kwargs
        request_kwargs = {
            'url': url,
            'params': query_params,
            'headers': headers,
            'timeout': timeout
        }
        
        # Add request body if present
        if 'body' in parameters:
            request_kwargs['json'] = parameters['body']
        
        try:
            response = requests.request(method, **request_kwargs)
            response.raise_for_status()
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json() if response.content else None
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'response': getattr(e.response, 'text', None)
            }
