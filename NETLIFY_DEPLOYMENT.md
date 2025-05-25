# Deploying to Netlify

This guide will walk you through the process of deploying your Face Detection Web App to Netlify.

## Prerequisites

- A GitHub account
- A Netlify account
- Your project pushed to GitHub

## Method 1: Deploy from GitHub

This is the recommended method as it allows for continuous deployment.

1. **Push your code to GitHub**
   Make sure your code is pushed to a GitHub repository.

2. **Log in to Netlify**
   Go to [netlify.com](https://www.netlify.com/) and log in with your account.

3. **Create a new site**
   Click on the "New site from Git" button.

4. **Connect to GitHub**
   Choose GitHub as your Git provider and authorize Netlify to access your repositories.

5. **Select your repository**
   Find and select your face detection repository from the list.

6. **Configure build settings**
   - Build command: (leave empty)
   - Publish directory: `.` (Use the root directory)
   
   Note: The application now loads models from a CDN, so no build command is needed.

7. **Deploy the site**
   Click on the "Deploy site" button.

8. **Wait for the deployment**
   Netlify will build and deploy your site. This may take a few minutes.

9. **Access your site**
   Once the deployment is complete, you can access your site at the URL provided by Netlify.

## Method 2: Deploy using Netlify CLI

If you prefer using the command line:

1. **Install Netlify CLI**
   ```
   npm install -g netlify-cli
   ```

2. **Login to Netlify**
   ```
   netlify login
   ```

3. **Initialize your site**
   ```
   netlify init
   ```

4. **Deploy your site**
   ```
   netlify deploy --prod
   ```

5. **Specify the publish directory**
   When prompted, enter `.` (current directory) as the publish directory.

## Troubleshooting

### Camera Access Issues

If users are having issues with camera access:

1. Make sure your site is being served over HTTPS (Netlify does this by default)
2. Users should grant camera permissions when prompted by the browser
3. Some browsers or devices may have restrictions on camera access

### Model Loading Issues

If the face detection models aren't loading:

1. Check the browser console for errors
2. Verify that the models were correctly downloaded and are in the `models` directory
3. Make sure the paths in `script.js` are correct

### CORS Issues

If you're experiencing CORS issues:

1. Check that the `netlify.toml` file has the correct CORS headers
2. Verify that the models are being loaded from the same domain

## Custom Domain

To use a custom domain:

1. Go to your site settings in Netlify
2. Click on "Domain settings"
3. Follow the instructions to add and configure your custom domain

## Environment Variables

If you need to use environment variables:

1. Go to your site settings in Netlify
2. Click on "Build & deploy" > "Environment"
3. Add your environment variables

## Continuous Deployment

With GitHub integration, Netlify will automatically deploy your site whenever you push changes to your repository. To disable this:

1. Go to your site settings in Netlify
2. Click on "Build & deploy" > "Continuous Deployment"
3. Stop automatic publishing by clicking on "Stop auto publishing" 