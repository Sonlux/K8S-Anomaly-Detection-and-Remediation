from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from kubernetes import client, config, watch
import pandas as pd
import logging
import os
import sys
import time
from typing import Dict, Any, List, TypedDict, Optional, Tuple, Literal
import json
import traceback
import yaml
import kubernetes as k8s
from unittest.mock import MagicMock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remediation_agent")

# Types for our state
class RemediationState(TypedDict):
    messages: List[Any]
    prediction: Dict[str, Any]
    pod_info: Dict[str, Any]
    remediation_plan: Dict[str, Any]
    approval_status: str  # "pending", "approved", "rejected", "complete"
    action_status: str  # "waiting", "in_progress", "success", "failed"

# Initialize the LLM using NVIDIA Llama API
nvidia_api_key = os.environ.get("NVIDIA_API_KEY", "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")

# Check if we're in test mode
TEST_MODE = os.environ.get("REMEDIATION_TEST_MODE", "false").lower() == "true"
if TEST_MODE:
    logger.info("Running in TEST MODE - no actual API or K8s calls will be made")

# Try to create the LLM with proper error handling
try:
    # Skip actual API initialization in test mode
    if TEST_MODE:
        use_llm = True
        use_custom_llm = True
        # Create an empty placeholder to avoid import errors in test mode
        nvidia_llm = None
        logger.info("Test mode: mocked NVIDIA LLM API")
    else:
        # Try to import NVIDIA LLM wrapper
        try:
            # Import from agents directory using absolute path
            agents_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, agents_path)  # Insert at beginning of path for priority
            from nvidia_llm import NvidiaLLM
            use_llm = True
            use_custom_llm = True
            nvidia_llm = NvidiaLLM(api_key=nvidia_api_key)
            logger.info(f"Successfully imported and initialized NvidiaLLM from {agents_path}")
        except ImportError as e:
            logger.warning(f"Failed to import NvidiaLLM module: {e}")
            use_llm = False
            use_custom_llm = False
            nvidia_llm = None
        except Exception as e:
            logger.error(f"Error initializing NvidiaLLM: {e}")
            use_llm = False
            use_custom_llm = False
            nvidia_llm = None
            llm = ChatOpenAI(
                base_url="https://integrate.api.nvidia.com/v1", 
                api_key=nvidia_api_key,
                model="llama3-70b-instruct"
            )
            logger.info("Successfully initialized NVIDIA LLM API with LangChain")
            use_llm = True
            use_custom_llm = False
except Exception as e:
    logger.error(f"Failed to initialize NVIDIA LLM API: {e}")
    logger.warning("Will run with basic remediation analysis (no LLM)")
    use_llm = False
    use_custom_llm = False

# Create base K8s client
try:
    config.load_kube_config()
except Exception:
    try:
        config.load_incluster_config()
    except Exception as e:
        logger.error(f"Failed to load Kubernetes configuration: {e}")
        
core_api = client.CoreV1Api()
apps_api = client.AppsV1Api()

# Import the RAG utility function
from rag_utils import query_knowledge_base

# System prompts
remediation_system_prompt = """You are an expert Kubernetes administrator and site reliability engineer (SRE). Your task is to analyze Kubernetes pod anomalies and propose detailed, actionable remediation plans. You have access to a knowledge base of Kubernetes documentation and best practices. **Always prioritize information from the provided context when formulating your response.** If the context does not contain sufficient information, use your general Kubernetes knowledge."""

