import pymupdf

def extract_words_from_pdf(pdf_path):
    """
    Parses a PDF and returns a list of words in reading order.
    """
    word_list = []
    
    try:
        # Open the PDF document
        doc = pymupdf.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # get_text("words") returns a list of tuples:
            # (x0, y0, x1, y1, "word", block_no, line_no, word_no)
            # This is superior to get_text("text") because it handles 
            # word wrapping and layout order automatically.
            words_on_page = page.get_text("words")
            
            for w in words_on_page:
                clean_word = w[4].strip() # Extract the actual string
                if clean_word:
                    word_list.append(clean_word)
                    
        doc.close()
        return word_list

    except Exception as e:
        return f"An error occurred: {e}"
    
words = extract_words_from_pdf("lmop.pdf")
for word in words:  # Print first 10 words to test
    print(word, end = " ")