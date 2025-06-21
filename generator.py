import google.generativeai as genai
from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
import io
from utils import create_fallback_image, create_error_image
from config import (
    GEMINI_MODEL_NAME,
    VERTEX_AI_LOCATION,
    VERTEX_AI_IMAGE_MODEL,
    API_KEY,
    PROJECT_ID
)

class ContentGenerator:
    def __init__(self):
        self.gemini_model = None
        self.vertex_ai_model = None
        self.initialize_gemini()
        self.initialize_vertex_ai()

    def initialize_gemini(self):
        """Initialize the Gemini text generation model"""
        try:
            genai.configure(api_key=API_KEY)
            self.gemini_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
            print(f"Successfully initialized Gemini with model: {GEMINI_MODEL_NAME}")
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.gemini_model = None

    def initialize_vertex_ai(self):
        """Initialize the Vertex AI image generation model"""
        try:
            vertexai.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)
            self.vertex_ai_model = ImageGenerationModel.from_pretrained(VERTEX_AI_IMAGE_MODEL)
            print(f"Successfully initialized Vertex AI with model: {VERTEX_AI_IMAGE_MODEL}")
        except Exception as e:
            print(f"Error initializing Vertex AI: {e}")
            self.vertex_ai_model = None

    def generate_dialogue(self, prompt):
        """Generate dialogue using the Gemini model"""
        try:
            if not self.gemini_model:
                raise Exception("Gemini model not initialized")

            enhanced_prompt = prompt + " Format the dialogue with character names in bold (using ** markers) followed by their lines. For example: **Character Name**: Their dialogue line."
            response = self.gemini_model.generate_content(enhanced_prompt)
            return response.text
        except Exception as e:
            print(f"Dialogue generation failed: {e}")
            return f"Failed to generate dialogue: {str(e)}"

    def generate_movie_dialogue(self, movie_title, storyline, character_names, num_characters, dialogue_length):
        """Generate a dialogue for movie characters"""
        character_str = ", ".join(character_names[:num_characters])
        dialogue_prompt = f"""Generate a dialogue between {num_characters} characters: {character_str}, with a maximum of {dialogue_length} words, based on the following storyline: {storyline}, and movie: {movie_title}. 
        The dialogue should reflect the movie's tone and the relationships between characters. 
        Generate the dialogue in the following format:
        **Character Name**: Spoken line.
        **Another Character Name**: Another spoken line.
        Only one character name can come before each sentence. So, think of it like a play script and write it."""

        return self.generate_dialogue(dialogue_prompt)

    def generate_scene_description(self, movie_title, storyline):
        """Generate a scene description for image generation"""
        scene_description_prompt = f"""Based on the movie '{movie_title}' with storyline: {storyline}, create a detailed scene description for image generation.
        Include visual elements like:
        - The specific setting and time of day
        - Lighting conditions and atmosphere
        - Important props or objects in the scene
        - The physical appearance and positioning of characters
        - Any distinctive visual style elements from the movie"""

        return self.generate_dialogue(scene_description_prompt)

    def generate_image(self, prompt):
        """Generate an image using the Vertex AI model"""
        try:
            if not self.vertex_ai_model:
                raise Exception("Vertex AI model not initialized")

            # Truncate prompt if too long
            if len(prompt) > 1000:
                prompt = prompt[:1000] + "..."

            response = self.vertex_ai_model.generate_images(
                prompt=prompt,
                number_of_images=1
            )

            if hasattr(response, 'images') and response.images:
                img = response.images[0]

                if hasattr(img, '_image_bytes'):
                    return img._image_bytes

                if hasattr(img, '_loaded_bytes'):
                    return img._loaded_bytes

                if hasattr(img, 'bytes'):
                    return img.bytes

                if hasattr(img, '_pil_image') and img._pil_image is not None:
                    img_byte_arr = io.BytesIO()
                    img._pil_image.save(img_byte_arr, format='PNG')
                    return img_byte_arr.getvalue()

            return create_fallback_image()

        except Exception as e:
            print(f"Exception in image generation: {e}")
            return create_error_image(e)

    def generate_movie_image(self, movie_title, scene_description, location, characters_description, style):
        """Generate a movie scene image"""
        image_prompt = f"""A cinematic scene from the movie '{movie_title}'. {scene_description}
        Setting: {location}, Characters: {characters_description}
        Atmosphere: {movie_title}'s atmosphere
        Style: {style}, highly detailed, professional movie production quality"""

        return self.generate_image(image_prompt)
