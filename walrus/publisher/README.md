# 🐋 Walrus Publisher Node Setup Guide

This directory contains everything you need to set up and run a Walrus publisher node.

## 📁 What's a Publisher Node?

A **Walrus Publisher Node** is a service that:
- Accepts blob upload requests from clients
- Coordinates with storage nodes to store data
- Provides an endpoint for the Walrus network
- Earns rewards for facilitating storage operations

## 🚀 Quick Start

### 1. Complete Setup (Recommended)
```bash
# Run complete automated setup
python3 publisher_setup.py setup

# This will:
# - Check Walrus CLI installation
# - Create configuration files
# - Generate a new wallet
# - Attempt to get WAL tokens (testnet)
# - Show system information
```

### 2. Start Your Publisher Node
```bash
# Run the combined daemon (publisher + aggregator)
python3 publisher_setup.py daemon

# Your node will be available at: http://0.0.0.0:8080
```

## 🔧 Manual Setup Steps

If you prefer step-by-step setup:

### Step 1: Create Configuration
```bash
python3 publisher_setup.py config --address 0.0.0.0:8080
```

### Step 2: Generate Wallet
```bash
python3 publisher_setup.py wallet
```

### Step 3: Get WAL Tokens (Testnet Only)
```bash
python3 publisher_setup.py get-wal
```

### Step 4: Stake Tokens
```bash
python3 publisher_setup.py stake 1000
```

### Step 5: Start Services

Choose one option:

**Option A: Combined Daemon (Recommended)**
```bash
python3 publisher_setup.py daemon
```

**Option B: Publisher Only**
```bash
python3 publisher_setup.py publisher
```

**Option C: Aggregator Only**
```bash
python3 publisher_setup.py aggregator
```

## 📊 Monitoring Your Node

### Check System Information
```bash
python3 publisher_setup.py info
```

### Check Storage Node Health
```bash
python3 publisher_setup.py health
```

### List Your Blobs
```bash
python3 publisher_setup.py blobs
```

## ⚙️ Configuration

Configuration is stored at `~/.walrus/publisher_config.yaml`:

```yaml
network_address: '0.0.0.0:8080'
storage_path: './walrus_storage'
max_blob_size: '1GB'
epochs: 10
stake_amount: 1000
```

## 🔗 Integration with Client

Your publisher node will work with the main Walrus client (`../walrus_cli.py`):

```bash
# From the parent directory, push to your local publisher
cd ..
python3 walrus_cli.py push my-directory
```

The client will automatically discover and use available publisher nodes in the network.

## 📈 Node Types

- **Publisher**: Accepts client upload requests
- **Aggregator**: Coordinates storage across nodes  
- **Daemon**: Combined publisher + aggregator (recommended)

## 🔒 Security & Requirements

- **Firewall**: Ensure port 8080 is accessible
- **Wallet**: Keep your wallet keys secure and backed up
- **Tokens**: You need SUI/WAL tokens for staking and operations
- **Network**: Stable internet connection required

## 💰 Economics

- **Staking**: Required to participate as a publisher
- **Rewards**: Earn tokens for facilitating storage
- **Costs**: Gas fees for on-chain transactions

## 📞 Troubleshooting

### Common Issues

**"Port already in use"**
```bash
python3 publisher_setup.py daemon --address 0.0.0.0:8081
```

**"Insufficient tokens"**
```bash
# Get more tokens (testnet only)
python3 publisher_setup.py get-wal
```

**"Wallet not found"**
```bash
python3 publisher_setup.py wallet
```

### Getting Help
```bash
# Show all available commands
python3 publisher_setup.py --help

# Get help for specific command
python3 publisher_setup.py daemon --help
```

## 🏭 Production Deployment

For production use:

1. **Systemd Service**: Create a service file for auto-restart
2. **Monitoring**: Set up monitoring and alerting
3. **Backup**: Regular wallet and config backups
4. **Updates**: Keep Walrus CLI updated
5. **Security**: Use firewall and security best practices

## 🌐 Network Participation

Once your publisher is running:

1. It becomes part of the Walrus storage network
2. Clients can discover and use your publisher
3. You earn rewards for successful storage operations
4. Your node helps decentralize the storage network

## ✅ Success Indicators

Your node is working correctly when:
- ✅ No error messages in logs
- ✅ Health checks pass
- ✅ System info shows your node
- ✅ Port is accessible from external clients
- ✅ You can upload blobs through your node

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `setup` | Complete automated setup |
| `config` | Create configuration file |
| `wallet` | Generate new wallet |
| `get-wal` | Get WAL tokens (testnet) |
| `stake` | Stake tokens |
| `publisher` | Run publisher service |
| `aggregator` | Run aggregator service |
| `daemon` | Run combined service |
| `info` | Show system information |
| `health` | Check node health |
| `blobs` | List your blobs |

Start with `python3 publisher_setup.py setup` and follow the prompts!