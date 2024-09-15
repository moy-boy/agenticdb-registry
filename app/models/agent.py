from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Metadata(BaseModel):
    """
    Metadata about the agent, including name, namespace, and description.
    """
    
    name: str = Field(..., description="The name of the agent.")
    namespace: str = Field(..., description="The namespace where the agent belongs.")
    description: str = Field(..., description="A brief description of the agent.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "agent-50",
                "namespace": "production",
                "description": "Description for agent-50"
            }
        }


class Parameters(BaseModel):
    """
    OpenAI Function Calling specification for the agent's parameters.
    """
    
    type: str = Field("object", description="Specifies the type of object for the parameters.")
    properties: Dict[str, Dict[str, Any]] = Field(
        ..., description="A dictionary of property names and their specifications (type, description, etc.)."
    )
    required: list[str] = Field(..., description="List of required property names.")
    additionalProperties: bool = Field(..., description="Flag indicating if additional properties are allowed.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "Color of the item"
                    },
                    "customer_name": {
                        "type": "integer",
                        "description": "The hotel name for the booking"
                    },
                    "date": {
                        "type": "boolean",
                        "description": "Type of issue reported"
                    },
                    "clothing_size": {
                        "type": "object",
                        "description": "Type of issue reported"
                    },
                    "transaction_id": {
                        "type": "object",
                        "description": "Check-in date at the hotel"
                    }
                },
                "required": [
                    "currency",
                    "transaction_id"
                ],
                "additionalProperties": False
            }
        }


class Spec(BaseModel):
    """
    Specifications for the agent, including its lifecycle, access level, parameters, and output.
    """
    
    type: str = Field(..., description="Type of the agent (e.g., 'agent').")
    lifecycle: str = Field(..., description="The lifecycle stage of the agent (e.g., 'stable').")
    owner: str = Field(..., description="Email of the agent's owner.")
    access_level: str = Field(..., description="Access level of the agent (e.g., 'PUBLIC').")
    category: str = Field(..., description="Category that the agent belongs to.")
    url: str = Field(..., description="URL endpoint where the agent can be accessed.")
    parameters: Parameters = Field(..., description="Parameters specification following OpenAI's function calling schema.")
    output: Dict[str, Any] = Field(..., description="The output specification (e.g., success/failure status).")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "agent",
                "lifecycle": "stable",
                "owner": "owner50@business.com",
                "access_level": "PUBLIC",
                "category": "Travel",
                "url": "https://api.business.com/agent-50",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "currency": {
                            "type": "string",
                            "description": "Currency used in the transaction."
                        },
                        "customer_name": {
                            "type": "integer",
                            "description": "The name of the customer."
                        },
                        "date": {
                            "type": "boolean",
                            "description": "Date of the transaction."
                        },
                        "clothing_size": {
                            "type": "object",
                            "description": "Size of the clothing."
                        },
                        "transaction_id": {
                            "type": "object",
                            "description": "Unique identifier for the transaction."
                        }
                    },
                    "required": [
                        "currency",
                        "transaction_id"
                    ],
                    "additionalProperties": False
                },
                "output": {
                    "type": "object",
                    "description": "Boolean flag indicating success or failure."
                }
            }
        }


class Agent(BaseModel):
    """
    Complete specification for an agent, including metadata and functional specifications.
    """
    
    metadata: Metadata = Field(..., description="Metadata information for the agent.")
    spec: Spec = Field(..., description="Specification details for the agent.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "name": "agent-50",
                    "namespace": "production",
                    "description": "Description for agent-50"
                },
                "spec": {
                    "type": "agent",
                    "lifecycle": "stable",
                    "owner": "owner50@business.com",
                    "access_level": "PUBLIC",
                    "category": "Travel",
                    "url": "https://api.business.com/agent-50",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "currency": {
                                "type": "string",
                                "description": "Currency used in the transaction."
                            },
                            "customer_name": {
                                "type": "integer",
                                "description": "The name of the customer."
                            },
                            "date": {
                                "type": "boolean",
                                "description": "Date of the transaction."
                            },
                            "clothing_size": {
                                "type": "object",
                                "description": "Size of the clothing."
                            },
                            "transaction_id": {
                                "type": "object",
                                "description": "Unique identifier for the transaction."
                            }
                        },
                        "required": [
                            "currency",
                            "transaction_id"
                        ],
                        "additionalProperties": False
                    },
                    "output": {
                        "type": "object",
                        "description": "Boolean flag indicating success or failure."
                    }
                }
            }
        }
