import os
from pathlib import Path
import configparser
from datetime import datetime

from prompt_toolkit.shortcuts import checkboxlist_dialog, message_dialog, input_dialog
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import radiolist_dialog
import typer
from rich import print

from lib.ai_web_researcher.gpt_online_researcher import gpt_web_researcher
from lib.ai_web_researcher.metaphor_basic_neural_web_search import metaphor_find_similar
from lib.ai_writers.keywords_to_blog import write_blog_from_keywords
from lib.ai_writers.speech_to_blog.main_audio_to_blog import generate_audio_blog
from lib.ai_writers.long_form_ai_writer import long_form_generator
from lib.ai_writers.ai_news_article_writer import ai_news_generation
from lib.gpt_providers.text_generation.ai_story_writer import ai_story_generator
from lib.gpt_providers.text_generation.ai_essay_writer import ai_essay_generator
from lib.gpt_providers.text_to_image_generation.main_generate_image_from_prompt import generate_image


def blog_from_audio():
    """
    Prompt the user to input either a YouTube URL, a file location, or keywords to search on YouTube.
    Validate the input and take appropriate actions based on the input type.
    """

    while True:
        audio_input = prompt("""Enter Youtube video URL OR provide Full-Path to audio file.\n👋 : """)
        # If the user cancels, exit the loop and the application
        if audio_input is None:
            break

        # If the user presses OK without providing any input, prompt again
        if not audio_input.strip():
            continue

        # Check if the input is a valid YouTube URL
        if audio_input.startswith("https://www.youtube.com/") or audio_input.startswith("http://www.youtube.com/") or os.path.exists(audio_input):
            # Validate YouTube URL, Process YouTube URL
            generate_audio_blog(audio_input)
            break


def blog_from_keyword():
    """ Input blog keywords, research and write a factual blog."""
    while True:
            print("________________________________________________________________")
            blog_keywords = input_dialog(
                    title='Enter Keywords/Blog Title',
                    text='Shit in, Shit Out; Better keywords, better research, hence better content.\n👋 Enter keywords/Blog Title for blog generation:',
                ).run()

            # If the user cancels, exit the loop
            if blog_keywords is None:
                break
            if blog_keywords and len(blog_keywords.split()) >= 2:
                break
            else:
                message_dialog(
                    title='Error',
                    text='🚫 Blog keywords should be at least two words long. Please try again.'
                ).run()
    choice = radiolist_dialog(
        title="Select content type:",
        values=[
            ("normal", "Normal-length content"),
            ("long", "Long-form content")
        ],
        default="normal"
    ).run()

    if choice == "normal":
        try:
            write_blog_from_keywords(blog_keywords)
        except Exception as err:
            print(f"Failed to write blog on {blog_keywords}, Error: {err}\n")
            exit(1)
    elif choice == "long":
        try:
            long_form_generator(blog_keywords)
        except Exception as err:
            print(f"Failed to write blog on {blog_keywords}, Error: {err}\n")
            exit(1)


def ai_news_writer():
    """ """
    while True:
        print("________________________________________________________________")
        news_keywords = input_dialog(
                title='Enter Keywords from News headlines:',
                text='Describe the News article in 3-5 words.\n👋 Enter main keywords describing the News Event: ',
            ).run()

        # If the user cancels, exit the loop
        if news_keywords is None:
            break
        if news_keywords and len(news_keywords.split()) >= 2:
            break
        else:
            message_dialog(
                title='Error',
                text='🚫 News keywords should be at least two words long. Least, you can do..'
            ).run()
    news_country = radiolist_dialog(
        title="Select origin country of the News event:",
        values=[
            ("es", "Spain"),
            ("vn", "Vietnam"),
            ("pk", "Pakistan"),
            ("in", "India"),
            ("de", "Germany"),
            ("cn", "China")
        ],
        default="in"
    ).run()
    news_language = radiolist_dialog(
        title="Select news article language to search for:",
        values=[
            ("en", "English"),
            ("es", "Spanish"),
            ("vi", "Vietnamese"),
            ("ar", "Arabic"),
            ("hi", "Hindi"),
            ("de", "German"),
            ("zh-cn", "Chinese")
        ],
        default="en"
    ).run()
    try:
        ai_news_generation(news_keywords, news_country, news_language)
    except Exception as err:
        raise err


