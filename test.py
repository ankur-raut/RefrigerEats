import urllib.request
from fpdf import FPDF
import streamlit as st

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
    second_image_y = pdf.get_y() + 100

    pdf.ln(10)
    pdf.multi_cell(0, 10, recipe_list[1])
    # Add the second image to the PDF
    pdf.image(image_paths[1], x=20, y=second_image_y, w=175)

    # Calculate the y-coordinate for the second image
    third_image_y = pdf.get_y() + 100

    pdf.ln(10)
    pdf.multi_cell(0, 10, recipe_list[2])
    # Add the second image to the PDF
    pdf.image(image_paths[2], x=20, y=third_image_y, w=175)

    # Save the PDF with the given file name
    pdf.output("output.pdf")


recipes_list = ["1. Tomato and Cucumber Salad",
"2. Spicy Indian Veggie Soup",
"3. Indian-Style Vegetable Stir-fry"]

img_list=['out0.png','out1.png','out2.png']
response = """
"""
generate_pdf(response,recipes_list,img_list)
st.write("PDF generated successfully! Click below to download.")
with open("output.pdf", "rb") as f:
    st.download_button("Download PDF", f.read(), file_name="output.pdf", mime="application/pdf")