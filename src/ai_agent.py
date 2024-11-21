import os
import groq
from typing import Dict, Any, List, Optional
from swagger_parser import SwaggerParser, EndpointInfo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAgent:
    def __init__(self, model_name: str = "llama3-8b-8192"):
        self.model = model_name
        self.client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.context = []
        
    def generate_response(self, prompt: str) -> str:
        """Generate a response using the Groq model"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def create_api_analysis_prompt(self, endpoints: List[Dict[str, str]], user_intent: str) -> str:
        """Create a prompt for analyzing APIs based on user intent"""
        endpoint_list = "\n".join([
            f"- {endpoint['method']} {endpoint['path']}: {endpoint['summary']}"
            for endpoint in endpoints
        ])
        
        return f"""Based on the following user intent and available API endpoints, provide a JSON array of required API calls in order of execution.
Each API object in the array should have: method, path, and reason (why this API is needed).

User's Intent: {user_intent}

Available API Endpoints:
{endpoint_list}

Respond ONLY with a valid JSON array. Example format:
[
    {{
        "method": "GET",
        "path": "/example/path",
        "reason": "Brief explanation why this API is needed"
    }}
]"""

    async def analyze_user_request(self, parser: SwaggerParser, user_intent: str) -> Dict[str, Any]:
        """Analyze user request and return required APIs in JSON format"""
        try:
            # Get all available endpoints
            endpoints = parser.get_endpoint_summary()
            
            # Create and send the analysis prompt
            analysis_prompt = self.create_api_analysis_prompt(endpoints, user_intent)
            analysis_response = self.generate_response(analysis_prompt)
            
            return {
                "required_apis": analysis_response,
                "available_endpoints": endpoints
            }
        except Exception as e:
            return {"error": f"Error analyzing request: {str(e)}"}

    async def process_user_request(self, parser: SwaggerParser, user_intent: str) -> Dict[str, Any]:
        """Process a user request and return required APIs"""
        try:
            # Get the analysis of the request
            analysis_result = await self.analyze_user_request(parser, user_intent)
            
            if "error" in analysis_result:
                return analysis_result
            
            return {
                "type": "api_list",
                "content": analysis_result["required_apis"],
                "available_endpoints": analysis_result["available_endpoints"]
            }
            
        except Exception as e:
            return {"error": str(e)}

    def create_endpoint_selection_prompt(self, endpoints: List[Dict[str, str]]) -> str:
        """Create a prompt for endpoint selection"""
        endpoint_list = "\n".join([
            f"- {endpoint['method']} {endpoint['path']}: {endpoint['summary']}"
            for endpoint in endpoints
        ])
        
        return f"""Based on the following available API endpoints, help me understand which endpoint would be most appropriate:

Available endpoints:
{endpoint_list}

Please analyze these endpoints and suggest the most appropriate one for the user's needs. Consider the HTTP method, path, and purpose of each endpoint."""

    def create_parameter_collection_prompt(self, endpoint: EndpointInfo) -> str:
        """Create a prompt for parameter collection"""
        params = endpoint.parameters
        param_list = "\n".join([
            f"- {param['name']} ({param['in']}): {param.get('description', 'No description')} "
            f"{'(Required)' if param.get('required', False) else '(Optional)'}"
            for param in params
        ])
        
        return f"""For the endpoint {endpoint.method} {endpoint.path}, I need to collect the following parameters:

{param_list}

Please help guide the user through providing these parameters, especially the required ones. Ask for them one at a time and validate the input."""

    async def suggest_endpoint(self, parser: SwaggerParser, user_intent: str) -> Optional[EndpointInfo]:
        """Suggest an appropriate endpoint based on user intent"""
        endpoints = parser.get_endpoint_summary()
        prompt = self.create_endpoint_selection_prompt(endpoints)
        full_prompt = f"User intent: {user_intent}\n\n{prompt}"
        
        response = await self.generate_response(full_prompt)
        # Process the response to extract the suggested endpoint
        # This is a simplified version - you might want to add more sophisticated parsing
        return response

    async def collect_parameters(self, endpoint: EndpointInfo, user_intent: str) -> Dict[str, Any]:
        """Collect and validate parameters for an endpoint"""
        prompt = self.create_parameter_collection_prompt(endpoint)
        full_prompt = f"User intent: {user_intent}\n\n{prompt}"
        
        response = await self.generate_response(full_prompt)
        # For now, return an empty dict - you can implement parameter extraction logic later
        return {}

    def validate_parameters(self, parameters: Dict[str, Any], endpoint: EndpointInfo) -> bool:
        """Validate the collected parameters against endpoint requirements"""
        required_params = [p['name'] for p in endpoint.parameters if p.get('required', False)]
        return all(param in parameters for param in required_params)
