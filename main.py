import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import io

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="User Guide Summarization",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'guide_context' not in st.session_state:
    st.session_state.guide_context = ""

def initialize_client():
    """Initialize Azure OpenAI client with error handling"""
    try:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if not api_key or not endpoint:
            st.error("⚠️ Azure OpenAI credentials not found. Please check your .env file.")
            st.info("Required environment variables: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT")
            return None
            
        client = AzureOpenAI(
            api_version="2024-07-01-preview",
            azure_endpoint=endpoint,
            api_key=api_key,
        )
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Azure OpenAI client: {str(e)}")
        return None

def summarize_user_guide(client, text, summary_style="concise", max_tokens=300, temperature=0.3, language="English", model="gpt-4o-mini"):
    """Generate user guide summary using Azure OpenAI"""
    try:
        if not text.strip():
            return "⚠️ No content to summarize. Please provide a user guide document."
        
        # Language-specific instructions
        language_instructions = {
            "English": "",
            "Spanish": "Respond in Spanish.",
            "French": "Respond in French.",
            "German": "Respond in German.",
            "Italian": "Respond in Italian.",
            "Portuguese": "Respond in Portuguese.",
            "Japanese": "Respond in Japanese.",
            "Chinese (Simplified)": "Respond in Simplified Chinese.",
            "Korean": "Respond in Korean.",
            "Arabic": "Respond in Arabic."
        }
        
        # Customize prompt based on style
        style_prompts = {
            "concise": "Summarize the following user guide documentation into concise bullet points covering key features, instructions, and important information:",
            "detailed": "Provide a detailed summary of the following user guide documentation, including all major sections, procedures, and important details:",
            "action-focused": "Extract and organize the key procedures, step-by-step instructions, and important guidelines from the following user guide documentation:"
        }
        
        base_prompt = style_prompts.get(summary_style, style_prompts['concise'])
        language_instruction = language_instructions.get(language, "")
        
        if language_instruction:
            prompt = f"{base_prompt} {language_instruction}\n\n{text}"
        else:
            prompt = f"{base_prompt}\n\n{text}"
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error generating summary: {str(e)}"

def answer_question(client, question, guide_summary, guide_document="", language="English", model="gpt-4o-mini"):
    """Answer questions about the user guide using the summary and document"""
    try:
        if not question.strip():
            return "⚠️ Please ask a question about the user guide."
        
        if not guide_summary.strip():
            return "⚠️ No guide summary available. Please generate a summary first."
        
        # Language-specific instructions
        language_instructions = {
            "English": "",
            "Spanish": " Please respond in Spanish.",
            "French": " Please respond in French.",
            "German": " Please respond in German.",
            "Italian": " Please respond in Italian.",
            "Portuguese": " Please respond in Portuguese.",
            "Japanese": " Please respond in Japanese.",
            "Chinese (Simplified)": " Please respond in Simplified Chinese.",
            "Korean": " Please respond in Korean.",
            "Arabic": " Please respond in Arabic."
        }
        
        language_instruction = language_instructions.get(language, "")

        # System prompt with CoT and structured JSON output
        system_prompt = f"""You are an expert assistant specialized in analyzing user guides and technical documentation.{language_instruction}

## Your Task:
Analyze the provided documentation and answer user questions using Chain of Thought reasoning, then return your response in structured JSON format.

## Response Format:
You MUST return your response as valid JSON with this structure:
{{
    "reasoning": "Your internal step-by-step thought process (not shown to user)",
    "answer": "The clear, helpful answer for the user",
    "confidence": 0.0 to 1.0,
    "sources": ["List of relevant sections or references from the guide"],
    "found_in_guide": true or false
}}

## Few-Shot Examples:

Example 1:
Q: How do I reset the application?
Response:
{{
    "reasoning": "Looking for reset instructions... Found in Settings section under Advanced Options",
    "answer": "To reset the application: Navigate to Settings > Advanced Options > Reset to Defaults. Click 'Confirm Reset' and restart the application.",
    "confidence": 0.95,
    "sources": ["Settings section", "Advanced Options"],
    "found_in_guide": true
}}

Example 2:
Q: What are the system requirements?
Response:
{{
    "reasoning": "Searching for technical specifications or requirements section in the documentation",
    "answer": "Minimum requirements: Windows 10+ or macOS 10.15+, 8GB RAM, 50GB storage, internet connection for updates.",
    "confidence": 1.0,
    "sources": ["System Requirements section"],
    "found_in_guide": true
}}

Example 3:
Q: Can I use custom themes?
Response:
{{
    "reasoning": "Searched for themes, customization, appearance settings - no relevant information found",
    "answer": "The documentation doesn't mention custom themes or appearance customization options.",
    "confidence": 0.8,
    "sources": [],
    "found_in_guide": false
}}

## Important Instructions:
- Always return valid JSON format
- Use the "reasoning" field for your Chain of Thought process
- Keep "answer" field user-friendly and direct
- Set confidence based on how certain you are
- List actual section names in "sources"
- Set "found_in_guide" to false if information is not available"""

        # Create context with document information
        context = f"User Guide Summary:\n{guide_summary}"
        if guide_document:
            context += f"\n\nOriginal Document:\n{guide_document[:2000]}..." if len(guide_document) > 2000 else f"\n\nOriginal Document:\n{guide_document}"
        
        # User prompt with context and question
        user_prompt = f"""Here is the documentation context:

{context}

User Question: {question}

Remember to return your response in the specified JSON format."""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,  # Increased for JSON structure
            temperature=0.1  # Lower temperature for more factual responses
        )
        
        # Parse JSON response and extract just the answer
        import json
        try:
            response_json = json.loads(response.choices[0].message.content)
            
            # Optionally log the reasoning for debugging (without showing to user)
            if response_json.get("reasoning"):
                print(f"🧠 CoT Reasoning: {response_json['reasoning']}")
            
            # Return just the clean answer for the user
            answer = response_json.get("answer", "Unable to generate response")
            
            # Optionally append confidence/source info if desired
            if response_json.get("confidence", 1.0) < 0.5:
                answer += "\n\n⚠️ Note: Low confidence in this answer."
            
            if not response_json.get("found_in_guide", True):
                answer += "\n\n📝 Note: This information was not found in the guide."
                
            return answer
            
        except json.JSONDecodeError:
            # Fallback to raw response if JSON parsing fails
            print("⚠️ JSON parsing failed, returning raw response")
            return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error answering question: {str(e)}"

