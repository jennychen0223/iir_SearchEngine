
import streamlit as st
import xml.etree.ElementTree as ET
import re
import os 
import json



# st.set_page_config(page_title="Search PubMed Articles", page_icon="image/logo_csie2.png")
st.set_page_config(page_title="Search Engine system")
# st.image("image/title_search.png")
# st.sidebar.image("image/logo_NCKU.jpeg", use_column_width=True)


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    data = []

    for article in root.findall('.//PubmedArticle'):
        # Initialize variables with empty strings
        pmid = ''
        title = ''
        abstract = ''
        journal_title = ''
        journal_issn = ''
        pubdate_year = ''
        pubdate_month = ''
        pubdate_day = ''
        author_list = []
        keyword_list = []

        pmid_element = article.find('.//PMID')
        if pmid_element is not None:
            pmid = pmid_element.text

        title_element = article.find('.//ArticleTitle')
        if title_element is not None:
            title = title_element.text

        abstract_element = article.find('.//Abstract/AbstractText')
        if abstract_element is not None:
            abstract = abstract_element.text

        # Extracting additional information
        journal_info = article.find('.//Journal')
        journal_title_element = journal_info.find('.//Title')
        if journal_title_element is not None:
            journal_title = journal_title_element.text

        journal_issn_element = journal_info.find('.//ISSN[@IssnType="Electronic"]')
        if journal_issn_element is not None:
            journal_issn = journal_issn_element.text

        pubdate = journal_info.find('.//PubDate')
        pubdate_year_element = pubdate.find('Year')
        pubdate_month_element = pubdate.find('Month')

        if pubdate_year_element is not None:
            pubdate_year = pubdate_year_element.text
        if pubdate_month_element is not None:
            pubdate_month = pubdate_month_element.text
        
        # Check if 'Day' element exists before accessing it
        pubdate_day_element = pubdate.find('Day')
        if pubdate_day_element is not None:
            pubdate_day = pubdate_day_element.text

        authors = article.find('.//AuthorList')
        if authors is not None:
            try:
                author_list = [f"{author.find('ForeName').text} {author.find('LastName').text}" for author in authors.findall('.//Author')]
            except AttributeError:
                author_list = []

        # Check if 'KeywordList' element exists before accessing it
        keyword_list_element = article.find('.//KeywordList[@Owner="NOTNLM"]')
        if keyword_list_element is not None:
            keyword_list = [keyword.text for keyword in keyword_list_element.findall('.//Keyword')]

        data.append({
            'PMID': pmid,
            'Title': title,
            'Journal Title': journal_title,
            'ISSN': journal_issn,
            'Publication Date': f"{pubdate_year}-{pubdate_month}-{pubdate_day}",
            'Abstract': abstract,
            'Authors': ', '.join(author_list),
            'Keywords': ', '.join(keyword_list)
        })

    return data



# def search_and_highlight(article, search_term, case_sensitive=True):
def search_and_highlight(article, search_term):
    highlighted_fields = {}
    
    for key, value in article.items():
        # flags = 0 if not case_sensitive else re.IGNORECASE
        flags = 0
        try:
            highlighted_text = re.sub(
                fr'({re.escape(search_term)})',
                r'<span style="background-color: yellow">\1</span>',
                value,
                flags=flags,
            )
            if highlighted_text is not None:
                highlighted_fields[key] = highlighted_text
            else:
                highlighted_fields[key] = value
        except TypeError:
            # Handle the error by assigning the original value if 'value' is not a valid string
            highlighted_fields[key] = value

    return highlighted_fields


# Sidebar
st.sidebar.title("Documents Area")
uploaded_files_xml = st.sidebar.file_uploader("Upload Files (XML)", type=["xml"], accept_multiple_files=True)

# Initialize data list
data = []

# Load uploaded files
for xml_file in uploaded_files_xml:
    data += parse_xml(xml_file)

