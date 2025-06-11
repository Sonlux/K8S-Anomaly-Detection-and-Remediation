from typing import Dict, List, Any, TypedDict, Optional, Tuple, Callable, Union
import logging

# Configure logger
logger = logging.getLogger("state-graph")

class StateGraph:
    """A simple state graph implementation for the multi-agent system.
    
    This is a simplified version of the LangGraph StateGraph class for testing purposes.
    """
    
    def __init__(self, state_type):
        """Initialize the state graph.
        
        Args:
            state_type: The type of state this graph will manage
        """
        self.state_type = state_type
        self.nodes = {}
        self.edges = {}
        self.conditional_edges = {}
        self.entry_point = None
        logger.info(f"Initialized StateGraph with state type: {state_type.__name__}")
    
    def add_node(self, name: str, function: Callable):
        """Add a node to the graph.
        
        Args:
            name: The name of the node
            function: The function to execute when this node is run
        """
        self.nodes[name] = function
        logger.debug(f"Added node: {name}")
    
    def add_edge(self, start_node: str, end_node: str):
        """Add an edge between two nodes.
        
        Args:
            start_node: The starting node
            end_node: The ending node
        """
        if start_node not in self.edges:
            self.edges[start_node] = []
        self.edges[start_node].append(end_node)
        logger.debug(f"Added edge: {start_node} -> {end_node}")
    
    def add_conditional_edges(self, start_node: str, condition_function: Callable):
        """Add conditional edges from a node.
        
        Args:
            start_node: The starting node
            condition_function: A function that takes the state and returns the next node
        """
        self.conditional_edges[start_node] = condition_function
        logger.debug(f"Added conditional edge from: {start_node}")
    
    def set_entry_point(self, node_name: str):
        """Set the entry point for the graph.
        
        Args:
            node_name: The name of the node to use as the entry point
        """
        if node_name not in self.nodes:
            raise ValueError(f"Node {node_name} not found in graph")
        self.entry_point = node_name
        logger.debug(f"Set entry point to: {node_name}")
    
    def compile(self):
        """Compile the graph into a runnable function.
        
        Returns:
            A function that takes a state and runs the graph
        """
        if not self.entry_point:
            raise ValueError("Entry point not set")
        
        def run_graph(state=None):
            """Run the graph with the given state.
            
            Args:
                state: The initial state (optional)
                
            Returns:
                The final state after running the graph
            """
            # Initialize state if not provided
            if state is None:
                state = {}
            
            current_node = self.entry_point
            logger.info(f"Starting graph execution at node: {current_node}")
            
            # Run until we reach END or run out of nodes
            while current_node != "END" and current_node is not None:
                # Execute the current node
                node_function = self.nodes.get(current_node)
                if not node_function:
                    logger.error(f"Node {current_node} not found in graph")
                    break
                
                logger.debug(f"Executing node: {current_node}")
                state = node_function(state)
                
                # Determine the next node
                if current_node in self.conditional_edges:
                    # Use conditional edge
                    condition_function = self.conditional_edges[current_node]
                    next_node = condition_function(state)
                    logger.debug(f"Conditional edge from {current_node} -> {next_node}")
                elif current_node in self.edges:
                    # Use first edge
                    next_node = self.edges[current_node][0]
                    logger.debug(f"Following edge {current_node} -> {next_node}")
                else:
                    # No more edges
                    logger.debug(f"No edges from {current_node}, ending execution")
                    break
                
                current_node = next_node
            
            logger.info("Graph execution complete")
            return state
        
        logger.info("Graph compiled successfully")
        return run_graph

# Define a constant for the END node
END = "END"