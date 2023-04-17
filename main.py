from flask import Flask, redirect, url_for, render_template, request, Response
from matplotlib import pyplot as plt

from socialcapitaltoolkit import socialcapitaltoolkit
app = Flask(__name__)

# create welcome page for user
@app.route('/')
def welcome():
    return render_template('index.html')

# Response processing after user response submission
@app.route('/submit',methods = ['POST','GET'])
def submit():
    if request.method == 'POST':
        response_submitted = request.form['text_submitted']
        my_model_response, dict_output_df, cluster_words, cluster_number, df_ss, pred = socialcapitaltoolkit(response_submitted)

        # create plot for cluster topics
        xs = dict_output_df['className']
        ys = dict_output_df['p']
        plt.figure(figsize=(10, 7))
        plt.bar(xs,ys)
        plt.xlabel("Cluster Topics")
        plt.ylabel("Probability")
        plt.savefig('static/myplot.png')

        #create pie chart for sentiment scores
        my_data = df_ss['Values']
        my_labels = ['negative', 'neutral', 'positive']
        plt.figure(figsize=(10, 7))
        plt.pie(my_data, labels=my_labels, autopct='%1.1f%%')
        plt.title('Sentiment Scores')
        plt.axis('equal')
        plt.savefig('static/myplot2.png')

        return render_template('result.html',plot_url = 'static/myplot.png',plot = 'static/myplot2.png',cluster_words=cluster_words, cluster_number=cluster_number, pred=pred)

if __name__ == '__main__':
    app.run(debug=True)
