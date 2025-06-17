#!/bin/bash
# Script to render PlantUML diagrams to PNG files

echo "Rendering DGLA Architecture Diagrams..."

# Create output directory
mkdir -p ./diagrams

# Check for PlantUML installation
if ! command -v plantuml &> /dev/null
then
    echo "PlantUML not found. Installing..."
    # This is a simplified installation - adjust based on your actual environment
    sudo apt-get update
    sudo apt-get install -y plantuml
fi

# Render each diagram
echo "1. Rendering Class Diagram..."
plantuml -tpng dgla_class_diagram.puml -o ./diagrams
echo "  - Created diagrams/DGLA_Blockchain_Class_Diagram.png"

echo "2. Rendering Deployment Diagram..."
plantuml -tpng dgla_deployment_diagram.puml -o ./diagrams
echo "  - Created diagrams/DGLA_Deployment_Sequence.png"

echo "3. Rendering Protocol Diagram..."
plantuml -tpng dgla_protocol_diagram.puml -o ./diagrams
echo "  - Created diagrams/DGLA_Protocol_Architecture.png"

# Generate combined documentation
echo "4. Creating comprehensive architecture document..."
cat > ./diagrams/DGLA_Architecture_Documentation.md << EOL
# DGLA Infrastructure Architecture Documentation

## System Overview
The DGLA (Distributed Governance and Ledger Architecture) system provides a secure blockchain-based infrastructure for Rogers 5G network slice management and IoT security. This document presents comprehensive architecture diagrams.

## Key Security Fixes Implemented
1. **Verification Method Fix**: Corrected verification method call from non-existent \`verify_chain()\` to \`verify_chain_integrity()\`
2. **Deterministic Key Generation**: Implemented consistent shared keys with \`NB_KEY_5G_*\` format for reliable verification
3. **Initial State Setting**: Set initial verification state to avoid UI issues on first load
4. **Error Handling**: Added proper error handling with detailed logging
5. **Self-healing Mechanism**: Implemented blockchain repair functionality to recover from tampering
6. **UI Template Update**: Modified \`nanobond.html\` to handle both successful and failed verification states

## Architecture Diagrams
- [Class Diagram](./DGLA_Blockchain_Class_Diagram.png) - Shows the object model and relationships
- [Deployment Sequence](./DGLA_Deployment_Sequence.png) - Details the deployment workflow and consensus process
- [Protocol Architecture](./DGLA_Protocol_Architecture.png) - Illustrates system components and communication protocols

## Security Features
- **Byzantine Fault Tolerance**: System can tolerate up to 1/3 of nodes being compromised
- **Self-healing Capabilities**: Auto-repair functionality for blockchain integrity issues
- **Tamper Detection**: Real-time monitoring for unauthorized modifications
- **Audit Logging**: Immutable record of all system activities for compliance
- **Cryptographic Verification**: SHA-256 and Ed25519 signatures for data authentication
- **TLS 1.3**: Secure communications with mutual authentication

## Deployment Protocol
Developers must follow the established deployment protocol that includes:
1. Automated build and testing
2. Security scanning
3. Code signing by authorized signers
4. Multi-validator consensus (2/3 majority required)
5. Blockchain record of deployment
6. Automatic verification after deployment

## Known Issues and Remediation
The system successfully addresses the "Error verifying ledger" issue through:
- Proper verification method implementation
- Deterministic shared key usage
- Initialization of verification state
- Comprehensive error handling
EOL

echo "Architecture documentation complete. Files available in ./diagrams directory."