# Prompt templates
remediation_plan_prompt = ChatPromptTemplate.from_messages([
    ("system", remediation_system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", """Based on the following Kubernetes pod information and detected anomaly, \
and using the provided context from the knowledge base, generate a comprehensive remediation plan.

<Context>
{context}
</Context>

<Pod_Information>
{pod_info}
</Pod_Information>

<Anomaly_Prediction>
{prediction}
</Anomaly_Prediction>

Your remediation plan should be clear, step-by-step, and include commands or configurations where applicable. \
Focus on the most effective and least disruptive solutions first. \
Provide a confidence level for your plan (e.g., 'high', 'medium', 'low').""")
])

# Define agent graph nodes
def detect_issue(state: RemediationState) -> RemediationState:
    """Analyze the anomaly and pod info to detect the specific issue."""
    prediction = state["prediction"]
    pod_info = state["pod_info"]
    messages = state["messages"]
    
    is_anomaly = prediction.get("predicted_anomaly", 0) == 1
    anomaly_type = prediction.get("anomaly_type", "unknown")
    probability = prediction.get("anomaly_probability", 0.0)
    
    if not is_anomaly:
        messages.append(AIMessage(content=f"No anomaly detected (confidence: {1-probability:.4f}). No remediation needed."))
        return {"messages": messages, "prediction": prediction, "pod_info": pod_info, 
                "remediation_plan": {}, "approval_status": "complete", "action_status": "success"}
    
    # Format the anomaly information for the LLM
    messages.append(AIMessage(content=f"Anomaly detected: {anomaly_type} with confidence {probability:.4f}. Generating remediation plan..."))
    
    # Return updated state
    return {"messages": messages, "prediction": prediction, "pod_info": pod_info, 
            "remediation_plan": {}, "approval_status": "pending", "action_status": "waiting"}

def generate_remediation_plan(state: RemediationState) -> RemediationState:
    """Generate a remediation plan using the LLM or basic logic if LLM is unavailable."""
    prediction = state["prediction"]
    pod_info = state["pod_info"]
    messages = state["messages"]
    
    # Get anomaly information
    anomaly_type = prediction.get("anomaly_type", "unknown")
    probability = prediction.get("anomaly_probability", 0.0)
    
    try:
        # Formulate a query for the RAG system based on the anomaly and pod info
        rag_query = f"Kubernetes remediation for {anomaly_type} anomaly on pod {pod_info.get('name', 'unknown')} in namespace {pod_info.get('namespace', 'default')}. Pod details: {json.dumps(pod_info)}. Anomaly details: {json.dumps(prediction)}"
        
        # Refine the RAG query to be more specific and question-like
        rag_query = f"""What is the remediation plan for a Kubernetes pod experiencing '{anomaly_prediction}'?
        The pod details are: {pod_info.get('name', 'N/A')}, namespace: {pod_info.get('namespace', 'N/A')},
        status: {pod_info.get('status', 'N/A')}, reason: {pod_info.get('reason', 'N/A')},
        message: {pod_info.get('message', 'N/A')}. Provide solutions for this specific anomaly and pod state.
        """

        # Query the knowledge base for relevant documents
        retrieved_docs = query_knowledge_base(rag_query)
        
        # Format the retrieved documents for the prompt
        context_text = "\n---\n".join([doc['document'] for doc in retrieved_docs])
        
        if use_llm:
            if use_custom_llm:
                # Use the custom NVIDIA LLM wrapper
                prompt_text = f"""{remediation_system_prompt}

Based on the following Kubernetes pod information and detected anomaly, \
and using the provided context from the knowledge base, generate a comprehensive remediation plan.

<Context>
{context_text}
</Context>

<Pod_Information>
{pod_info}
</Pod_Information>

<Anomaly_Prediction>
{prediction}
</Anomaly_Prediction>

Your remediation plan should be clear, step-by-step, and include commands or configurations where applicable. \
Focus on the most effective and least disruptive solutions first. \
Provide a confidence level for your plan (e.g., 'high', 'medium', 'low')."""

                # Generate the remediation plan using the custom wrapper
                plan_text = nvidia_llm.generate(prompt_text, temperature=0.3)
                
                # Add the response to messages
                messages.append(AIMessage(content=plan_text))
                
                # Parse the plan using our improved parser
                plan_dict = parse_llm_response(plan_text)
                
                # Log the parsed plan for debugging
                logger.debug(f"Parsed plan: {plan_dict}")
                
            else:
                # Use LangChain with OpenAI client
                # Format the data for the prompt
                prompt = remediation_plan_prompt.format(
                    messages=messages,
                    prediction=prediction,
                    pod_info=pod_info,
                    context=context_text # Pass the retrieved context to the prompt
                )
                
                # Generate the remediation plan
                response = llm.invoke(prompt)
                messages.append(response)
                
                # Extract structured information from the response
                plan_text = response.content
                
                # Parse the plan using our improved parser
                plan_dict = parse_llm_response(plan_text)
        else:
            # Generate a basic remediation plan without LLM
            logger.info("Generating basic remediation plan without LLM")
            plan_dict = generate_basic_remediation_plan(prediction, pod_info)
            
            # Add basic plan to messages
            messages.append(AIMessage(content=f"[Basic Analysis Mode]\n\nIssue summary: {plan_dict.get('Issue summary', 'No summary')}"))
        
        # Add action type based on anomaly
        if "action_type" not in plan_dict:
            if anomaly_type == "crash_loop":
                plan_dict["action_type"] = "restart_pod"
            elif anomaly_type == "oom_kill":
                plan_dict["action_type"] = "increase_memory"
            elif anomaly_type == "resource_exhaustion":
                plan_dict["action_type"] = "scale_deployment"
            elif anomaly_type == "network_issue":
                plan_dict["action_type"] = "restart_pod"
            else:
                plan_dict["action_type"] = "restart_pod"  # Default action
                
        # Set warning level if missing
        if "Warning level" not in plan_dict:
            plan_dict["Warning level"] = "medium"
            
        # Return updated state with the remediation plan
        return {"messages": messages, "prediction": prediction, "pod_info": pod_info,
                "remediation_plan": plan_dict, "approval_status": "pending", "action_status": "waiting"}
    except Exception as e:
        error_msg = f"Error generating remediation plan: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()
        
        # Fall back to basic plan in case of error
        fallback_plan = generate_basic_remediation_plan(prediction, pod_info)
        messages.append(AIMessage(content=f"[Error in plan generation, using basic mode]\n\nIssue summary: {fallback_plan.get('Issue summary', 'Error')}\n\nRecommended steps: {fallback_plan.get('Recommended remediation steps', 'Restart pod if needed')}"))
        
        return {"messages": messages, "prediction": prediction, "pod_info": pod_info,
                "remediation_plan": fallback_plan, "approval_status": "pending", "action_status": "waiting"}

def generate_basic_remediation_plan(prediction: Dict[str, Any], pod_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a basic remediation plan without using an LLM."""
    plan = {}
    
    # Extract key information
    anomaly_type = prediction.get("anomaly_type", "unknown")
    event_reason = prediction.get("event_reason", "")
    event_count = prediction.get("event_count", 0)
    restarts = pod_info.get("restart_count", 0)
    pod_name = pod_info.get("name", "unknown")
    namespace = pod_info.get("namespace", "default")
    
    # Generate basic issue summary
    if anomaly_type == "crash_loop":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is in CrashLoopBackOff with {restarts} restarts."
        plan["Root cause analysis"] = "Pod is repeatedly crashing, likely due to application errors or resource issues."
        plan["Recommended remediation steps"] = "1. Restart the pod to clear any transient issues\n2. Check logs for application errors"
        plan["Potential impact"] = "Brief service interruption during pod restart."
        plan["Warning level"] = "medium"
        plan["action_type"] = "restart_pod"
        
    elif anomaly_type == "oom_kill":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is experiencing Out of Memory (OOM) kills."
        plan["Root cause analysis"] = "Pod is being terminated due to memory usage exceeding limits."
        plan["Recommended remediation steps"] = "1. Increase memory limits by 50%\n2. Monitor memory usage after increase"
        plan["Potential impact"] = "Application might restart during resource update."
        plan["Warning level"] = "high"
        plan["action_type"] = "increase_memory"
        
    elif anomaly_type == "resource_exhaustion":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is experiencing resource exhaustion."
        plan["Root cause analysis"] = "Pod's resources are near maximum, causing performance degradation."
        plan["Recommended remediation steps"] = "1. Scale up the deployment by adding 1 replica\n2. Consider increasing resource limits if scaling is not sufficient"
        plan["Potential impact"] = "New pod creation will consume additional cluster resources."
        plan["Warning level"] = "medium"
        plan["action_type"] = "scale_deployment"
        
    elif anomaly_type == "network_issue":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is experiencing network issues."
        plan["Root cause analysis"] = "Network packet drops or connection issues detected."
        plan["Recommended remediation steps"] = "1. Restart the pod to re-establish network connections\n2. Check network policies if issue persists"
        plan["Potential impact"] = "Brief service interruption during pod restart."
        plan["Warning level"] = "medium"
        plan["action_type"] = "restart_pod"
        
    else:
        plan["Issue summary"] = f"Unknown anomaly detected for pod {namespace}/{pod_name}."
        plan["Root cause analysis"] = "The specific cause could not be determined from available metrics."
        plan["Recommended remediation steps"] = "1. Restart the pod as a general troubleshooting step\n2. Monitor the pod after restart"
        plan["Potential impact"] = "Brief service interruption during pod restart."
        plan["Warning level"] = "medium"
        plan["action_type"] = "restart_pod"
    
    # Add event information if available
    if event_reason and event_count > 0:
        plan["Issue summary"] += f" Event '{event_reason}' observed {event_count} times."
        
    return plan

def request_approval(state: RemediationState) -> RemediationState:
    """Present the remediation plan and request approval."""
    messages = state["messages"]
    remediation_plan = state["remediation_plan"]
    
    # Format the approval request
    # Get warning level and normalize it - carefully extract it from the string if needed
    warning_level_raw = remediation_plan.get("Warning level", "medium")
    
    # If warning level contains multiple lines or additional text, extract just the level
    if isinstance(warning_level_raw, str) and len(warning_level_raw) > 10:
        # Try to extract just the level (high/medium/low) from text
        if "high" in warning_level_raw.lower():
            warning_level = "high"
        elif "medium" in warning_level_raw.lower():
            warning_level = "medium"
        else:
            warning_level = "low"
    else:
        warning_level = warning_level_raw.lower().strip() if isinstance(warning_level_raw, str) else "medium"
        
    action_type = remediation_plan.get("action_type", "unknown")
    pod_name = state["pod_info"].get("name", "unknown")
    namespace = state["pod_info"].get("namespace", "default")
    
    # Create color-coded warning based on level
    if warning_level == "high":
        warning_prefix = "⚠️ HIGH RISK"
    elif warning_level == "medium":
        warning_prefix = "⚠️ MEDIUM RISK"
    else:
        warning_prefix = "ℹ️ LOW RISK"
    
    # Get a concise issue summary
    issue_summary = remediation_plan.get('Issue summary', 'No summary available')
    if len(issue_summary) > 500:  # If summary is too long, get the first paragraph or sentence
        first_paragraph = issue_summary.split('\n\n')[0] if '\n\n' in issue_summary else issue_summary
        if len(first_paragraph) > 200:
            # Get first sentence or first 200 chars
            first_sentence = first_paragraph.split('.')[0] + '.'
            issue_summary = first_sentence if len(first_sentence) < 200 else first_paragraph[:197] + '...'
            
    # Get remediation steps
    remediation_steps = remediation_plan.get('Recommended remediation steps', 'No steps available')
    
    # Get potential impact
    potential_impact = remediation_plan.get('Potential impact', 'Impact not analyzed')
    
    approval_text = f"""{warning_prefix} REMEDIATION PLAN
    
Pod: {namespace}/{pod_name}
Action: {action_type}

{issue_summary}

Remediation steps:
{remediation_steps}

Potential impact:
{potential_impact}

Do you approve this remediation plan? (yes/no)"""
    
    messages.append(AIMessage(content=approval_text))
    
    # Return state with pending approval
    return {"messages": messages, "prediction": state["prediction"], "pod_info": state["pod_info"],
            "remediation_plan": remediation_plan, "approval_status": "pending", "action_status": "waiting"}

def process_approval(state: RemediationState, approval: str) -> RemediationState:
    """Process the user's approval response."""
    messages = state["messages"]
    
    # Update approval status based on user response
    approval_status = "approved" if approval.lower() in ["yes", "y", "approve", "approved"] else "rejected"
    
    if approval_status == "approved":
        messages.append(AIMessage(content="Remediation plan approved. Proceeding with execution..."))
        action_status = "in_progress"
    else:
        messages.append(AIMessage(content="Remediation plan rejected. No action will be taken."))
        action_status = "success"  # Nothing to do, so mark as success
    
    # Return updated state
    return {"messages": messages, "prediction": state["prediction"], "pod_info": state["pod_info"],
            "remediation_plan": state["remediation_plan"], "approval_status": approval_status, 
            "action_status": action_status}

def execute_remediation(state: RemediationState) -> RemediationState:
    """Execute the approved remediation plan."""
    messages = state["messages"]
    remediation_plan = state["remediation_plan"]
    pod_info = state["pod_info"]
    
    # Only execute if approval status is "approved"
    if state["approval_status"] != "approved":
        return state
    
    # Get pod and action information
    pod_name = pod_info.get("name", "unknown")
    namespace = pod_info.get("namespace", "default")
    action_type = remediation_plan.get("action_type", "unknown")
    
    try:
        # Execute the appropriate remediation action
        if action_type == "restart_pod":
            try:
                # Delete pod to trigger recreation
                core_api.delete_namespaced_pod(
                    name=pod_name,
                    namespace=namespace,
                    body=client.V1DeleteOptions()
                )
                success_msg = f"Successfully restarted pod {namespace}/{pod_name}"
                messages.append(AIMessage(content=success_msg))
                logger.info(success_msg)
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # Pod not found - this is ok in test mode or if the pod was already deleted
                    warning_msg = f"Pod {namespace}/{pod_name} not found. It may have been already deleted or doesn't exist."
                    messages.append(AIMessage(content=warning_msg))
                    logger.warning(warning_msg)
                else:
                    # Re-raise other API exceptions
                    raise
            
        elif action_type == "increase_memory":
            try:
                # Get the deployment name from pod
                deployment_name = pod_info.get("owner_reference", pod_name.rsplit("-", 1)[0])
                
                # Get current deployment
                deployment = apps_api.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                # Update memory limits (increase by 50%)
                containers = deployment.spec.template.spec.containers
                for container in containers:
                    if container.resources and container.resources.limits and "memory" in container.resources.limits:
                        current_mem = container.resources.limits["memory"]
                        # Parse memory value (e.g., "256Mi")
                        value = int(''.join(filter(str.isdigit, current_mem)))
                        unit = ''.join(filter(str.isalpha, current_mem))
                        new_value = int(value * 1.5)
                        container.resources.limits["memory"] = f"{new_value}{unit}"
                        
                        # Also update requests if they exist
                        if container.resources.requests and "memory" in container.resources.requests:
                            req_value = int(''.join(filter(str.isdigit, container.resources.requests["memory"])))
                            req_unit = ''.join(filter(str.isalpha, container.resources.requests["memory"]))
                            new_req = int(req_value * 1.5)
                            container.resources.requests["memory"] = f"{new_req}{req_unit}"
                
                # Update the deployment
                apps_api.patch_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace,
                    body=deployment
                )
                
                success_msg = f"Successfully increased memory allocation for deployment {namespace}/{deployment_name}"
                messages.append(AIMessage(content=success_msg))
                logger.info(success_msg)
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    warning_msg = f"Deployment {namespace}/{deployment_name} not found. It may have been deleted or doesn't exist."
                    messages.append(AIMessage(content=warning_msg))
                    logger.warning(warning_msg)
                else:
                    # Re-raise other API exceptions
                    raise
            
        elif action_type == "scale_deployment":
            try:
                # Get the deployment name from pod
                deployment_name = pod_info.get("owner_reference", pod_name.rsplit("-", 1)[0])
                
                # Get current deployment
                deployment = apps_api.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                # Scale up by 1 replica
                current_replicas = deployment.spec.replicas
                new_replicas = current_replicas + 1
                
                # Update replicas
                deployment.spec.replicas = new_replicas
                
                # Update the deployment
                apps_api.patch_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace,
                    body=deployment
                )
                
                success_msg = f"Successfully scaled deployment {namespace}/{deployment_name} from {current_replicas} to {new_replicas} replicas"
                messages.append(AIMessage(content=success_msg))
                logger.info(success_msg)
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    warning_msg = f"Deployment {namespace}/{deployment_name} not found. It may have been deleted or doesn't exist."
                    messages.append(AIMessage(content=warning_msg))
                    logger.warning(warning_msg)
                else:
                    # Re-raise other API exceptions
                    raise
            
        else:
            warning_msg = f"Unsupported action type: {action_type}. No remediation action taken."
            messages.append(AIMessage(content=warning_msg))
            logger.warning(warning_msg)
        
        # Return updated state
        return {"messages": messages, "prediction": state["prediction"], "pod_info": pod_info,
                "remediation_plan": remediation_plan, "approval_status": "approved", "action_status": "success"}
        
    except Exception as e:
        error_msg = f"Error executing remediation: {str(e)}"
        messages.append(AIMessage(content=error_msg))
        logger.error(error_msg)
        traceback.print_exc()
        
        # Return updated state with failure
        return {"messages": messages, "prediction": state["prediction"], "pod_info": pod_info,
                "remediation_plan": remediation_plan, "approval_status": "approved", "action_status": "failed"}

# Define the workflow graph
def create_remediation_graph():
    workflow = StateGraph(RemediationState)
    
    # Add nodes
    workflow.add_node("detect_issue", detect_issue)
    workflow.add_node("generate_plan", generate_remediation_plan)
    workflow.add_node("request_approval", request_approval)
    workflow.add_node("execute_remediation", execute_remediation)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "detect_issue",
        lambda state: END if state["approval_status"] == "complete" else "generate_plan"
    )
    
    workflow.add_edge("generate_plan", "request_approval")
    
    workflow.add_conditional_edges(
        "request_approval",
        lambda state: "execute_remediation" if state["approval_status"] == "approved" else END
    )
    
    workflow.add_edge("execute_remediation", END)
    
    # Set entry point
    workflow.set_entry_point("detect_issue")
    
    # Compile the graph
    return workflow.compile()

