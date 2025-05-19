"""
Example script demonstrating component embedding
"""
import preswald as pw

# Create some components with unique IDs
pw.header("Embed Example", level=1, id="main_header")
pw.text("This is a sample application with multiple components.", id="intro_text")

# Create a component specifically for embedding
with pw.card(id="embeddable_card", title="Embeddable Component"):
    pw.text("This component can be embedded on its own.", id="card_text")
    pw.button("Click Me", id="embed_button")

# Create another component
pw.plotly({
    "data": [{"y": [1, 2, 3, 4], "type": "scatter"}],
    "layout": {"title": "Sample Plot"}
}, id="sample_plot")

# Add instructions for embedding
pw.markdown("""
## How to Embed

To embed the card component, use the following HTML code:

```html
<iframe 
    src="http://localhost:8000/embed?component_id=embeddable_card" 
    width="100%" 
    height="300" 
    frameborder="0">
</iframe>
```

This will only show the card component, not the rest of the application.
""", id="embed_instructions") 