def do_web_research():
    """ Input keywords and do web research and present a report."""
    if check_search_apis():
        while True:
            print("________________________________________________________________")
            search_keywords = input_dialog(
                    title='Enter Search Keywords below: More Options in main_config.',
                    text='👋 Enter keywords for web research (Or keywords from your blog):',
                ).run()
            if search_keywords and len(search_keywords.split()) >= 2:
                break
            else:
                message_dialog(
                    title='Warning',
                    text='🚫 Search keywords should be at least three words long. Please try again.'
                ).run()

    try:
        print(f"🚀🎬🚀 [bold green]Starting web research on given keywords: {search_keywords}..")
        web_research_result = gpt_web_researcher(search_keywords)
    except Exception as err:
        print(f"\n💥🤯 [bold red]ERROR 🤯 : Failed to do web research: {err}\n")

def write_story():
    """ Alwrity AI Story Writer """
    personas = [
        ("Award-Winning Science Fiction Author", "Award-Winning Science Fiction Author"),
        ("Historical Fiction Author", "Historical Fiction Author"),
        ("Fantasy World Builder", "Fantasy World Builder"),
        ("Mystery Novelist", "Mystery Novelist"),
        ("Romantic Poet", "Romantic Poet"),
        ("Thriller Writer", "Thriller Writer"),
        ("Children's Book Author", "Children's Book Autho"),
        ("Satirical Humorist", "Satirical Humorist"),
        ("Biographical Writer", "Biographical Writer"),
        ("Dystopian Visionary", "Dystopian Visionary"),
        ("Magical Realism Author", "Magical Realism Author")
    ]

    dialog = radiolist_dialog(
        title="Select Your Story Writing Persona Or Book Genre",
        text="Choose a persona that resonates you want AI Story Writer to adopt.",
        values=personas
    )

    selected_persona_name = dialog.run()
    # Define persona descriptions
    persona_descriptions = {
        "Award-Winning Science Fiction Author": "You are an award-winning science fiction author with a penchant for expansive, intricately woven stories. Your ultimate goal is to write the next award-winning sci-fi novel.",
        "Historical Fiction Author": "You are a seasoned historical fiction author, meticulously researching past eras to weave captivating narratives. Your goal is to transport readers to different times and places through your vivid storytelling.",
        "Fantasy World Builder": "You are a world-building enthusiast, crafting intricate realms filled with magic, mythical creatures, and epic quests. Your ambition is to create the next immersive fantasy saga that captivates readers' imaginations.",
        "Mystery Novelist": "You are a master of suspense and intrigue, intricately plotting out mysteries with unexpected twists and turns. Your aim is to keep readers on the edge of their seats, eagerly turning pages to unravel the truth.",
        "Romantic Poet": "You are a romantic at heart, composing verses that capture the essence of love, longing, and human connections. Your dream is to write the next timeless love story that leaves readers swooning.",
        "Thriller Writer": "You are a thrill-seeker, crafting adrenaline-pumping tales of danger, suspense, and high-stakes action. Your mission is to keep readers hooked from start to finish with heart-pounding thrills and unexpected twists.",
        "Children's Book Author": "You are a storyteller for the young and young at heart, creating whimsical worlds and lovable characters that inspire imagination and wonder. Your goal is to spark joy and curiosity in young readers with enchanting tales.",
        "Satirical Humorist": "You are a keen observer of society, using humor and wit to satirize the absurdities of everyday life. Your aim is to entertain and provoke thought, delivering biting social commentary through clever and humorous storytelling.",
        "Biographical Writer": "You are a chronicler of lives, delving into the stories of real people and events to illuminate the human experience. Your passion is to bring history to life through richly detailed biographies that resonate with readers.",
        "Dystopian Visionary": "You are a visionary writer, exploring dark and dystopian futures that reflect contemporary fears and anxieties. Your vision is to challenge societal norms and provoke reflection on the path humanity is heading.",
        "Magical Realism Author": "You are a purveyor of magical realism, blending the ordinary with the extraordinary to create enchanting and thought-provoking tales. Your goal is to blur the lines between reality and fantasy, leaving readers enchanted and introspective."
    }
    if selected_persona_name:
        selected_persona = next((persona for persona in personas if persona[0] == selected_persona_name), None)
        if selected_persona:
            character_input = input_dialog(
                title=f"Enter characters for {selected_persona[0]}",
                text=persona_descriptions[selected_persona_name]
            ).run()

    #FIXME/TBD: Presently supports gemini only. Openai, minstral coming up.
    # Check if LLM API KEYS are present and Not none.
    if os.getenv('GEMINI_API_KEY'):
        ai_story_generator(selected_persona_name, selected_persona_name, character_input)
    else:
        print(f"ERROR: Provide Google Gemini API keys. Openai, mistral, ollama coming up.")
        exit(1)