# Search
keyword = st.text_input("Search Engine (Enter the keyword) : ")
# case_sensitive = st.toggle("Case Sensitive Search", value=True)
matching_articles = []

if st.button("Search"):
    for article in data:
        # highlighted_fields = search_and_highlight(article, keyword, case_sensitive)
        highlighted_fields = search_and_highlight(article, keyword)
        # Check if any field was highlighted
        # if any('<span style="background-color: yellow">' in value for value in highlighted_fields.values()):
        #     matching_articles.append(highlighted_fields)
        # Check if any value in highlighted_fields contains the substring
        if any(isinstance(value, str) and '<span style="background-color: yellow">' in value for value in highlighted_fields.values()):
            matching_articles.append(highlighted_fields)

    if not matching_articles:
        st.error("Keywords not found.")
        # st.write("Not found.")
    else:
        
      # Inside the for loop where you display matching articles
      st.success("Successfully found Keywords")

      for idx, article in enumerate(matching_articles, start=1):
          
          file_name = article['PMID']
          st.markdown(f'<p style="text-align:center; color:red;">Matching Article {idx}: {file_name}.xml</p>', unsafe_allow_html=True)
          
          # Calculate and display line count for abstract
          abstract_text = article['Abstract']
          num_lines = len(abstract_text.split('\n')) if abstract_text else 0
          # st.markdown(f"**Number of Lines in Abstract**: {num_lines}", unsafe_allow_html=True)

          # Calculate and display document statistics
          abstract_text = article['Abstract']
          
          ## Keywords
          num_keywords = len(keyword.split())

          ## Characters
          try:              
            # 包含空格的字符數
            num_characters_including_spaces = len(abstract_text)
            # 不包含空格的字符數
            num_characters_excluding_spaces = len(abstract_text.replace(" ", ""))
              
          except TypeError:
            num_characters_including_spaces = 0
            num_characters_excluding_spaces = 0

          ## Words
          try:              
              num_words = len(abstract_text.split())
          except (TypeError, AttributeError):
              num_words = 0
          
          ## Sentences
        #   num_sentences = len(re.split(r'[.!?]', abstract_text)) if abstract_text else 0
        #   num_sentences = len(abstract_text)
          sss = re.split(r'[.!?]', abstract_text)
          num_sentences = len([s for s in sss if s.strip()])

          ## non-ASCII
          try:
    
              # 非 ASCII 字符數
              num_non_ascii_characters = sum(1 for char in abstract_text if ord(char) > 127)

              # 非 ASCII 單詞數
              words = re.findall(r'\b\w+\b', abstract_text)
              num_non_ascii_words = sum(1 for word in words if any(ord(char) > 127 for char in word))
          except TypeError:
      
              num_non_ascii_characters = 0
              num_non_ascii_words = 0
              

          # Create a table for document statistics
          statistics_table = {
              "Statistic": ["Number of Keywords", 
                            "Number of Characters (including spaces)", 
                            "Number of Characters (excluding spaces)",  
                            "Number of Words",
                            "Number of Sentences",
                            "Number of non-ASCII characters",
                            "Number of non-ASCII words",                            
                            ],

              "Value": [num_keywords, 
                        num_characters_including_spaces, 
                        num_characters_excluding_spaces, 
                        num_words,
                        num_sentences,
                        num_non_ascii_characters,
                        num_non_ascii_words
                        ]
          }

          st.table(statistics_table)

          # Display other article information
          for key, value in article.items():
              if key in ['PMID', 'Title', 'Journal Title', 'ISSN', 'Publication Date', 'Authors', 'Keywords']:
                  # Format these fields as bold and italic
                  st.markdown(f"**_{key}_**: {value}", unsafe_allow_html=True)
              else:
                  st.markdown(f"**{key}**: {value}", unsafe_allow_html=True)
          st.write("---")

    #   # Display the total number of matching articles
    #   st.write(f"Total Number of Matching Articles: {len(matching_articles)}")