# Instantiate the graph
remediation_agent = create_remediation_graph()

def remediate_pod(prediction: dict, pod_info: dict, user_input: str = None) -> List[Any]:
    """Process a pod anomaly through the remediation agent."""
    # Initialize the state
    initial_state = {
        "messages": [],
        "prediction": prediction,
        "pod_info": pod_info,
        "remediation_plan": {},
        "approval_status": "pending",
        "action_status": "waiting"
    }
    
    # Run the initial flow until approval is needed
    current_state = remediation_agent.invoke(initial_state)
    
    # If approval is pending and user input is provided, process the approval
    if current_state["approval_status"] == "pending" and user_input is not None:
        # Process the approval
        current_state = process_approval(current_state, user_input)
        
        # Continue flow if approved
        if current_state["approval_status"] == "approved":
            # Call execute_remediation directly instead of invoking the whole agent again
            current_state = execute_remediation(current_state)
    
    return current_state["messages"]

def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Parse LLM response text into structured sections."""
    logger.debug("Parsing LLM response into structured sections")
    
    # List of sections we're looking for
    sections = [
        "Issue summary", "Root cause analysis", "Recommended remediation steps", 
        "Potential impact", "Warning level"
    ]
    plan_dict = {}
    
    # First try to find sections based on exact headings or numbers
    current_section = None
    section_content = []
    
    # Log the first 100 chars of the response for debugging
    logger.debug(f"Response text preview: {response_text[:100]}...")
    
    for line in response_text.split('\n'):
        # Clean up the line
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Try different section heading patterns
        matched = False
        
        # Match exact section titles (regardless of case)
        for section in sections:
            if section.lower() in clean_line.lower():
                logger.debug(f"Found section: {section} in line: {clean_line}")
                if current_section and section_content:
                    plan_dict[current_section] = '\n'.join(section_content).strip()
                    section_content = []
                current_section = section
                matched = True
                break
                
        # Match numbered sections like "1. Issue Summary" or "1) Issue Summary"
        if not matched:
            for i, section in enumerate(sections, 1):
                pattern = section.lower()
                if (f"{i}." in clean_line.lower() or f"{i})" in clean_line.lower()) and pattern in clean_line.lower():
                    logger.debug(f"Found numbered section {i}. {section} in line: {clean_line}")
                    if current_section and section_content:
                        plan_dict[current_section] = '\n'.join(section_content).strip()
                        section_content = []
                    current_section = section
                    matched = True
                    break
        
        # Match Markdown-style headings like "## Issue Summary"
        if not matched and clean_line.startswith('#'):
            for section in sections:
                if section.lower() in clean_line.lower():
                    logger.debug(f"Found markdown section: {section} in line: {clean_line}")
                    if current_section and section_content:
                        plan_dict[current_section] = '\n'.join(section_content).strip()
                        section_content = []
                    current_section = section
                    matched = True
                    break
                    
        # Match pattern like "**Warning Level**"
        if not matched and "**" in clean_line:
            for section in sections:
                pattern = f"**{section}**"
                if pattern.lower() in clean_line.lower():
                    logger.debug(f"Found bold section: {section} in line: {clean_line}")
                    if current_section and section_content:
                        plan_dict[current_section] = '\n'.join(section_content).strip()
                        section_content = []
                    current_section = section
                    matched = True
                    break
                    
        # If no section matched, add to current section content
        if not matched and current_section:
            section_content.append(line)
    
    # Add the last section
    if current_section and section_content:
        plan_dict[current_section] = '\n'.join(section_content).strip()
        
    # If we couldn't find explicit sections, try a more aggressive approach
    if not plan_dict or len(plan_dict) < 3:
        logger.debug(f"Not enough sections found ({len(plan_dict)}), trying more aggressive parsing")
        # Look for patterns like "**Issue Summary**" or "Issue Summary:"
        for section in sections:
            pattern1 = f"**{section}**"
            pattern2 = f"{section}:"
            
            if pattern1.lower() in response_text.lower():
                start_idx = response_text.lower().find(pattern1.lower())
                # Find the next section
                end_idx = len(response_text)
                for next_section in sections:
                    if next_section == section:
                        continue
                    next_pattern1 = f"**{next_section}**"
                    next_pattern2 = f"{next_section}:"
                    
                    next_idx1 = response_text.lower().find(next_pattern1.lower(), start_idx + len(pattern1))
                    next_idx2 = response_text.lower().find(next_pattern2.lower(), start_idx + len(pattern1))
                    
                    if next_idx1 > 0 and next_idx1 < end_idx:
                        end_idx = next_idx1
                    if next_idx2 > 0 and next_idx2 < end_idx:
                        end_idx = next_idx2
                
                content = response_text[start_idx + len(pattern1):end_idx].strip()
                plan_dict[section] = content
                logger.debug(f"Found section {section} using pattern '{pattern1}'")
            
            elif pattern2.lower() in response_text.lower():
                start_idx = response_text.lower().find(pattern2.lower())
                # Find the next section
                end_idx = len(response_text)
                for next_section in sections:
                    if next_section == section:
                        continue
                    next_pattern1 = f"**{next_section}**"
                    next_pattern2 = f"{next_section}:"
                    
                    next_idx1 = response_text.lower().find(next_pattern1.lower(), start_idx + len(pattern2))
                    next_idx2 = response_text.lower().find(next_pattern2.lower(), start_idx + len(pattern2))
                    
                    if next_idx1 > 0 and next_idx1 < end_idx:
                        end_idx = next_idx1
                    if next_idx2 > 0 and next_idx2 < end_idx:
                        end_idx = next_idx2
                
                content = response_text[start_idx + len(pattern2):end_idx].strip()
                plan_dict[section] = content
                logger.debug(f"Found section {section} using pattern '{pattern2}'")
    
    # If still no luck with warning level, try more specific patterns
    if "Warning level" not in plan_dict:
        logger.debug("Warning level not found, trying specialized extraction")
        # Check for common patterns like "Warning Level: High"
        warning_patterns = [
            "warning level: high", "warning level: medium", "warning level: low",
            "warning level - high", "warning level - medium", "warning level - low",
            "* high", "* medium", "* low",
            "**high**", "**medium**", "**low**",
            "high risk", "medium risk", "low risk"
        ]
        
        for pattern in warning_patterns:
            if pattern in response_text.lower():
                if "high" in pattern:
                    plan_dict["Warning level"] = "high"
                    logger.debug(f"Found warning level 'high' using pattern '{pattern}'")
                    break
                elif "medium" in pattern:
                    plan_dict["Warning level"] = "medium"
                    logger.debug(f"Found warning level 'medium' using pattern '{pattern}'")
                    break
                elif "low" in pattern:
                    plan_dict["Warning level"] = "low"
                    logger.debug(f"Found warning level 'low' using pattern '{pattern}'")
                    break
    
    # Special handling for warning level to ensure it's normalized
    if "Warning level" in plan_dict:
        warning_text = plan_dict["Warning level"].lower()
        if "high" in warning_text:
            plan_dict["Warning level"] = "high"
        elif "medium" in warning_text:
            plan_dict["Warning level"] = "medium"
        elif "low" in warning_text:
            plan_dict["Warning level"] = "low"
        else:
            # If we couldn't determine, default to medium
            plan_dict["Warning level"] = "medium"
    else:
        # Default to medium if we couldn't find it
        plan_dict["Warning level"] = "medium"
        logger.debug("Warning level not found, defaulting to 'medium'")
    
    # Log the final result
    logger.debug(f"Parsed {len(plan_dict)} sections from response: {list(plan_dict.keys())}")
    if "Warning level" in plan_dict:
        logger.debug(f"Warning level: {plan_dict['Warning level']}")
    
    return plan_dict

# Example usage
if __name__ == "__main__":
    print("Running remediation agent example...")
    
    # Set test mode to avoid real Kubernetes API calls
    os.environ["REMEDIATION_TEST_MODE"] = "true"
    
    # Sample anomaly prediction
    sample_prediction = {
        'predicted_anomaly': 1,
        'anomaly_probability': 0.96,
        'anomaly_type': 'crash_loop',
        'event_age_minutes': 120,
        'event_reason': 'BackOff',
        'event_count': 45
    }
    
    # Sample pod info
    sample_pod_info = {
        'name': 'example-pod-1',
        'namespace': 'default',
        'status': 'Running',
        'owner_reference': 'example-deployment',
        'node': 'node-1',
        'ip': '10.244.0.23',
        'cpu_request': '100m',
        'memory_request': '256Mi',
        'cpu_limit': '200m',
        'memory_limit': '512Mi',
        'restart_count': 12
    }
    
    # For direct script execution, we need to patch Kubernetes API
    try:
        from unittest.mock import patch, MagicMock
        
        # Create mock Kubernetes classes
        class MockKubernetesClient:
            def mock_delete_pod(self, name, namespace, body):
                print(f"MOCK: Would delete pod {namespace}/{name} in real environment")
                return {"status": "Success"}
                
            def mock_read_deployment(self, name, namespace):
                print(f"MOCK: Would read deployment {namespace}/{name} in real environment")
                deployment = MagicMock()
                deployment.metadata.name = name
                deployment.metadata.namespace = namespace
                deployment.spec.replicas = 1
                
                container = MagicMock()
                container.name = "container"
                container.resources = MagicMock()
                container.resources.limits = {"memory": "512Mi"}
                container.resources.requests = {"memory": "256Mi"}
                
                deployment.spec.template.spec.containers = [container]
                return deployment
                
            def mock_patch_deployment(self, name, namespace, body):
                if hasattr(body.spec, 'replicas'):
                    print(f"MOCK: Would scale deployment {namespace}/{name} to {body.spec.replicas} replicas")
                else:
                    print(f"MOCK: Would update deployment {namespace}/{name} resource limits")
                    for container in body.spec.template.spec.containers:
                        if container.resources and container.resources.limits:
                            print(f"MOCK: New memory limits: {container.resources.limits.get('memory')}")
                return {"status": "Success"}
                
        # Create mock instance
        mock_client = MockKubernetesClient()
        
        # Mock response for generate function
        sample_response = """Based on the pod information and anomaly prediction, here's a remediation plan:

