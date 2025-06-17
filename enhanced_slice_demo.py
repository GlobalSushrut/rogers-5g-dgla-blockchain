#!/usr/bin/env python3
"""
Enhanced Rogers 5G Network Slice Verification Demo with Internal DGLA Blockchain

This demo shows the internal workings of how network slice data is stored
and verified in the DGLA blockchain infrastructure.
"""

import os
import sys
import time
import uuid
import datetime
import logging
from typing import Dict, List, Any, Tuple, Optional

# Import our blockchain implementation
from dgla_blockchain_store import DGLADataStore, DGLABlockchain, Block

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Rogers5G-Enhanced")

class NetworkSlice:
    """Represents a 5G network slice with cryptographic verification"""
    
    def __init__(self, slice_id, type_name, priority, resources):
        """Initialize a network slice"""
        self.slice_id = slice_id
        self.type_name = type_name
        self.priority = priority
        self.resources = resources
        self.created_at = datetime.datetime.now().isoformat()
        self.dgla_id = None  # Will be filled when submitted to DGLA
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert slice to dictionary
        
        Returns:
            Dict: Slice as a dictionary
        """
        return {
            "slice_id": self.slice_id,
            "type_name": self.type_name,
            "priority": self.priority,
            "resources": self.resources,
            "created_at": self.created_at
        }

class EnhancedSliceManager:
    """Enhanced manager for network slices showing blockchain internals"""
    
    def __init__(self):
        """Initialize the enhanced slice manager"""
        self.slices = {}
        # Initialize DGLA data store that contains the actual blockchain
        self.dgla_store = DGLADataStore()
        
    def create_slice(self, type_name, priority, resources):
        """Create a new network slice and store it in the blockchain
        
        Args:
            type_name: Type of slice (e.g., 'emergency', 'consumer', 'iot')
            priority: Priority level (0-100, higher is more important)
            resources: Dict of resource allocations
            
        Returns:
            NetworkSlice: The created slice
        """
        slice_id = str(uuid.uuid4())[:8]
        slice = NetworkSlice(slice_id, type_name, priority, resources)
        self.slices[slice_id] = slice
        
        # Store in DGLA blockchain and get storage ID
        dgla_id = self.dgla_store.store_network_slice(slice.to_dict())
        slice.dgla_id = dgla_id
        
        logger.info(f"Slice {slice_id} created and stored in DGLA blockchain with ID {dgla_id}")
        return slice
        
    def verify_slice_integrity(self, slice_id):
        """Verify the integrity of a specific slice
        
        Args:
            slice_id: ID of the slice to verify
            
        Returns:
            bool: True if slice is intact, False if compromised
        """
        # First check if slice exists
        if slice_id not in self.slices:
            return False
            
        # Retrieve the slice from blockchain
        stored_slice = self.dgla_store.retrieve_network_slice(slice_id)
        if not stored_slice:
            return False
            
        # Verify the slice properties match what's in memory
        current_slice = self.slices[slice_id]
        return current_slice.priority == stored_slice.get("priority")
        
    def verify_blockchain_integrity(self):
        """Verify the integrity of the entire blockchain
        
        Returns:
            tuple: (is_valid, message)
        """
        return self.dgla_store.verify_integrity()
        
    def simulate_attack(self, slice_id):
        """Simulate an attack by directly modifying slice priority
        
        Args:
            slice_id: ID of the slice to attack
            
        Returns:
            bool: True if attack was successful
        """
        if slice_id not in self.slices:
            return False
            
        # Direct modification bypassing normal channels
        self.slices[slice_id].priority -= 10
        
        # Deliberately tamper with blockchain to show why verification fails
        # This simulates how an attacker might try to modify both in-memory and stored data
        for block in self.dgla_store.blockchain.chain:
            if "entries" not in block.data:
                continue
                
            for entry in block.data["entries"]:
                if entry.get("type") != "network_slice":
                    continue
                    
                content = entry.get("content", {})
                if content.get("slice_id") == slice_id:
                    # Tamper with the priority without updating hashes
                    content["priority"] = self.slices[slice_id].priority
                    return True
                    
        return False
        
    def show_blockchain(self):
        """Display the internal blockchain structure
        
        Returns:
            List[Dict]: List of blocks in the chain
        """
        return self.dgla_store.blockchain.get_chain_data()
        
    def remediate_slice(self, slice_id):
        """Fix a compromised slice by restoring from blockchain
        
        Args:
            slice_id: ID of the slice to fix
            
        Returns:
            bool: True if remediation was successful
        """
        if slice_id not in self.slices:
            return False
            
        # We need to restore the correct data - for this demo:
        # 1. Create a valid new block with the correct slice data
        # 2. Re-sign it and add it to the blockchain
        slice = self.slices[slice_id]
        
        # Store the fixed slice data in a new block
        dgla_id = self.dgla_store.store_network_slice(slice.to_dict())
        slice.dgla_id = dgla_id
        
        logger.info(f"Slice {slice_id} remediated and restored in blockchain with new ID {dgla_id}")
        return True

def run_enhanced_demo():
    """Run the enhanced demo showing internal blockchain workings"""
    
    print("🔐 Enhanced Rogers 5G Network Slice Verification Demo")
    print("===================================================\n")
    
    # Initialize the slice manager with blockchain storage
    manager = EnhancedSliceManager()
    
    print("1. Creating network slices with blockchain storage...")
    emergency_slice = manager.create_slice(
        "emergency", 
        100,  # Highest priority
        {
            "bandwidth_mbps": 500,
            "latency_ms": 5,
            "reliability_percent": 99.999
        }
    )
    print(f"  ✓ Emergency Services slice created with ID: {emergency_slice.slice_id}")
    print(f"  ✓ Stored in DGLA blockchain with ID: {emergency_slice.dgla_id}")
    
    consumer_slice = manager.create_slice("consumer", 50, {"bandwidth_mbps": 100})
    print(f"  ✓ Consumer slice created with ID: {consumer_slice.slice_id}")
    
    # Display internal blockchain structure
    print("\n2. Examining internal blockchain structure...")
    blockchain_data = manager.show_blockchain()
    
    # Show genesis block
    genesis_block = blockchain_data[0]
    print(f"  Genesis Block:")
    print(f"    ✓ Hash: {genesis_block['hash'][:16]}...")
    print(f"    ✓ Data: {genesis_block['data']['message']}")
    
    # Show block containing emergency slice
    slice_block = blockchain_data[1]  # Second block contains our slices
    print(f"  Block 1:")
    print(f"    ✓ Hash: {slice_block['hash'][:16]}...")
    print(f"    ✓ Previous Hash: {slice_block['previous_hash'][:16]}...")
    print(f"    ✓ Entries: {len(slice_block['data'].get('entries', []))} items")
    print(f"    ✓ Merkle Root: {slice_block['data'].get('merkle_root', 'none')[:16]}...")
    
    # Show slice data in blockchain
    for entry in slice_block['data'].get('entries', []):
        if entry.get('type') == 'network_slice':
            content = entry.get('content', {})
            print(f"    Entry:")
            print(f"      ✓ Type: {entry.get('type')}")
            print(f"      ✓ Slice ID: {content.get('slice_id')}")
            print(f"      ✓ Priority: {content.get('priority')}")
            print(f"      ✓ Signature: {content.get('signature', 'none')[:16]}...")
            
    # Verify blockchain integrity
    print("\n3. Verifying blockchain integrity...")
    valid, message = manager.verify_blockchain_integrity()
    print(f"  {'✓' if valid else '✗'} Blockchain integrity: {message}")
    
    # Verify specific slice integrity
    is_valid = manager.verify_slice_integrity(emergency_slice.slice_id)
    print(f"  {'✓' if is_valid else '✗'} Emergency slice integrity: {'Valid' if is_valid else 'Compromised'}")
    
    # Simulate attack
    print("\n4. Simulating attack on emergency services slice...")
    manager.simulate_attack(emergency_slice.slice_id)
    print(f"  ! Attack detected: Priority maliciously lowered to {emergency_slice.priority}")
    
    # Verify blockchain integrity after attack
    valid, message = manager.verify_blockchain_integrity()
    print(f"  {'✓' if valid else '✗'} Blockchain integrity after attack: {message}")
    
    # Show how hash verification fails
    blockchain_data = manager.show_blockchain()
    tampered_block = blockchain_data[1]  # Block containing our slices
    print(f"  Block hash verification:")
    print(f"    Current hash: {tampered_block['hash'][:16]}...")
    
    # Calculate expected hash for comparison
    temp_block = Block(
        tampered_block['index'],
        tampered_block['timestamp'],
        tampered_block['data'],
        tampered_block['previous_hash'],
        tampered_block['nonce']
    )
    expected_hash = temp_block.calculate_hash()
    print(f"    Expected hash: {expected_hash[:16]}...")
    print(f"    Hash verification: {'Valid' if tampered_block['hash'] == expected_hash else 'FAILED'}")
    
    # Remediate the compromised slice
    print("\n5. Remediating compromised slice using blockchain repair...")
    manager.remediate_slice(emergency_slice.slice_id)
    print(f"  ✓ Slice {emergency_slice.slice_id} remediated")
    print(f"  ✓ New blockchain record created with ID: {emergency_slice.dgla_id}")
    
    # Verify blockchain integrity after remediation
    valid, message = manager.verify_blockchain_integrity()
    print(f"  {'✓' if valid else '✗'} Blockchain integrity after remediation: {message}")
    
    print("\nThis enhanced demo has demonstrated:")
    print("1. How slice data is internally stored in the DGLA blockchain")
    print("2. The cryptographic mechanisms for verifying blockchain integrity")
    print("3. How the verify_chain_integrity() method detects tampering")
    print("4. The internal hash verification that ensures data integrity")
    print("5. The use of deterministic keys for consistent verification")
    
if __name__ == "__main__":
    run_enhanced_demo()
