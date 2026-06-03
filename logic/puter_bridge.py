import os
import streamlit as st
import streamlit.components.v1 as components

# --- Professional Puter.js Bridge ---
def puter_ai_chat(prompt):
    """
    Seamlessly calls Puter.js in the browser. 
    Bypasses API keys by leveraging Puter's anonymous guest sessions.
    """
    component_key = f"puter_chat_{hash(prompt)}"
    
    html_code = f"""
    <script src="https://js.puter.com/v2/"></script>
    <script>
        (async function() {{
            try {{
                const result = await puter.ai.chat({repr(prompt)}, {{ model: 'gpt-4o' }});
                const response = result.message.content;
                
                // Streamlit component bridge
                const setStreamlitValue = (value) => {{
                    const event = new CustomEvent("streamlit:setComponentValue", {{
                        detail: value
                    }});
                    window.parent.dispatchEvent(event);
                }};
                
                // Sending back the result
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: response,
                    key: '{component_key}'
                }}, '*');
                
            }} catch (err) {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: "Error: " + err.message,
                    key: '{component_key}'
                }}, '*');
            }}
        }})();
    </script>
    <div style="font-size: 0.8em; color: #666;">AI Advisor is thinking...</div>
    """
    
    # Render the component
    res = components.html(html_code, height=30, key=component_key)
    return res

# --- Updated handle_query Fallback ---
# I will update chatbot.py to use this bridge when in UI mode.