def detect_question_language(client, question, model="gpt-4o-mini"):
    """Detect the language of the user's question using AI"""
    try:
        if not question.strip():
            return "English"  # Default fallback
        
        # Simple language detection prompt
        detection_prompt = f"""Identify the language of the following text and respond with ONLY the language name in English (e.g., "Spanish", "French", "German", etc.). If you're not sure or it's mixed languages, respond with "English".

Text: "{question}"

Language:"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": detection_prompt}],
            max_tokens=10,
            temperature=0.1
        )
        
        detected_language = response.choices[0].message.content.strip()
        
        # Validate detected language against supported languages
        supported_languages = [
            "English", "Spanish", "French", "German", "Italian", 
            "Portuguese", "Japanese", "Chinese", "Korean", "Arabic"
        ]
        
        # Handle variations and ensure we return a supported language
        language_mapping = {
            "chinese (simplified)": "Chinese (Simplified)",
            "chinese": "Chinese (Simplified)",
            "simplified chinese": "Chinese (Simplified)",
            "mandarin": "Chinese (Simplified)"
        }
        
        detected_lower = detected_language.lower()
        if detected_lower in language_mapping:
            return language_mapping[detected_lower]
        
        # Check if detected language is in supported list (case insensitive)
        for lang in supported_languages:
            if lang.lower() == detected_lower:
                return lang
        
        # If not found, default to English
        return "English"
        
    except Exception as e:
        print(f"Language detection error: {e}")
        return "English"  # Fallback to English on error

def answer_question_auto_lang(client, question, guide_summary, guide_document="", fallback_language="English", model="gpt-4o-mini"):
    """Answer questions with automatic language detection from the question"""
    try:
        if not question.strip():
            return "⚠️ Please ask a question about the user guide."
        
        if not guide_summary.strip():
            return "⚠️ No guide summary available. Please generate a summary first."
        
        # Detect the language of the question
        detected_language = detect_question_language(client, question, model)
        
        # Use the original answer_question function with detected language
        return answer_question(client, question, guide_summary, guide_document, detected_language, model)
        
    except Exception as e:
        return f"❌ Error answering question: {str(e)}"

def main():
    # Header
    st.title("🔍 User Guide Summarization")
    st.markdown("Transform your user guide documentation into organized, digestible summaries using AI")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Model selection
    model = st.sidebar.selectbox(
        "🤖 AI Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-35-turbo", "gpt-35-turbo-16k"],
        index=0,
        help="Choose the Azure OpenAI model for processing"
    )
    
    # Language selection
    language = st.sidebar.selectbox(
        "🌐 Output Language",
        ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Chinese (Simplified)", "Korean", "Arabic"],
        help="Choose the language for the summary and Q&A responses"
    )
    
    # Summary style options
    summary_style = st.sidebar.selectbox(
        "📝 Summary Style",
        ["concise", "detailed", "action-focused"],
        help="Choose the style of summary you want"
    )
    
    # Advanced settings
    with st.sidebar.expander("Advanced Settings"):
        max_tokens = st.slider("Max Output Length", 150, 1000, 300, 50)
        temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.3, 0.1)
        
        # Model information
        st.info(f"**Selected Model:** {model}")
        model_info = {
            "gpt-4o-mini": "Fast and cost-effective, great for most tasks",
            "gpt-4o": "Advanced reasoning and complex tasks",
            "gpt-4": "High-quality responses with deep understanding",
            "gpt-35-turbo": "Balanced performance and speed",
            "gpt-35-turbo-16k": "Extended context length support"
        }
        st.caption(model_info.get(model, "Azure OpenAI model"))
    
    # Initialize client
    client = initialize_client()
    
    if client is None:
        st.stop()
    
    # Main content area with tabs
    tab1, tab2 = st.tabs(["🔍 User Guide Summary", "💬 Q&A Chatbot"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📥 Input")
            
            # Input method selection
            input_method = st.radio(
                "Choose input method:",
                ["Upload file", "Paste text", "Load sample"]
            )
            
            transcript_text = ""
            
            if input_method == "Upload file":
                uploaded_file = st.file_uploader(
                    "Upload user guide document",
                    type=['txt', 'md'],
                    help="Upload a text file containing your user guide documentation",
                )
                
                if uploaded_file is not None:
                    transcript_text = str(uploaded_file.read(), "utf-8")
                    st.success(f"✅ File uploaded successfully! ({len(transcript_text)} characters)")
            
            elif input_method == "Paste text":
                transcript_text = st.text_area(
                    "Paste your user guide document here:",
                    height=300,
                    placeholder="Enter or paste your user guide documentation here..."
                )
            
            else:  # Load sample
                if st.button("📄 Load Sample User Guide"):
                    try:
                        with open("data/user_guide_sample.txt", "r") as f:
                            transcript_text = f.read()
                        st.success("✅ Sample user guide loaded!")
                    except FileNotFoundError:
                        st.error("❌ Sample file not found. Please create data/user_guide_sample.txt")
                        transcript_text = ""
            
            # Display input preview
            if transcript_text:
                with st.expander("📖 Preview Input"):
                    st.text_area("Document preview:", transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text, height=150, disabled=True)
        
        with col2:
            st.header("📤 Output")
            
            # Generate summary button
            if st.button("🎯 Generate Summary", type="primary", disabled=not transcript_text):
                if transcript_text.strip():
                    with st.spinner("🤖 Generating summary..."):
                        summary = summarize_user_guide(
                            client, 
                            transcript_text, 
                            summary_style, 
                            max_tokens, 
                            temperature,
                            language,
                            model
                        )
                        st.session_state.summary = summary
                        st.session_state.last_input = transcript_text
                        st.session_state.guide_context = transcript_text
                        # Clear chat history when new summary is generated
                        st.session_state.chat_history = []
                else:
                    st.warning("⚠️ Please provide a user guide document first.")
            
            # Display summary
            if st.session_state.summary:
                st.subheader("📋 User Guide Summary")
                
                # Summary output
                summary_container = st.container()
                with summary_container:
                    st.markdown(st.session_state.summary)
                
                # Action buttons
                col_download, col_copy = st.columns(2)
                
                with col_download:
                    # Download as text file
                    summary_bytes = st.session_state.summary.encode('utf-8')
                    st.download_button(
                        label="💾 Download Summary",
                        data=summary_bytes,
                        file_name="user_guide_summary.txt",
                        mime="text/plain"
                    )
                
                with col_copy:
                    # Copy to clipboard (placeholder - requires JavaScript)
                    if st.button("📋 Copy to Clipboard"):
                        st.info("💡 Use Ctrl+A, Ctrl+C to copy the summary above")
            
            # Display statistics
            if st.session_state.summary and st.session_state.last_input:
                st.subheader("📊 Statistics")
                input_words = len(st.session_state.last_input.split())
                output_words = len(st.session_state.summary.split())
                compression_ratio = round((1 - output_words/input_words) * 100, 1) if input_words > 0 else 0
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                col_stat1.metric("Input Words", input_words)
                col_stat2.metric("Output Words", output_words)
                col_stat3.metric("Compression", f"{compression_ratio}%")
    
    with tab2:
        st.header("🤖 User Guide Q&A Chatbot")
        
        # Check if there's a summary to chat about
        if not st.session_state.summary:
            st.info("� Please generate a user guide summary first to start chatting about it!")
            st.markdown("Go to the **User Guide Summary** tab to upload a document and generate a summary.")
        else:
            # Display user guide summary context
            with st.expander("📋 User Guide Context", expanded=False):
                st.markdown("**Current User Guide Summary:**")
                st.text_area("Summary", st.session_state.summary, height=100, disabled=True)
            
            # Chat interface
            st.markdown("**Ask questions about the user guide:**")
            st.info("💡 **Smart Language Detection**: Ask questions in any supported language, and I'll respond in the same language! The configured language above is used for summaries only.")
            
            # Display chat history
            if st.session_state.chat_history:
                st.markdown("### 💬 Conversation History")
                
                for i, (question, answer) in enumerate(st.session_state.chat_history):
                    # User question
                    st.markdown(f"**👤 You:** {question}")
                    # Bot answer
                    st.markdown(f"**🤖 Assistant:** {answer}")
                    st.markdown("---")
            
            # Question input
            col_input, col_ask = st.columns([4, 1])
            
            with col_input:
                question = st.text_input(
                    "Ask a question:",
                    placeholder="e.g., How do I configure this feature? | ¿Cómo configuro esta característica? | Comment configurer cette fonctionnalité?",
                    key="question_input"
                )
            
            with col_ask:
                st.markdown("<br>", unsafe_allow_html=True)  # Align button with input
                ask_button = st.button("🚀 Ask", type="primary")
            
            # Process question
            if ask_button and question:
                if client:
                    with st.spinner("🤔 Thinking..."):
                        # Use auto-detection for chatbot, but keep manual language for summaries
                        answer = answer_question_auto_lang(
                            client, 
                            question, 
                            st.session_state.summary, 
                            st.session_state.last_input,
                            language,  # fallback language
                            model
                        )
                        
                        # Add to chat history
                        st.session_state.chat_history.append((question, answer))
                        
                        # Clear input and rerun to show new message
                        st.rerun()
                else:
                    st.error("❌ Unable to process question. Please check your API configuration.")
            
            # Chat controls
            col_clear, col_export = st.columns(2)
            
            with col_clear:
                if st.button("🗑️ Clear Chat") and st.session_state.chat_history:
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col_export:
                if st.session_state.chat_history:
                    # Export chat history
                    chat_export = "User Guide Q&A Session\n" + "="*50 + "\n\n"
                    chat_export += f"User Guide Summary:\n{st.session_state.summary}\n\n"
                    chat_export += "Conversation:\n" + "-"*30 + "\n"
                    
                    for i, (q, a) in enumerate(st.session_state.chat_history, 1):
                        chat_export += f"Q{i}: {q}\n"
                        chat_export += f"A{i}: {a}\n\n"
                    
                    st.download_button(
                        label="💾 Export Chat",
                        data=chat_export.encode('utf-8'),
                        file_name="user_guide_qa_session.txt",
                        mime="text/plain"
                    )
            
            # Suggested questions
            if st.session_state.summary and not st.session_state.chat_history:
                st.markdown("### 💡 Suggested Questions (Multi-Language)")
                suggested_questions = [
                    "What are the main features described in this guide?",
                    "¿Cuáles son las características principales descritas en esta guía?",
                    "Quelles sont les procédures étape par étape?",
                    "Welche wichtigen Konfigurationsschritte gibt es?",
                    "このガイドの主要な機能は何ですか？"
                ]
                
                cols = st.columns(2)
                for i, suggestion in enumerate(suggested_questions):
                    with cols[i % 2]:
                        if st.button(f"💭 {suggestion}", key=f"suggestion_{i}"):
                            # Set the question and trigger ask
                            if client:
                                with st.spinner("🤔 Thinking..."):
                                    # Use auto-detection for suggested questions too
                                    answer = answer_question_auto_lang(
                                        client, 
                                        suggestion, 
                                        st.session_state.summary, 
                                        st.session_state.last_input,
                                        language,  # fallback language
                                        model
                                    )
                                    
                                    st.session_state.chat_history.append((suggestion, answer))
                                    st.rerun()

if __name__ == "__main__":
    main()