def essay_writer():
    # Define essay types and education levels
    essay_types = [
        ("Argumentative", "Argumentative - Forming an opinion via research. Building an evidence-based argument."),
        ("Expository", "Expository - Knowledge of a topic. Communicating information clearly."),
        ("Narrative", "Narrative - Creative language use. Presenting a compelling narrative."),
        ("Descriptive", "Descriptive - Creative language use. Describing sensory details.")
    ]

    education_levels = [
        ("Primary School", "Primary School"),
        ("High School", "High School"),
        ("College", "College"),
        ("Graduate School", "Graduate School")
    ]

    # Define the options for number of pages
    num_pages_options = [
        ("Short Form (1-2 pages)", "Short Form"),
        ("Medium Form (3-5 pages)", "Medium Form"),
        ("Long Form (6+ pages)", "Long Form")
    ]

    # Ask the user for the title of the essay
    essay_title = input_dialog(title="Essay Title", text="Enter the title of your essay:").run()
    while not essay_title.strip():
        print("Please enter a valid title for your essay.")
        essay_title = input_dialog(title="Essay Title", text="Enter the title of your essay:").run()

    # Ask the user for type of essay, level of education, and number of pages
    selected_essay_type = radiolist_dialog(title="Type of Essay", text="Choose the type of essay you want to write:",
                                           values=essay_types).run()

    selected_education_level = radiolist_dialog(title="Level of Education", text="Choose your level of education:",
                                               values=education_levels).run()

    # Prompt the user to select the length of the essay
    num_pages_prompt = "Select the length of your essay:"
    selected_num_pages = radiolist_dialog(title="Number of Pages", text=num_pages_prompt, values=num_pages_options).run()

    ai_essay_generator(essay_title, selected_essay_type, selected_education_level, selected_num_pages)



