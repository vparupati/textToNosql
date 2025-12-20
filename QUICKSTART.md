# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup Environment (1 minute)

```bash
cd /Users/vparupati/CapStone/textToNosql

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key (1 minute)

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
# Add: OPENAI_API_KEY=your_key_here
```

### 3. Run Demo (3 minutes)

```bash
# Run the demo with sample data
python src/main.py --mode demo
```

This will:
- ✅ Load sample e-commerce data
- ✅ Run 4 example queries
- ✅ Show the complete SMART pipeline
- ✅ Display results

**No MongoDB required for demo!** (It will show warnings but still demonstrate the pipeline)

## 🎯 Try Interactive Mode

```bash
python src/main.py --mode interactive
```

Example queries to try:
- "Find all products"
- "Count products in Electronics category"
- "What is the average price of products?"
- "Show me customers from New York"

Type `quit` or `exit` to stop.

## 📊 With MongoDB (Optional)

### Local MongoDB

```bash
# Install MongoDB
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Run demo (will now execute queries!)
python src/main.py --mode demo
```

### MongoDB Atlas (Cloud)

1. Create free cluster at [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas)
2. Get connection string
3. Update `configs/config.yaml`:
   ```yaml
   mongodb:
     uri: "your_mongodb_atlas_uri"
   ```
4. Run demo

## 📓 Explore the Notebook

```bash
# Install Jupyter if not already installed
pip install jupyter

# Start Jupyter
jupyter notebook notebooks/demo.ipynb
```

The notebook provides:
- Step-by-step walkthrough
- Interactive examples
- Visualization of pipeline
- Evaluation examples

## 📁 Add Your Own Data

### Option 1: Use TEND Dataset

```bash
# Copy your TEND dataset
cp -r /path/to/tend/data data/raw/tend/

# Update config.yaml
# Then run:
python src/main.py --mode eval --test-file data/raw/tend/test.json
```

### Option 2: Use Converted Spider Data

```bash
# Copy converted Spider data
cp -r /path/to/spider/converted data/raw/spider/

# Update paths in config.yaml
```

### Option 3: Keep Using Samples

Sample data is already included in `data/samples/`:
- `ecommerce.json` - Products & Customers
- `school.json` - Students
- `training_examples.json` - 15 query examples

## 🔧 Configuration

Edit `configs/config.yaml` to customize:

```yaml
# Switch LLM provider
models:
  llm_provider: "anthropic"  # or "openai", "local"
  llm_model: "claude-3-5-sonnet-20241022"

# Adjust RAG settings
rag:
  enabled: true
  num_examples: 5  # Retrieve more examples
  
# Set MongoDB
mongodb:
  uri: "mongodb://localhost:27017/"  # or Atlas URI
```

## 🆘 Troubleshooting

### "OpenAI API key not found"
```bash
# Make sure .env file exists and has your key
echo "OPENAI_API_KEY=sk-..." > .env
```

### "MongoDB connection failed"
```bash
# For demo, MongoDB is optional
# To use MongoDB:
brew services start mongodb-community
# Or use MongoDB Atlas cloud
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Next Steps

1. ✅ Run demo mode
2. ✅ Try interactive mode  
3. ✅ Explore Jupyter notebook
4. ✅ Read [README.md](README.md) for full documentation
5. ✅ Read [walkthrough.md](../../../.gemini/antigravity/brain/ea50d139-6011-4b10-88e5-36203c55312e/walkthrough.md) for implementation details

## 🎓 Learning Path

**Beginner**: Demo → Interactive → Notebook  
**Intermediate**: Add your data → Configure RAG → Evaluate  
**Advanced**: Fine-tune SLMs → Extend pipeline → Deploy

---

**Questions?** Check:
- [README.md](README.md) - Full documentation
- [Walkthrough](../../../.gemini/antigravity/brain/ea50d139-6011-4b10-88e5-36203c55312e/walkthrough.md) - Implementation details
- [data/raw/README.md](data/raw/README.md) - Data setup guide