**1. Issue summary**
The pod is experiencing a crash loop with 12 restarts. This is indicated by the 'BackOff' event that has occurred 45 times over 120 minutes.

**2. Root cause analysis**
Crash loops typically occur when a container repeatedly fails to start successfully. This could be due to:
- Application errors in the pod's code
- Missing dependencies or configuration
- Resource constraints (though this seems less likely given the current resource usage)
- Corrupted application state

**3. Recommended remediation steps**
1. Restart the pod to clear any transient issues:
   - Delete the pod to trigger recreation by the deployment controller
2. If the issue persists, check pod logs:
   - `kubectl logs example-pod-1 -n default`
3. Check for any recent changes to the application or configuration

**4. Potential impact**
- Brief service interruption during pod restart
- Potential for the issue to recur if the root cause is not addressed
- User requests might fail during the restart period

**5. Warning level**
**HIGH** - The pod is in a crash loop which indicates a critical failure requiring immediate attention."""

        # Mock the generate method
        def mock_generate(prompt, temperature=0.5):
            return sample_response
        
        # Apply patches
        with patch('kubernetes.client.CoreV1Api') as mock_core_api, \
             patch('kubernetes.client.AppsV1Api') as mock_apps_api:
            
            # Configure mocks
            mock_core_api.return_value.delete_namespaced_pod.side_effect = mock_client.mock_delete_pod
            mock_apps_api.return_value.read_namespaced_deployment.side_effect = mock_client.mock_read_deployment
            mock_apps_api.return_value.patch_namespaced_deployment.side_effect = mock_client.mock_patch_deployment
            
            # Also mock the generate function by directly assigning to the module's attribute
            # Do not use 'global' as it causes syntax errors when used after assignments
            if 'nvidia_llm' in globals():
                # Store the original if it exists
                original_nvidia_llm = nvidia_llm
            
            # Create a mock and assign it 
            nvidia_llm_mock = MagicMock()
            nvidia_llm_mock.generate = mock_generate
            # Assign to the module's attribute
            sys.modules[__name__].nvidia_llm = nvidia_llm_mock
            
            # Run example
            print("Generating remediation plan...")
            messages = remediate_pod(sample_prediction, sample_pod_info)
            
            # Print the messages
            for msg in messages:
                prefix = "AI: " if isinstance(msg, AIMessage) else "Human: "
                print(f"{prefix}{msg.content}\n")
            
            # Simulate user approval
            print("\nSimulating user approval...")
            user_input = "yes"  # Auto-approve for the example
            
            # Execute remediation with approval
            print("Executing remediation plan...")
            messages = remediate_pod(sample_prediction, sample_pod_info, user_input)
            
            # Print new messages (only the ones added after approval)
            for msg in messages[-2:]:
                prefix = "AI: " if isinstance(msg, AIMessage) else "Human: "
                print(f"{prefix}{msg.content}\n")
            
    except ImportError as e:
        print(f"Error setting up mocks: {e}")
        print("Using default example without mocking...")
        
        # Generate initial remediation plan
        print("Generating remediation plan...")
        messages = remediate_pod(sample_prediction, sample_pod_info)
        
        # Print the messages
        for msg in messages:
            prefix = "AI: " if isinstance(msg, AIMessage) else "Human: "
            print(f"{prefix}{msg.content}\n")
        
        # Manual user input
        user_input = input("Do you approve this remediation plan? (yes/no): ")
        
        # Execute remediation if approved
        if user_input.lower() in ["yes", "y", "approve", "approved"]:
            print("\nExecuting remediation plan...")
            messages = remediate_pod(sample_prediction, sample_pod_info, user_input)
            
            # Print new messages (only the ones added after approval)
            for msg in messages[len(messages)-2:]:
                prefix = "AI: " if isinstance(msg, AIMessage) else "Human: "
                print(f"{prefix}{msg.content}\n")
        else:
            print("\nRemediation plan rejected. No action taken.")