def blog_tools():
    os.system("clear" if os.name == "posix" else "cls")
    text = "_______________________________________________________________________\n"
    text += "\n⚠️    Alert!   💥❓💥\n"
    text += "Collection of Helpful Blogging Tools, powered by LLMs.\n"
    text += "_______________________________________________________________________\n"
    print(text)

    personas = [
        ("Get Content Outline", "Get Content Outline"),
        ("Write Blog Title", "Write Blog Title"),
        ("Write Blog Meta Description", "Write Blog Meta Description"),
#        ("Write Blog Introduction", "Write Blog Introduction"),
#        ("Write Blog conclusion", "Write Blog conclusion"),
#        ("Write Blog Outline", "Write Blog Outline"),
        ("Generate Blog FAQs", "Generate Blog FAQs"),
        ("AI Linkedin Post", "AI Linkedin Post"),
        ("YouTube To Blog", "YouTube To Blog"),
        ("AI Essay Writer", "AI Essay Writer"),
        ("AI Story Writer", "AI Story Writer"),
#        ("Research blog references", "Research blog references"),
#        ("Convert Blog To HTML", "Convert Blog To HTML"),
#        ("Convert Blog To Markdown", "Convert Blog To Markdown"),
#        ("Blog Proof Reader", "Blog Proof Reader"),
#        ("Get Blog Tags", "Get Blog Tags"),
#        ("Get blog categories", "Get blog categories"),
#        ("Get Blog Code Examples", "Get Blog Code Examples"),
#        ("Check WebPage Performance", "Check WebPage Performance"),
        ("Quit/Exit", "Quit/Exit")
    ]
    dialog = radiolist_dialog(
        title = "Select Your AI content tool.",
        text = "Choose a tool to use and visit provided online link to try them out.",
        values = personas
    )

    selected_persona_name = dialog.run()

    persona_descriptions = {
        "Get Content Outline": "Get Content Outline - VISIT: https://alwrity-outline.streamlit.app/",
        "Write Blog Title": "Write Blog Title - VISIT: https://alwrity-title.streamlit.app/",
        "Write Blog Meta Description": "Write Blog Meta Description - VISIT: https://alwrity-metadesc.streamlit.app/",
#        "Write Blog Introduction": "Write Blog Introduction - To Be Done (TBD)",
#        "Write Blog conclusion": "Write Blog conclusion - ",
#        "Write Blog Outline": "Write Blog Outline - ",
        "Generate Blog FAQs": "Generate Blog FAQs - VISIT: https://alwrity-faq.streamlit.app/",
        "AI Linkedin Post": "AI Linkedin Post writer - VISIT: https://alwrity-linkedin.streamlit.app/",
        "YouTube To Blog": "YouTube To Blog - VISIT: https://alwrity-yt-blog.streamlit.app/",
        "AI Essay Writer": "AI Essay Writer - VISIT: https://alwrity-essay.streamlit.app/",
        "AI Story Writer": "AI Story Writer - VISIT: https://alwrity-story.streamlit.app/",
#        "Research blog references": "Research blog references - Example: https://example.com/research-blog-references",
#        "Convert Blog To HTML": "Convert Blog To HTML - Example: https://example.com/convert-blog-to-html",
#        "Convert Blog To Markdown": "Convert Blog To Markdown - Example: https://example.com/convert-blog-to-markdown",
#        "Blog Proof Reader": "Blog Proof Reader - Example: https://example.com/blog-proof-reader",
#        "Get Blog Tags": "Get Blog Tags - Example: https://example.com/get-blog-tags",
#        "Get blog categories": "Get blog categories - Example: https://example.com/get-blog-categories",
#        "Get Blog Code Examples": "Get Blog Code Examples - Example: https://example.com/get-blog-code-examples",
#        "SEO Checks": "SEO checks - TBD",
        "Quit/Exit": "Quit/Exit - Example: Quit/Exit"
    }

    if selected_persona_name:
        selected_persona = next((persona for persona in personas if persona[0] == selected_persona_name), None)
        if selected_persona:
            character_input = message_dialog(
                    title=f"To Try {selected_persona_name}, Visit below URL:",
                    text=persona_descriptions[selected_persona_name]
            ).run()


def image_generator():
    """ Generate image from given text """
    print("Enter your long string below---")
    img_prompt = prompt("Enter text to create image from:: ")

    img_models = WordCompleter(['Stability-Stable-Diffusion', 'Dalle2', 'Dalle3'], ignore_case=True)
    print("Choose between:: Stable-Diffusion, Dalle2, Dalle3")
    img_model = prompt('Choose the image model to use for generation: ', completer=img_models, validator=ModelTypeValidator())

    if 'Stability-Stable-Diffusion' in img_model:
        api_key = 'STABILITY_API_KEY'
    elif 'Dalle3' in img_model:
        api_key = 'OPENAI_API_KEY'

    if os.getenv(api_key) is None:
        print(f"\n\n[bold green] 🙋 Get {api_key} Here:https://platform.stability.ai/docs/getting-started 🙋 -- \n")
        user_input = typer.prompt(f"💩 -**Please Enter(copy/paste) {api_key} Key** - Here🙋:")
        os.environ[api_key] = user_input
        try:
            with open(".env", "a") as env_file:
                env_file.write(f"{api_key}={user_input}\n")
                print(f"✅ API Key added to .env file.")
        except Exception as err:
            print(f"Error: {err}")
    try:
        generate_image(img_prompt, img_model)
    except Exception as err:
        print(f"Failed to generate image: {err}")



