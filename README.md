# Analyzing_food_views_and_Recommending_Customers_Wanted_Restaurants
We use Python to scrape over 500,000 customer reviews from restaurant review websites such as Google and EZtable. Later we use 2 NLP models to analyze the views. The first model is BERT and we re-train it to re-evaluate each restaurant based on user reviews. The second model is Jieba and we use it to create labels of high relevance for each searching.

#Website
https://honestreview.herokuapp.com/

![image](https://github.com/greglll/Analyzing_food_views_and_Recommending_Customers_Wanted_Restaurants/blob/master/heatmap_test_y_3X3_0922.png =80x)
fig1. After re-training by three labels(positive, neutral, and negative), we use BERT to test the validation dataset. Result shows high accuracy on the positive and negative labels. But there are uncertain when validating neutral labels.
