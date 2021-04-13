# web scrapping using request and BS
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)  # initialising the flask app with the name 'app'


@app.route('/', methods=['GET'])  # route with allowed methods as POST and GET
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ", "")  # obtaining the search string entered in the form
        try:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString  # preparing the URL to search the product on flipkart
            uClient = uReq(flipkart_url)  # requesting the webpage from the internet
            flipkartPage = uClient.read()  # reading the webpage
            uClient.close()  # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
            bigboxes = flipkart_html.findAll("div", {"class": "_2kHMtA"})
            box = bigboxes[0]  # Select the first search result
            productLink = "https://www.flipkart.com" + box.a['href']  # extract the url of the first product
            prodRes = requests.get(productLink)  # getting the product page from server
            prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML
            commentboxes = prod_html.find_all('div', {
                'class': "col _2wzgFH"})  # finding the HTML section containing the customer comments

            filename = searchString + ".csv"
            fw = open(filename, "w")  # creating a local file to save the details
            headers = "Product, Customer Name, Rating, Heading, Comment \n"  # providing the heading of the columns
            fw.write(headers)  # writing first the headers to file

            reviews = []

            for commentbox in commentboxes:
                try:
                    name = commentbox.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.p.text
                except:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.find_all('div', {'class': 't-ZTKy'})
                    custComment = comtag[0].div.div.text
                except:
                    custComment = 'No Customer Comment'
                # fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}  # saving that detail to a dictionary
                # x = table.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
                reviews.append(mydict)

            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])  # showing the review to the user

        except Exception as e:
            print("Error message is ", e)
            return 'something is wrong'
            # return render_template('results.html')
    else:
        return render_template('index.html')

#port = int(os.getenv("PORT"))
if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=8000, debug=True)  # running the app on the local machine on port 8000
    # app.run(host='0.0.0.0', port=port)
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