class ModelTypeValidator(Validator):
    def validate(self, document):
        if document.text.lower() not in ['stability-stable-diffusion', 'dalle2', 'dalle3']:
            raise ValidationError(message='Please choose a valid Text to image model.')


def image_to_text_writer():
    """ IMage to Text Content Generation"""
    os.system("clear" if os.name == "posix" else "cls")
    text = "_______________________________________________________________________\n"
    text += "\n⚠️    Alert!   💥❓💥\n"
    text += "Provide Inputs Below to Continue..\n"
    text += "_______________________________________________________________________\n\n"
    print(text)

    print("Make sure the file path is correct and the file is one of the following image types: PNG, JPEG, WEBP, HEIC, HEIF.\n")
    
    file_location = prompt('⚠️  Enter the image file location: ', validator=FileTypeValidator())
    if file_location:
        writing_completer = WordCompleter(['Blog', 'Food Recipe', 'Alt Text', 'Marketing Copy'], ignore_case=True)
        print("Choose between 'Blog', 'Food Recipe', 'Alt Text', 'Marketing Copy'")
        writing_type = prompt('Select the type of writing: ', completer=writing_completer, validator=WritingTypeValidator())
    
    prompt_gemini = None
    if writing_type.lower() == 'blog':
        prompt_gemini = "Given an image of a product and its target audience, write an engaging marketing description",
    elif writing_type.lower() == 'food recipe':
        prompt_gemini = """I have the ingredients above. Not sure what to cook for lunch.
        Show me a list of foods with the recipes.
        Accurately identify the baked good in the image and provide an appropriate and recipe consistent with your analysis.
        Write a short, engaging blog post based on this picture.
        It should include a description of the meal in the photo and talk about my journey meal prepping.
        """
    elif writing_type.lower() == 'alt text':
        prompt_gemini = """Given an image from my blog, generate 3 different ALT texts.
        The image alt text should be of maximum 2 lines. It should be descriptive and SEO optimised."""
    elif writing_type.lower() == 'marketing copy':
        prompt_gemini = "Given an image of a product and its target audience, write an engaging marketing description"

    print("TBD/FIXME: Will be taken up soon..")


class WritingTypeValidator(Validator):
    def validate(self, document):
        writing_type = document.text.strip().lower()
        if writing_type not in ['blog', 'food recipe', 'alt text', 'marketing copy']:
            raise ValidationError(message="Please select a valid writing type: Blog, Food Recipe, Alt Text, or Marketing Copy.")


class FileTypeValidator(Validator):
    def validate(self, document):
        file_path = document.text.strip()
        if not os.path.exists(file_path):
            raise ValidationError(message="File does not exist.")
        elif not self.is_valid_file_type(file_path):
            raise ValidationError(message="Unsupported file type or MIME type. Please select an image file.")
    
    def is_valid_file_type(self, file_path):
        # Define supported MIME types for image files
        supported_types = ['image/png', 'image/jpeg', 'image/webp', 'image/heic', 'image/heif']
        file_mime_type = self.get_file_mime_type(file_path)
        return file_mime_type in supported_types
    
    def get_file_mime_type(self, file_path):
        # Placeholder function to get the MIME type of the file
        # You can use libraries like magic or mimetypes for this purpose
        # Example:
        # import magic
        # mime = magic.Magic(mime=True)
        # return mime.from_file(file_path)
        return 'image/png'  # Placeholder value for demonstration


def competitor_analysis():
    text = "_______________________________________________________________________\n"
    text += "\n⚠️    Alert!   💥❓💥\n"
    text += "Provide competitor's URL, get details of similar/alternative companies.\n"
    text += "Usecases: Know similar companies and alternatives, to given URL\n"
    text += "Usecases: Write about similar companies, tools, alternative-to, similar products, similar websites etc\n"
    text += "Read More Here: https://docs.exa.ai/reference/company-analyst \n"
    text += "_______________________________________________________________________\n"
    print(text)
    similar_url = prompt("⚠️ 👋  Enter a single Valid URL for web analysis:: ")
    try:
        metaphor_find_similar(similar_url)
    except Exception as err:
        print(f"[bold red]✖ 🚫 Failed to do similar search.\nError:{err}[/bold red]")
    return

