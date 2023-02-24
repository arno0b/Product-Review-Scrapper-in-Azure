from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import csv

application = Flask(__name__)  # create a Flask instance
app = application
@app.route('/',methods=['GET'])  # create a route for the home page
@cross_origin()
def homePage():
    return render_template("index.html")  # return the index.html template for the home page

@app.route('/review', methods = ['POST','GET'])  # create a route for the review page
def index():
      if request.method == 'POST':  # check if request method is POST
            try:
                  search_string = request.form['content'].replace(" ", "")  # retrieve the search query and remove spaces
                  flipkart_url  = "https://www.flipkart.com/search?q=" + search_string  # construct Flipkart URL with search query
                  url_client = uReq(flipkart_url)  # open URL using urlopen from urllib.request
                  flipkart_page = url_client.read()  # read the page HTML content
                  url_client.close()  # close the URL client
                  flipkart_html = bs(flipkart_page, "html.parser")  # parse the HTML content using BeautifulSoup
                  boxes = flipkart_html.findAll('div', {'class': "_1AtVbE col-12-12"})  # find all HTML div elements with the specified class
                  del boxes[0:3]  # delete the first three elements in the list
                  box = boxes[0]  # get the first element in the list
                  prod_link = 'https://www.flipkart.com' + box.div.div.div.a["href"]  # construct URL for the product page
                  prod_res = requests.get(prod_link)  # make an HTTP GET request to the product page
                  prod_res.encoding = 'utf-8'  # set the encoding to utf-8
                  prod_html = bs(prod_res.text, 'html.parser')  # parse the HTML content of the product page
                  rev_box = prod_html.find_all('div', {'class': '_16PBlm'})  # find all HTML div elements with the specified class

                  filename = search_string + ".csv"  # set the filename for the CSV file
                  fw = open(filename, 'w')  # open the file for writing
                  headers = "Product, Customer_name, Rating, Heading, Comment \n"  # set the headers for the CSV file
                  fw.write(headers)  # write the headers to the CSV file
                  review = []  # create an empty list for storing reviews
                  for box in rev_box:  # loop through each review box
                        try:
                              name = box.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text  # get the name of the commentor
                        except:
                              name = 'No Name'  # set a default name if none is found
                            
                        try:
                              rating = box.div.div.div.div.text  # get the rating
                        except:
                              rating = 'No rating'  # set a default rating if none is found

                        try:
                              comhead = box.div.div.div.p.text  # get the comment heading
                        except:
                              comhead = 'No comment head'  # set a default comment

                        try:
                              comment = box.div.div.find_all('div', {'class': ""}) # get the comment
                              custom_comment = comment[0].div.text # set a default comment
                        except Exception as e:
                              print("Exception while creating dictionary: ",e)
                              custom_comment = 'No comment'

                        # create a dictionary for each review and add it to the list
                        mydict = {'Product': search_string, 'Name of Commentor': name,
                                'Rating': rating, 'Overall comment': comhead,
                                'Comment': custom_comment}
                        review.append(mydict)

                  # with open(filename, 'w', newline='') as file:
                  #       writer = csv.DictWriter(file, fieldnames=review[0].keys())
                  #       writer.writeheader()
                  #       for row in review:
                  #             writer.writerow(row)
                   # return the results to the result.html template
                  return render_template('result.html', reviews = review[0: (len(review)-1)])
            except Exception as e:
                  # if there is an exception while scraping, log it and return an error message
                  print('The Exception message is: ',e)
                  return 'Something is wrong'

      else:
            return render_template('index.html')
      
if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
