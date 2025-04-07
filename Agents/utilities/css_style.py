
def get_css_styles(colorblind_mode=False):
    """Return CSS styles based on colorblind mode selection."""
    if colorblind_mode:
        # Colorblind-friendly pattern: High contrast, distinguishable colors
        return """
        <style>
            .chat-message {
                padding: 1rem; 
                border-radius: 0.5rem; 
                margin-bottom: 1rem; 
                display: flex;
                flex-direction: column;
            }
            .chat-message.user {
                background-color: #d4e6f1;  /* Light blue-gray */
                border-left: 5px solid #2c3e50;  /* Dark slate */
            }
            .chat-message.assistant {
                background-color: #ecf0f1;  /* Light gray */
                border-left: 5px solid #2c3e50;  /* Dark slate */
            }
            .chat-message .content {
                display: flex;
                margin-top: 0.5rem;
            }
            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                object-fit: cover;
                margin-right: 1rem;
            }
            .message {
                flex: 1;
                color: #1a2525;  /* Darker gray for better contrast */
            }
            .timestamp {
                font-size: 0.8rem;
                color: #7f8c8d;  /* Medium gray */
                margin-top: 0.2rem;
            }
            .markdown-content table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            .markdown-content th, .markdown-content td {
                border: 1px solid #bdc3c7;  /* Light gray border */
                padding: 8px;
                text-align: left;
            }
            .markdown-content th {
                background-color: #dfe6e9;  /* Light blue-gray */
            }
            .stMarkdown p {
                font-size: 14px;
                margin-bottom: 0.2rem;
                word-wrap: break-word;
            }
            .stTextInput > div > div > input {
                font-size: 14px;
            }
            [data-testid="stSidebar"] {
                width: 500px !important;
            }
            [data-testid="stAppViewContainer"] > .main {
                margin-left: 500px !important;
            }
        </style>
        """
    else:
        # Normal color pattern (original)
        return """
        <style>
            .chat-message {
                padding: 1rem; 
                border-radius: 0.5rem; 
                margin-bottom: 1rem; 
                display: flex;
                flex-direction: column;
            }
            .chat-message.user {
                background-color: #e6f7ff;
                border-left: 5px solid #0079AD;
            }
            .chat-message.assistant {
                background-color: #f0f0f0;
                border-left: 5px solid #0079AD;
            }
            .chat-message .content {
                display: flex;
                margin-top: 0.5rem;
            }
            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                object-fit: cover;
                margin-right: 1rem;
            }
            .message {
                flex: 1;
                color: #000000;
            }
            .timestamp {
                font-size: 0.8rem;
                color: #888;
                margin-top: 0.2rem;
            }
            .markdown-content table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            .markdown-content th, .markdown-content td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .markdown-content th {
                background-color: #f5f5f5;
            }
            .stMarkdown p {
                font-size: 14px;
                margin-bottom: 0.2rem;
                word-wrap: break-word;
            }
            .stTextInput > div > div > input {
                font-size: 14px;
            }
            [data-testid="stSidebar"] {
                width: 500px !important;
            }
            [data-testid="stAppViewContainer"] > .main {
                margin-left: 500px !important;
            }
        </style>
        """