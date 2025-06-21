# CineDialogue: Movie Dialogue and Image Generator

## Overview
CineDialogue is an AI-powered application that generates creative dialogue and visual scenes based on popular movies from IMDb's top-rated list. This application combines web scraping, natural language processing, and image generation to create a comprehensive movie-inspired content generator.

## Features
- Automatic fetching of IMDb's top-rated movies
- Detailed movie information display including cast, ratings, and storyline
- AI-generated dialogue between movie characters with customizable parameters
- AI-generated cinematic scene visuals based on movie context
- Multiple style options for image generation (Marvel, Futuristic, Cartoon, Realistic)
- Automatic saving of generated content

## Technical Implementation
- **User Interface**: Built with Tkinter for a clean, responsive GUI
- **Text Generation**: Powered by Google's Gemini 2.0 Flash model
- **Image Generation**: Implemented using Vertex AI's Imagen 3.0
- **Web Scraping**: Utilizes BeautifulSoup and Cinemagoer for movie data collection
- **Architecture**: Modular design with separation of concerns (UI, generators, configuration, utilities)

## Requirements
- Python 3.8+
- Tkinter
- Google Gemini AI API key
- Vertex AI project access
- Required Python packages:
  - requests
  - beautifulsoup4
  - google-generativeai
  - vertexai
  - Pillow
  - imdb-py

## Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your API credentials in `config.py`
4. Run the application: `python main.py`

## Use Cases
- Creative writing inspiration for screenwriters
- Visual concept development for filmmakers
- Educational tool for film studies
- Entertainment for movie enthusiasts

## Project Structure
- `main.py`: Application entry point
- `config.py`: Configuration variables and constants
- `ui.py`: User interface components
- `generator.py`: AI text and image generation logic
- `utils.py`: Helper functions and utilities
