import pyfiglet
from texttable import Texttable
from termcolor import colored


def logo(text,color="black"):

    # Create a PyFiglet object with your text
    text = pyfiglet.Figlet().renderText(text)

    #Add color to the text using colored
    color_text=colored(text,color=color)

    return color_text


def MakeTable(table_data,columns_width,design_chars=['-','|','+','-']):

    #Make table representation of data 
    table=Texttable()
    table.add_rows(table_data)
    table.set_cols_width(columns_width)
    table.set_chars(design_chars)
    return table    #return the table object.


def findwidth(table_data):

    #This method is used to determine width of the table for specified contents
    #Each and every row must contain same amount of data
    max=0
    columns_width=[]
    for row in range(0,len(table_data[0])):
        for column in range(0,len(table_data)):
            if(len(str(table_data[column][row]))>max):
                max=len(str(table_data[column][row]))
        columns_width.append(max)
        max=0
    return columns_width
            






