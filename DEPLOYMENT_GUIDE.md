# Deployment Guide for VEML7700 Viam Module

This guide will walk you through setting up the GitHub repository and deploying your VEML7700 module to Viam.

## Prerequisites

- A GitHub account
- A Viam account (https://app.viam.com)
- Viam CLI installed (optional for local testing)

## Step 1: Create GitHub Repository

1. Go to GitHub and create a new repository named `viam-veml7700-module`
2. Make it public (required for Viam public modules)
3. Don't initialize with README (we already have files)

## Step 2: Initialize Git and Push to GitHub

Run these commands in the VEML7700 directory:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: VEML7700 Viam module"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/Wootter/viam-veml7700-module.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Get Viam API Keys

1. Go to https://app.viam.com
2. Navigate to your organization settings
3. Go to "API Keys" section
4. Click "Generate API Key"
5. Save both the **Key ID** and **Key Value** (you'll need these next)

## Step 4: Add GitHub Secrets

1. Go to your GitHub repository
2. Click on "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret" and add:
   - Name: `VIAM_API_KEY_ID`
   - Value: [Your Viam API Key ID]
4. Click "New repository secret" again and add:
   - Name: `VIAM_API_KEY`
   - Value: [Your Viam API Key Value]

## Step 5: Create and Push a Version Tag

The GitHub Action triggers on version tags. To create your first release:

```bash
# Create a version tag
git tag 1.0.0

# Push the tag to GitHub
git push origin 1.0.0
```

This will trigger the GitHub Action to:
1. Build the module
2. Create the module in Viam (if it doesn't exist)
3. Publish the module to Viam

## Step 6: Verify Deployment

1. Go to https://app.viam.com
2. Navigate to your organization
3. Go to "Registry" or "Modules"
4. You should see `wootter:veml7700-sensor` listed

## Step 7: Use the Module in Your Robot

1. In the Viam app, go to your robot configuration
2. Click "Create component"
3. Select "sensor" as the type
4. Search for "wootter:veml7700-sensor"
5. Add it with configuration:
   ```json
   {
     "name": "light-sensor",
     "model": "wootter:veml7700-sensor:linux",
     "type": "sensor",
     "namespace": "rdk",
     "attributes": {
       "bus_number": 1
     }
   }
   ```

## Troubleshooting

### GitHub Action fails
- Check that your secrets are correctly set
- Verify the API keys are valid
- Check the Actions tab for detailed error logs

### Module not appearing in Viam
- Make sure the module creation step succeeded
- Check that your organization namespace is "wootter"
- Verify the tag format is correct (e.g., 1.0.0)

### Sensor not reading
- Verify I2C is enabled on your Raspberry Pi: `sudo raspi-config`
- Check sensor connections
- Test I2C bus: `i2cdetect -y 1` (should show device at 0x10)

## Updating the Module

To release a new version:

```bash
# Make your changes and commit
git add .
git commit -m "Description of changes"
git push

# Create a new version tag (increment the version)
git tag 1.0.1
git push origin 1.0.1
```

## Local Testing (Optional)

To test the module locally before deploying:

```bash
# Install Viam CLI
curl -o viam https://storage.googleapis.com/packages.viam.com/apps/viam-cli/viam-cli-stable-linux-amd64
chmod +x viam
sudo mv viam /usr/local/bin/

# Login to Viam
viam login

# Build and test locally
make module.tar.gz
```

## Support

For issues related to:
- **Viam platform**: https://docs.viam.com
- **This module**: Create an issue on GitHub
- **VEML7700 sensor**: Check sensor datasheet and wiring
