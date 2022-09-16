# Bruno Vieira Ribeiro - July, 2022
# XKCD scraper from Explain XKCD website
###########################################################

from requests_html import HTMLSession
import sqlite3 as sql
import pickle

s = HTMLSession()

## Getting review content
def get_strips(url):

    r = s.get(url)

    return r


# Parsing a strip
def parse_strip(r):

    # Getting the transcript as single string
    transcript_lines = r.html.xpath(
        "//h2[contains(.,'Transcript')]//following-sibling::dl"
    )

    full_transcript = ""
    for line in transcript_lines:
        full_transcript += line.text

    # Getting the top text with comic number and date
    num_and_date = r.html.find("a.external.text")[0].find("span")[0].text

    # Clean the text
    num_and_date = num_and_date.replace("\xa0", " ")

    # Comic strip number is given by:
    strip_number = num_and_date[
        num_and_date.index("#") + 1 : num_and_date.index("(") - 1
    ]

    # Getting the date:
    strip_date = num_and_date[num_and_date.index("(") + 1 : num_and_date.index(")")]

    ## Getting the strip title
    strip_title = (
        r.html.xpath('//*[@id="mw-content-text"]/div/table')[0]
        .find("td")[1]
        .find("b")[0]
        .text
    )

    # print(strip_number, strip_date, strip_title, full_transcript, sep=" | ")

    # row = {
    #     "number": strip_number,
    #     "date": strip_date,
    #     "title": strip_title,
    #     "transcript": full_transcript,
    # }
    # return row
    return strip_number, strip_date, strip_title, full_transcript


# Handling pagination
def get_next_page(url):

    r = s.get(url)

    next_button = r.html.xpath("//span[contains(.,'Next')]//parent::a")

    if next_button:
        next_url = next_button[0].attrs["href"]
        return "https://www.explainxkcd.com" + next_url
    else:
        print("Last page!")
        print(url)


def main():

    ## Start database for storing:
    con = sql.connect("xkcd.db")
    cur = con.cursor()

    ## Create table for strips info
    cur.execute(
        """CREATE TABLE IF NOT EXISTS xkcd_strips
                        (number int, date text, title text, transcript text)"""
    )

    base_url = "https://www.explainxkcd.com/wiki/index.php/"
    page = 2494
    url = base_url + str(page)

    # Loop for pagination
    counter = 2494
    # # Saving page reviews
    # results = []

    while True:
        print(f"On page {counter}")

        strip = get_strips(url)

        # results.append(parse_strip(strip))

        # print("Total strips: ", len(results))

        strip_number, strip_date, strip_title, full_transcript = parse_strip(strip)

        cur.execute(
            "INSERT OR IGNORE INTO xkcd_strips VALUES (?, ?, ?, ?)",
            (strip_number, strip_date, strip_title, full_transcript),
        )
        con.commit()

        url = get_next_page(url)
        if not url:
            break
        counter += 1

    # pickle.dump(results, open("xkcd_strips.data", "wb"))
    con.close()


if __name__ == "__main__":
    main()
