import os
from jinja2 import Environment, FileSystemLoader

# Setup Jinja2 environment pointing to the prompts directory
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
env = Environment(loader=FileSystemLoader(PROMPTS_DIR), autoescape=False)

def render_prompt(template_name: str, **kwargs) -> str:
    """
    Load a Markdown prompt template and render it with provided variables.
    
    Args:
        template_name: Name of the file (e.g., 'trend_detector.md')
        **kwargs: Variables to inject into the template
        
    Returns:
        The fully rendered prompt string.
    """
    template = env.get_template(template_name)
    return template.render(**kwargs)
