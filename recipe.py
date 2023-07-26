import streamlit as st
from langchain.llms import OpenAI, Cohere
import os 
import replicate
import os
import urllib.request
from PIL import Image
import streamlit as st
from pathlib import Path
import random
import pandas as pd
import cohere as co
from fpdf import FPDF
import requests
from PIL import Image
from io import BytesIO
import urllib.request
import json
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator
from typing import List

st.title("RefrigerEats")

mod = None

with st.sidebar:
    with st.form('Cohere/OpenAI'):
        # User selects the model (OpenAI/Cohere) and enters API keys
        model = st.radio('Choose OpenAI/Cohere', ('OpenAI', 'Cohere'))
        api_key = st.text_input('Enter API key', type="password")
        rep_key = st.text_input('Enter Replicate Key', type="password")
        submitted = st.form_submit_button("Submit")


# Check if API key is provided and set up the language model accordingly
if api_key:
    if model == 'OpenAI':
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["REPLICATE_API_TOKEN"] = rep_key
        model_name = "gpt-3.5-turbo"
        temperature = 0.0
        model = OpenAI(model_name=model_name, temperature=temperature)
        mod = 'OpenAI'
    elif model == 'Cohere':
        os.environ["Cohere_API_KEY"] = api_key
        os.environ["REPLICATE_API_TOKEN"] = rep_key
        llm = Cohere(cohere_api_key=api_key,max_tokens=2096)
        mod = 'Cohere'


def objectDetect(path):
    output = replicate.run(
        "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
        input={"image": open(path, "rb"),
               "question": "List all the fruits, vegetables adn edible items in the image"}
    )
    return output

def imageGen(prompt):
    output = replicate.run(
        "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
        input={"prompt": prompt}
    )
    return output

def recipe(res):
    recipe=[]
    for i in res:
        recipe_string = f"Dish Name: {i}\n\n"
        recipe_string += "Ingredients:\n"
        for ingredient in res[i]["Ingredients"]:
            recipe_string += f"- {ingredient}\n"
        recipe_string += "\nSteps:\n"
        for step_num, step in enumerate(res[i]["Steps"], 1):
            recipe_string += f"{step_num}. {step}\n"
        recipe.append(recipe_string)
    return recipe

def images(res):
    images = []
    for i in res:
        prompt = f"""
        I am making a cooking book and I need to generate images for my recipes.
        The name of the recipe is {i}.
        Make a realistic simple image of the recipe using these ingredients.
        """
        images.append(imageGen(prompt))
    return images

def generate_pdf(text,recipe_list,image_paths):
        # Create a FPDF object
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set style and size of font for the PDF
    pdf.set_font("Arial", size=12)

    # Set left and right margins
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    # Add the heading line "Top 3 Recipes"
    pdf.cell(0, 10, "Top 3 Recipes", ln=True, align="C")

    # Add a line break after the heading
    pdf.ln(10)

    # Add multi-cell with line break for the text
    pdf.multi_cell(0, 10, text)

    # Move to the next line after the text
    pdf.ln()

    # Add a page
    pdf.add_page()

    pdf.ln(10)
    pdf.multi_cell(0, 10, recipe_list[0])

    # Add the first image to the PDF
    pdf.image(image_paths[0], x=20, y=pdf.get_y(), w=175)

    # Calculate the y-coordinate for the second image
    second_image_y = pdf.get_y() + 10 + pdf.h

    pdf.add_page()  # Add a new page for the second recipe

    pdf.ln(10)
    pdf.multi_cell(0, 10, recipe_list[1])
    # Add the second image to the PDF
    pdf.image(image_paths[1], x=20, y=pdf.get_y(), w=175)

    # Calculate the y-coordinate for the third image
    third_image_y = pdf.get_y() + 10 + pdf.h

    pdf.add_page()  # Add a new page for the third recipe

    pdf.ln(10)
    pdf.multi_cell(0, 10, recipe_list[2])
    # Add the third image to the PDF
    pdf.image(image_paths[2], x=20, y=pdf.get_y(), w=175)

    # Save the PDF with the given file name
    pdf.output("output.pdf")


uploaded_file = st.file_uploader(f"Upload image:", type=['png','jpg'])

st.write("Additional instructions:")
vegOrNon = st.selectbox("veg / Non- Veg",("Veg","Non-Veg"))
cuisines = [
    "Italian",
    "Chinese",
    "Indian",
    "Japanese",
    "Mexican",
    "Thai",
    "Greek",
    "French",
    "Spanish",
    "Korean"
]
cuisine = st.selectbox("Select Cuisine", cuisines)
Taste = st.selectbox("Select Taste Preference",("Sweet","Spicy","Salty","Sour"))


