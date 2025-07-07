from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import requests
import streamlit as st
from dotenv import load_dotenv
import streamlit.components.v1 as components
import os
from langchain_ollama import OllamaLLM
import streamlit.components.v1 as components
from io import BytesIO
import zipfile
import openai
import fastapi


load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
PEXEL_KEY=os.getenv("PEXELS_API_KEY")


st.title("🧠 AI Website Builder")
st.markdown("Describe the type of website you'd like to create:")

prompt = st.text_input("🔤 Your Prompt")

def fetch_pexels_video(query):
    headers = {
        "Authorization": PEXEL_KEY
    }
    params = {
        "query": query,
        "per_page": 1
    }
    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["videos"]:
            video_files=data["videos"][0]["video_files"]
            hd_video = next((f for f in video_files if f["quality"] == "hd"), None)#generator ki statement nyi aise hi likhte h f for f in files 
            #next(iterator,default)<- syntax

            if hd_video:
             return hd_video["link"]
            else:
             return video_files[0]["link"]
        
        else:
            st.warning("No video found for the given query.")
            return ""
    else:
        st.error("⚠️ Failed to fetch video from Pexels.")
        return ""
# Initialize Groq LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

# HTML generation function
def generate_html(user_prompt, video_url):
    template = """
You are a professional frontend website developer and UI/UX designer.

Create a visually appealing, modern, and responsive landing page using HTML and Tailwind CSS based on this description: "{user_prompt}"

Requirements:
- Use the video URL: {video_url} as the hero background or key visual.
-Use High Quality Background Videos
- Design with an elegant color scheme, smooth spacing, and clear visual hierarchy.
- Use modern fonts, gradient backgrounds, subtle shadows, and rounded corners.
- Include a sticky header with a logo and navigation.
- Add call-to-action buttons with hover effects.
- Ensure it is 100% responsive across laptops, tablets, and mobile phones.
- Avoid JavaScript and backend logic.
- Add a zoom-in animation to the heading using @keyframes called 'zoomIn' and Tailwind-compatible class 'animate-zoom-in'.
- Define it in a <style> tag and apply it to the hero section headline.
- Only return a single HTML file with Tailwind CSS.

"""


    prompt_template = PromptTemplate(template=template, input_variables=["user_prompt", "video_url"])
    chain = prompt_template | llm

    result = chain.invoke({
        "user_prompt": user_prompt,
        "video_url": video_url
    })
    return result.content if hasattr(result, 'content') else result  # in case result is a string

# Main action
if st.button("🚀 Generate Website"):
    if not prompt.strip():
        st.warning("⚠️ Please enter a prompt.")
    else:
        with st.spinner("Generating your AI-powered website..."):
            video_url = fetch_pexels_video(prompt)
            if video_url:
                html_code = generate_html(prompt,video_url)

                st.subheader("🔍 Live Preview:")
                components.html(html_code, height=1200, scrolling=True)
        

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("index.html", html_code)
        st.download_button("📥 Download Website", zip_buffer.getvalue(), file_name="website.zip")

        with st.expander("🧾 View HTML Code"):
            st.code(html_code, language="html")