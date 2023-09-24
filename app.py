import time
import openai
import torch
import streamlit as st
from stqdm import stqdm
from diffusers import DiffusionPipeline

#Stable Diffusion XL setup
pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0",
                                         torch_dtype=torch.float16,
                                         use_safetensors=True,
                                         variant="fp16")
pipe.to("cuda")

st.set_page_config(
    page_title="ChemAI",
)

with st.sidebar:
  with st.form("API KEY"):
    openai_api_key = st.text_input("OpenAI API key", value="", type="password")
    st.caption("*If you don't have an OpenAI API key, get it [here](https://platform.openai.com/account/api-keys).*")
    submitted_key = st.form_submit_button('Submit')



if submitted_key:
  try:
      openai.api_key = openai_api_key
      response = openai.Completion.create(engine="davinci", prompt="test")
  except Exception as e:
      st.warning(f'Invalid OpenAI API key: {e}')


#%%
#GPT-3.5-Paramters
#(A) Element Generator
element_gen = """
Generate a short summary for any element. This AI will output The name of an element,
The chemical symbol of an element,The atomic number of an element,The electron configuration of an element
The properties of an element, such as its atomic mass, density, and melting and boiling points depends on the user request.
This chat able to create summary of any elements in periodic table.
"""

Element_user1 = """
Can you give me a summary of oxygen?
"""

Element_response1 = """
Oxygen is Earth's most abundant element, and after hydrogen and helium,
it is the third-most abundant element in the universe. At standard temperature and pressure,
two atoms of the element bind to form dioxygen, a colorless and odorless diatomic gas with the formula O. 2.
"""

element_user2 = """
Can you give me a summary of neon?
"""

element_response2 = """
Neon is a chemical element with the symbol Ne and atomic number 10. It is a noble gas. Neon is a colorless, odorless, inert monatomic gas under standard conditions, with about two-thirds the density of air.
It was discovered (along with krypton and xenon) in 1898 as one of the three residual rare inert elements remaining in dry air, after nitrogen, oxygen, argon and carbon dioxide were removed.
Neon was the second of these three rare gases to be discovered and was immediately recognized as a new element from its bright red emission spectrum.
The name neon is derived from the Greek word, νέον, neuter singular form of νέος (neos), meaning 'new'.
Neon is chemically inert, and no uncharged neon compounds are known. The compounds of neon currently known include ionic molecules, molecules held together by van der Waals forces and clathrates.
"""

element_user3 = """
Can you give me the boiling points of iron?
"""

element_response3 = """
Iron has a Boiling Point of 2861°C, meaning at 2861°C it will turn to a Gas.
"""

#(C) Image Description Generator
idg_system = """
On this section, the image of the element will be output.
"""
idg_input1 = """
give me a short clear image description about the game
"""

idg_response1 = """
Iron is a lustrous, ductile, malleable, silver-gray metal (group VIII of the periodic table).
It is known to exist in four distinct crystalline forms. Iron rusts in damp air, but not in dry air. It dissolves readily in dilute acids.
"""



  #%%

def element_ai(text_input):
    response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
        {
            "role":"system",
            "content": element_gen
        },

        {
            "role":"user",
            "content" : Element_user1
        },

        {
            "role":"assistant",
            "content": Element_response1
        },

        {
            "role":"user",
            "content" : element_user2
        },

        {
            "role":"assistant",
            "content": element_response2
        },

        {
            "role":"user",
            "content" : element_user3
        },

        {
            "role":"assistant",
            "content": element_response3
        },

        {
            "role":"user",
            "content" : text_input
        }
        ],
    max_tokens = 1000,
    temperature = 1
    )

    elementer = response['choices'][0]['message']['content']
    return elementer

def img_desc(elementer):

    response_img = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
        {
            "role":"system",
            "content": idg_system
        },

        {
            "role":"user",
            "content" : idg_input1
        },

        {
            "role":"assistant",
            "content": idg_response1
        },

        {
    "role":"user",
    "content" : f"""
    Generate a short clear image description in one sentence about how
    the element look likes: {elementer}.
    The output must be compact in on sentence only.
    """
    }
    ],
    max_tokens = 1000,
    temperature = 1
    )

    img_desc = response_img['choices'][0]['message']['content']
    return img_desc

def stable_diffusion_xl(img_desc):
    prompt = f"""
    Generate a visual image about the element:
    {img_desc}
                      """
    images = pipe(prompt=prompt).images[0]
    return images


#%%
# Setup Streamlit App
# Define custom styles for justified text
justified_text_style = '''
<style>
.justified-text {
    text-align: justify;
}
</style>
'''
st.markdown(justified_text_style, unsafe_allow_html=True)

page_bg_img = '''
<style>
body {
background-image: url("https://images.unsplash.com/photo-1693498068361-7f07114e33cc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=988&q=80");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

info = """
I am ChemAI who is your chemistry assistant which able to help with your homework and your questions specifically about periodic table.
Ask me anything about elements in the periodic table and I will summarize the elements and give the picture of it.
It also allows you to generate an image of the elements by using Stable Diffusion XL.
"""

st.markdown("<h1 style='text-align: center; color: white;'>ChemAI</h1>", unsafe_allow_html=True)
col1, col2 = st.columns([5,5])

col1.markdown(f'<div class="justified-text">{info}</div>', unsafe_allow_html=True)

form = col2.form

with form('input_form'):
      text_input = st.text_area("Input your question here")

      submitted = st.form_submit_button('Submit')

      text_inputs = [text_input]

if submitted:


    for i in stqdm(range(100), backend=True, frontend=True):
      time.sleep(0.5)

    element = element_ai(text_input)
    st.markdown('**_Output:_** ')
    st.write(element)

    image_desc = img_desc(element)
    st.markdown('**_The Image Description:_** ')
    st.write(image_desc)
    for i in stqdm(range(100), backend=True, frontend=True):
      time.sleep(0.5)
    st.markdown('**_Predicted image that generated by AI:_** ')
    image = stable_diffusion_xl(image_desc)
    st.image(image)
