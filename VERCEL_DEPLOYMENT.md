# 🚀 Vercel Deployment Guide

This guide will help you deploy the Audio Trimmer application to Vercel.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Node.js**: Install Node.js (for Vercel CLI)

## 🔧 Deployment Steps

### Method 1: Using Vercel Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Deploy via Vercel Dashboard**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect it's a Python project
   - Click "Deploy"

### Method 2: Using Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

## ⚙️ Configuration

The project includes these configuration files:

- `vercel.json`: Vercel deployment configuration
- `requirements.txt`: Python dependencies
- `runtime.txt`: Python version specification
- `app.py`: Main Flask application

## 🔍 Important Notes

### Limitations
- **File Size**: Maximum 50MB per file upload
- **Execution Time**: Maximum 60 seconds per request
- **Memory**: Limited to 1024MB per function

### Audio Processing
- The app uses `pydub` and `librosa` for audio processing
- FFmpeg is required for some audio formats (handled by pydub)
- Processing happens in memory and temporary files

### Supported Formats
- **Input**: WAV, MP3, OGG, M4A, FLAC, MP4
- **Output**: MP3, WAV, FLAC

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version in `runtime.txt` is supported

2. **Audio Processing Errors**
   - Verify file format is supported
   - Check file size is under 50MB
   - Ensure audio file is not corrupted

3. **Timeout Errors**
   - Large audio files may take longer than 60 seconds
   - Consider processing smaller files or using local deployment

### Environment Variables
No environment variables are required for basic functionality.

## 📊 Performance

- **Cold Start**: ~2-5 seconds for first request
- **Processing Speed**: Depends on audio file size and complexity
- **Concurrent Users**: Vercel handles scaling automatically

## 🔄 Updates

To update your deployment:

1. Make changes to your code
2. Commit and push to GitHub
3. Vercel will automatically redeploy

## 📞 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify all files are committed to GitHub
3. Ensure `app.py` is the main entry point
4. Check that `vercel.json` is properly configured

## 🎯 Next Steps

After successful deployment:
1. Test with different audio files
2. Monitor performance in Vercel dashboard
3. Consider setting up custom domain
4. Configure environment variables if needed 