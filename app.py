import streamlit as st
import time
import re
from datetime import datetime
import io
import os
from dotenv import load_dotenv
import google.generativeai as genai


st.set_page_config(
    page_title="AI Story Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .story-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        color: #000000;
        line-height: 1.6;
    }
    .parameter-info {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


load_dotenv()

genai_api_key = os.getenv("GEMINI_API_KEY", "")
if genai_api_key:
    genai.configure(api_key=genai_api_key)

class StoryGenerator:
    def __init__(self):
        self.genres = {
            "Fantasy": "magical realms, mythical creatures, and epic adventures",
            "Sci-Fi": "futuristic technology, space exploration, and scientific concepts",
            "Romance": "love stories, relationships, and emotional connections",
            "Mystery": "puzzles, detective work, and suspenseful revelations",
            "Horror": "scary elements, supernatural occurrences, and spine-chilling moments",
            "Adventure": "exciting journeys, daring exploits, and thrilling experiences",
            "Literary Fiction": "character-driven narratives with deep themes and realistic settings",
            "Comedy": "humorous situations, witty dialogue, and funny characters"
        }

        self.tones = {
            "Serious": "maintain a serious, thoughtful tone throughout",
            "Humorous": "include humor and light-hearted elements",
            "Dark": "create a darker, more intense atmosphere",
            "Uplifting": "inspire and uplift with positive themes",
            "Mysterious": "maintain an air of mystery and intrigue",
            "Dramatic": "emphasize emotional intensity and conflict"
        }

        self.lengths = {
            "Short": {"words": 200, "description": "Quick read, ~200 words"},
            "Medium": {"words": 500, "description": "Standard story, ~500 words"},
            "Long": {"words": 1000, "description": "Extended narrative, ~1000 words"}
        }

    def enhance_prompt(self, prompt, genre, tone):
        """Enhance the user prompt with genre and tone information"""
        genre_desc = self.genres.get(genre, "")
        tone_desc = self.tones.get(tone, "")

        enhanced_prompt = f"""
        Write a creative {genre.lower()} story based on this prompt: "{prompt}"

        Genre requirements: {genre_desc}
        Tone: {tone_desc}

        Make the story engaging with:
        - Well-developed characters
        - A clear beginning, middle, and end
        - Vivid descriptions
        - Compelling dialogue where appropriate
        - A satisfying conclusion

        Story prompt: {prompt}
        """
        return enhanced_prompt

    def get_available_models(self, api_key):
        """Get list of available models to find the correct one"""
        try:
            if api_key:
                genai.configure(api_key=api_key)
            
            models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append(model.name)
            return models
        except Exception as e:
            st.error(f"Error listing models: {str(e)}")
            return []

    def generate_story(self, prompt, genre, tone, length, api_key):
        """Generate a story using Gemini API"""
        try:
        
            if api_key:
                genai.configure(api_key=api_key)

            
            enhanced_prompt = self.enhance_prompt(prompt, genre, tone)

           
            word_target = self.lengths[length]["words"]

            
            gemini_prompt = f"""
            {enhanced_prompt}
            Please write a complete story of about {word_target} words.
            """
            
           
            model_names = [
                "gemini-1.5-flash",
                "gemini-1.5-pro", 
                "gemini-pro",
                "models/gemini-1.5-flash",
                "models/gemini-1.5-pro",
                "models/gemini-pro"
            ]
            
           
            available_models = self.get_available_models(api_key)
            
            
            model_to_use = None
            for model_name in model_names:
                if model_name in available_models:
                    model_to_use = model_name
                    break
            
           
            if not model_to_use and available_models:
                model_to_use = available_models[0]
            
            if not model_to_use:
                return None, "No suitable Gemini model found. Please check your API key."
            
            
            model = genai.GenerativeModel(model_to_use)
            response = model.generate_content(gemini_prompt)
            story = response.text.strip()
            return story, None
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg:
                return None, f"Model not found. Available models: {', '.join(self.get_available_models(api_key))}"
            return None, error_msg

    def count_words(self, text):
        """Count words in the generated story"""
        return len(re.findall(r'\w+', text))

    def format_story_for_download(self, story, prompt, genre, tone, length):
        """Format story for download with metadata"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        formatted_story = f"""
AI GENERATED STORY
==================

Generated on: {timestamp}
Original Prompt: {prompt}
Genre: {genre}
Tone: {tone}
Length: {length}

STORY:
------

{story}

==================
Generated by AI Story Generator
"""
        return formatted_story


def main():
    
    st.markdown('<h1 class="main-header">📚 AI Story Generator</h1>', unsafe_allow_html=True)
    st.markdown("Transform your ideas into captivating stories with the power of AI!")

    
    generator = StoryGenerator()

    
    st.sidebar.header("🎛️ Story Parameters")

  
    env_api_key = os.getenv("GEMINI_API_KEY", "")

    
    api_key = env_api_key

    if not api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar to generate stories.")
        st.info("Don't have an API key? Get one at https://ai.google.dev/")
    else:
        
        with st.sidebar.expander("🔧 Debug Info"):
            if st.button("Show Available Models"):
                available_models = generator.get_available_models(api_key)
                if available_models:
                    st.success(f"Available models: {', '.join(available_models)}")
                else:
                    st.error("No models found or API key invalid")

    
    genre = st.sidebar.selectbox("📖 Genre", list(generator.genres.keys()))
    tone = st.sidebar.selectbox("🎭 Tone", list(generator.tones.keys()))
    length = st.sidebar.selectbox("📏 Length", list(generator.lengths.keys()))

    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Parameter Info:**")
    st.sidebar.markdown(f"**Genre:** {generator.genres[genre]}")
    st.sidebar.markdown(f"**Tone:** {generator.tones[tone]}")
    st.sidebar.markdown(f"**Length:** {generator.lengths[length]['description']}")

   
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("✍️ Enter Your Story Prompt")
        prompt = st.text_area(
            "What story would you like me to write?",
            placeholder="Example: A robot discovers emotions and falls in love with a human...",
            height=100
        )

        
        st.markdown("**💡 Need inspiration? Try these prompts:**")
        example_prompts = [
            "A time traveler visits ancient Egypt",
            "A detective solves crimes using cooking skills",
            "The last person on Earth receives a phone call",
            "A dragon opens a coffee shop in modern times",
            "Two rival magicians must work together to save the world"
        ]

        cols = st.columns(len(example_prompts))
        for i, example in enumerate(example_prompts):
            with cols[i % len(cols)]:
                if st.button(f"💡", key=f"example_{i}", help=example):
                    st.session_state.example_prompt = example

       
        if 'example_prompt' in st.session_state:
            prompt = st.session_state.example_prompt
            del st.session_state.example_prompt

    with col2:
        st.header("🎯 Quick Stats")
        if prompt:
            prompt_words = len(re.findall(r'\w+', prompt))
            st.metric("Prompt Words", prompt_words)
        st.metric("Target Words", generator.lengths[length]["words"])
        st.metric("Selected Genre", genre)
        st.metric("Selected Tone", tone)

   
    if st.button("🚀 Generate Story", type="primary", disabled=not (api_key and prompt)):
        if not prompt.strip():
            st.error("Please enter a story prompt!")
            return

        with st.spinner(f"🎭 Crafting your {genre.lower()} story... This may take a moment."):
            
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)  
                progress_bar.progress(i + 1)

            story, error = generator.generate_story(prompt, genre, tone, length, api_key)
            progress_bar.empty()

        if error:
            st.error(f"❌ Error generating story: {error}")
            st.info("Please check your API key and try again.")
        elif story:
            
            st.success("✨ Story generated successfully!")

            
            word_count = generator.count_words(story)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Word Count", word_count)
            with col2:
                st.metric("🎯 Target", generator.lengths[length]["words"])
            with col3:
                accuracy = min(100, int((word_count / generator.lengths[length]["words"]) * 100))
                st.metric("🎯 Length Accuracy", f"{accuracy}%")

            
            st.markdown("---")
            st.markdown("## 📖 Your Generated Story")
            st.markdown(f'<div class="story-container">{story}</div>', unsafe_allow_html=True)

            
            formatted_story = generator.format_story_for_download(story, prompt, genre, tone, length)
            st.download_button(
                label="📥 Download Story",
                data=formatted_story,
                file_name=f"ai_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

           
            st.markdown("---")
            st.markdown("### 💬 How was your story?")
            feedback_col1, feedback_col2 = st.columns(2)
            with feedback_col1:
                if st.button("👍 Great story!"):
                    st.success("Thank you for your feedback!")
            with feedback_col2:
                if st.button("👎 Could be better"):
                    st.info("Thanks for the feedback! Try adjusting the parameters and generating again.")

   
    st.markdown("---")
    st.markdown("### 📚 Sample Stories Gallery")

    sample_stories = {
        "Fantasy Adventure": {
            "prompt": "A young wizard discovers a spell that can rewrite history",
            "preview": "Elena's fingers trembled as she traced the ancient runes in the forbidden tome. The Chronos Spell – a magic so powerful it had been erased from every other text in the academy's vast library..."
        },
        "Sci-Fi Mystery": {
            "prompt": "A space detective investigates a murder on a generation ship",
            "preview": "Detective Yara Chen floated through the maintenance tunnel, her magnetic boots clicking against the metal grating. In forty years of interstellar travel, the UES Harmony had never seen a murder – until now..."
        },
        "Romance Comedy": {
            "prompt": "Two food critics who hate each other get stuck in an elevator",
            "preview": "The elevator shuddered to a halt between floors 12 and 13, and Marcus realized his worst nightmare had come true: he was trapped with Sophia Martinez, the food critic who'd destroyed his restaurant's reputation..."
        }
    }

    for title, content in sample_stories.items():
        with st.expander(f"📖 {title}"):
            st.markdown(f"**Prompt:** {content['prompt']}")
            st.markdown(f"**Preview:** {content['preview']}")


if __name__ == "__main__":
    main()