if (st.button("Submit")):
    if uploaded_file is not None: 
            st.write("File uploaded successfully!")
            file_contents = uploaded_file.read()
            save_path = uploaded_file.name
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            image.save(save_path)
            output = objectDetect(save_path)
            # output = "tomatoes, cucumbers, carrots, peppers, onions, lettuce, broccoli, cabbage, carrots, tomatoes, broccoli, cabbage, carrots"
            st.write("These are the Ingredients present:")
            st.write(output)
            if(mod==Cohere):
                input_txt = f"""
                suggest top 3 recipes that can be made from ingredients list. also consider the recipe should be\
                {Taste} in taste, {vegOrNon} and the cuisine should be {cuisine} strictly.
                1. For the first recipe, select one important ingredient from the list and propose a recipe centered around it.
                2. The second recipe should be a combination of all the ingredients in the list.
                3. Lastly, suggest a recipe that harmoniously combines the vegetables from the list with the essence of authentic {vegOrNon} and {cuisine} cuisine.
                Format:
                ```Recipe Name:```
                ```Ingredients:```
                ```Steps:```
                Follow the Format strictly as mentioned and all 3 keys should always be present.
                ingredients = {output}
                Each recipe should be in new line and strictly do not give numbering to new lines.
                Do not end your output with lines somethins like :Let me know if you have any other questions!. \
                Just give the recipe and end your output.
                """
                st.write("Here are the top 3 recipes that can be made from the ingredients available")
                response = llm(input_txt)
                recipes = response.split('\n\n')
                txt=""
                for recipe in recipes:
                    st.markdown(recipe)
                    st.markdown("---")
                    txt += recipe
                # st.write(recipes)
                print(response)
                # res = llm(f"what are the 3 recipes mentioned in give output in json format strictly {response}")
                res = llm(f"return the names of 3 recipes mentioned in {response} in a list format")
                print(res)
                # st.write(res)
                recipes_list = res.splitlines()
                images = []
                res_li = []
                for i in recipes_list:
                    if i:
                        print(i)
                        prompt = f"""
                        I am making a cooking book and I need to generate images for my recipes.
                        The name of the recipe is {i}.
                        Make a realistic simple image of the recipe using these ingredients.
                        """
                        res_li.append(i)
                        images.append(imageGen(prompt))
                # res = json.loads(res)
                # recipe = recipe(res)
                # st.write(recipe)
                # img = images(res)
                # img = [img[0] for img in img]
                images = [image[0] for image in images]
                cnt = 0
                for i in images:
                    url = i
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(f"out{cnt}.png", "wb") as f:
                            f.write(response.content)
                    cnt = cnt+1

                for i, j in zip(res_li,images):
                    st.write(i)
                    st.image(j)
                    st.write(" ")
                
                print(res_li)
            else:
                # Here's another example, but with a compound typed field.
                class Actor(BaseModel):
                #     name: str = Field(description="name of an actor")
                #     film_names: List[str] = Field(description="list of names of films they starred in")
                    # filmography: List[List[str]] = Field(description="name of an actor and list of names of 2 films they starred in")
                    recipe: List[dict] = Field(description="Recipe Name and the ingrdients list")
                    steps: List[dict] = Field(description="Steps to make this Recipe")

                # ingredients = ["tomatoes, cucumbers, carrots, peppers, onions, lettuce, broccoli, cabbage, carrots, tomatoes, broccoli, cabbage, carrots"]
                actor_query = f"Generate the 3 recipes with steps based on {output} and italian cuisin and Veg"

                parser = PydanticOutputParser(pydantic_object=Actor)

                prompt = PromptTemplate(
                    template="Answer the user query.\n{format_instructions}\n{query}\n",
                    input_variables=["query"],
                    partial_variables={"format_instructions": parser.get_format_instructions()},
                )

                _input = prompt.format_prompt(query=actor_query)

                output = model(_input.to_string())

                out = parser.parse(output)
                recipe = []
                ingredients = []
                steps = []
                # cnt = 1
                for i,j in zip(out.recipe,out.steps):
                    recipe.append(i['name'])
                    ingredients.append(i['ingredients'])
                    steps.append(j['description'])
                
                images = []
                for i in recipe:
                    print(i)
                    prompt = f"""
                    I am making a cooking book and I need to generate images for my recipes.
                    The name of the recipe is {i}.
                    Make a realistic simple image of the recipe using these ingredients.
                    """
                    images.append(imageGen(prompt))
                
                images = [image[0] for image in images]
                cnt = 0
                for i in images:
                    url = i
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(f"out{cnt}.png", "wb") as f:
                            f.write(response.content)
                    cnt = cnt+1
                txt = ""
                for i,j,k,l in zip(recipe,ingredients,steps,images):
                    st.write(f"Dish Name: {i}")
                    st.write("Ingredients:")
                    txt += i
                    for z in j:
                        st.write(z)
                        txt += z
                    st.write("Steps:")
                    cnt=1
                    for a in k.split('\n'):
                        st.write(f"{cnt}. {a}")
                        cnt +=1
                        txt += a
                    st.image(l)
                    st.write(" ")
                res_li = recipe
                
            
            img_list=['out0.png','out1.png','out2.png']
            generate_pdf(txt,res_li,img_list)
            st.write("PDF generated successfully! Click below to download.")
            with open("output.pdf", "rb") as f:
                st.download_button("Download PDF", f.read(), file_name="output.pdf", mime="application/pdf")
                

    else:
        st.write("Please upload file")

