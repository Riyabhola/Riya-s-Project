import streamlit.components.v1 as components
import json

def puter_chat_component(prompt, key=None):
    """
    A 'professional' Puter.js wrapper for Streamlit.
    Bypasses API keys by using Puter's browser-based anonymous guest flow.
    """
    # JS code to load puter.js and make the call
    html_code = f"""
    <script src="https://js.puter.com/v2/"></script>
    <script>
        (async function() {{
            try {{
                // Puter.js handles the 'Continue as Guest' flow in the browser
                const result = await puter.ai.chat({json.dumps(prompt)}, {{ model: 'gpt-4o' }});
                const content = result.message.content;
                
                // Send the result back to Streamlit
                // This is a standard way for custom components to communicate
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: content,
                    key: '{key}'
                }}, '*');
            }} catch (error) {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: "ERROR: " + error.message,
                    key: '{key}'
                }}, '*');
            }}
        }})();
    </script>
    <div style="display:none;">Puter AI Worker</div>
    """
    
    # This renders the component and listens for the 'setComponentValue' message
    return components.html(html_code, height=0, key=f"puter_worker_{key}")

def puter_ai_chat_seamless(prompt, context=""):
    """
    High-level function to be used in chatbot.py
    Note: This will only work if called within a Streamlit app context.
    """
    full_prompt = prompt
    if context:
        full_prompt = f"CONTEXT:\n{context}\n\nUSER QUERY: {prompt}"
    
    # Since this is a client-side component, we need to handle it in the Streamlit loop.
    # This function is a placeholder for the logic we'll add to app.py
    pass
