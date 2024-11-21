import streamlit as st
import json
from typing import Dict, Any
from swagger_parser import SwaggerParser
from ai_agent import AIAgent
from api_interaction import APIInteraction
import asyncio

st.set_page_config(
    page_title="Swagger AI Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("Swagger AI Agent 🤖")
st.write("Upload a Swagger/OpenAPI specification and interact with APIs using natural language!")

# Initialize session state variables if they don't exist
if 'swagger_parser' not in st.session_state:
    st.session_state.swagger_parser = None
if 'base_url' not in st.session_state:
    st.session_state.base_url = ""
if 'agent' not in st.session_state:
    st.session_state.agent = AIAgent()

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Upload Swagger File")
    
    # Add a text area for direct JSON input
    st.subheader("Option 1: Paste Swagger Content")
    swagger_text = st.text_area(
        "Paste your Swagger/OpenAPI JSON content here",
        height=300
    )
    
    if swagger_text and st.button("Parse Pasted Content"):
        try:
            swagger_content = json.loads(swagger_text)
            
            if not isinstance(swagger_content, dict):
                st.error("Error: Content must be a valid Swagger/OpenAPI JSON specification")
            else:
                try:
                    # Save the JSON content to file
                    with open('./src/input.json', 'w') as file:
                        json.dump(swagger_content, file, indent=2)
                    
                    st.session_state.swagger_parser = SwaggerParser(swagger_content)
                    st.success("✅ Swagger content parsed successfully!")
                    
                    # Display available endpoints
                    st.subheader("Available Endpoints")
                    endpoints = st.session_state.swagger_parser.get_endpoint_summary()
                    for endpoint in endpoints:
                        st.write(f"**{endpoint['method']}** {endpoint['path']}")
                        if endpoint['summary']:
                            st.write(f"*{endpoint['summary']}*")
                        st.divider()
                except Exception as e:
                    st.error(f"Error parsing Swagger specification: {str(e)}")
        except json.JSONDecodeError:
            st.error("Error: Invalid JSON format. Please check your input.")
        except Exception as e:
            st.error(f"Error parsing content: {str(e)}")
    
    st.subheader("Option 2: Upload File")
    uploaded_file = st.file_uploader("Choose a Swagger/OpenAPI file", type='json')
    
    if uploaded_file is not None:
        try:
            # Read the file content
            file_content = uploaded_file.read()
            
            try:
                # Decode as string if it's bytes
                if isinstance(file_content, bytes):
                    content = file_content.decode('utf-8')
                else:
                    content = str(file_content)
                
                try:
                    swagger_content = json.loads(content)
                    
                    if not isinstance(swagger_content, dict):
                        st.error("Error: File must contain a valid Swagger/OpenAPI JSON specification")
                    else:
                        try:
                            # Save the uploaded content to file
                            with open('./src/input.json', 'w') as file:
                                json.dump(swagger_content, file, indent=2)
                            
                            st.session_state.swagger_parser = SwaggerParser(swagger_content)
                            st.success("✅ Swagger file uploaded and validated successfully!")
                            
                            # Display available endpoints
                            st.subheader("Available Endpoints")
                            endpoints = st.session_state.swagger_parser.get_endpoint_summary()
                            for endpoint in endpoints:
                                st.write(f"**{endpoint['method']}** {endpoint['path']}")
                                if endpoint['summary']:
                                    st.write(f"*{endpoint['summary']}*")
                                st.divider()
                        except Exception as e:
                            st.error(f"Error parsing Swagger specification: {str(e)}")
                
                except json.JSONDecodeError:
                    st.error("Error: Invalid JSON format. Please make sure the file contains valid JSON.")
                except Exception as e:
                    st.error(f"Error parsing JSON content: {str(e)}")
                    
            except UnicodeDecodeError:
                st.error("Error: File must be in UTF-8 text format")
            except Exception as e:
                st.error(f"Error decoding file content: {str(e)}")
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            
        # Reset the file buffer position
        uploaded_file.seek(0)

with col2:
    st.header("2. Interact with API")
    
    # Base URL input
    st.session_state.base_url = st.text_input(
        "Base URL",
        value=st.session_state.base_url,
        help="Enter the base URL of the API (e.g., https://api.example.com)"
    )
    
    # User intent input
    user_intent = st.text_area(
        "What would you like to do?",
        help="Describe what you want to do with the API in natural language"
    )
    
    # Create a function to handle async operations
    async def process_request_async(parser: SwaggerParser, user_intent: str):
        try:
            result = await st.session_state.agent.process_user_request(parser, user_intent)
            return result
        except Exception as e:
            return {"error": str(e)}

    if st.button("Process Request"):
        if user_intent:
            try:
                # Run the async function using asyncio
                result = asyncio.run(process_request_async(st.session_state.swagger_parser, user_intent))
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    # Display the API list
                    st.markdown("## Required APIs")
                    try:
                        # Try to parse the JSON string into a Python object for pretty display
                        import json
                        api_list = json.loads(result["content"])
                        st.json(api_list)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, display as plain text
                        st.code(result["content"], language="json")
                    
                    # Display available endpoints for reference
                    with st.expander("All Available Endpoints"):
                        for endpoint in result["available_endpoints"]:
                            st.markdown(f"**{endpoint['method']} {endpoint['path']}**")
                            st.markdown(f"*{endpoint['summary']}*")
                            st.markdown("---")
                    
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")

# Display instructions if no file is uploaded
if not st.session_state.swagger_parser:
    st.info("""
    👋 Welcome! To get started:
    1. Either paste your Swagger/OpenAPI JSON content or upload a JSON file
    2. Enter the base URL of your API
    3. Describe what you want to do in natural language
    4. Click "Process Request" to interact with the API
    """)
