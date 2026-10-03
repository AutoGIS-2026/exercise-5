# Exercise 5: Cartographic visualisation


This week’s exercise focuses on creating **static and interactive maps**. Its
goal is to allow you to concentrate on cartographic visualisation using Python
tools. The task is to play around, explore different possibilities and maybe try
out other visualisation packages than we used in the lesson.


- Scores on this exercise are out of **20 points**.


## Notes

### (Almost) no instructions!

For this exercise, there are not detailed instructions given. Each of the two
notebooks defines a *topic* for a map, the expected *output format*, and
*criteria* we will use to grade your results. Beyond that, you are free to
experiment: use the data presented in the course or data from any third-party
source (don’t forget data source attribution!), stick to the Python packages we
got to know during the lessons, or experiment with other packages you found [in
the list of GIS packages in lesson
1](https://autogis-site.readthedocs.io/en/latest/lessons/lesson-1/course-motivation.html#which-gis-packages-are-available-in-python), 
or use any other packages you’ve come across.

Let your creativity run free, and show us what you’ve learnt!

#### (Almost) no immediate feedback

Whenever you push and submit your work, an automated process will check your
submission and tell you how many points you have achieved, so far.

This week, the automated feedback does not award points: it runs a few basic
checks (for instance, whether your maps are saved in the `docs` folder, and whether
they contain data) and lists anything that needs your attention. Your maps are
graded manually by the course teachers, who also provide more detailed feedback.

#### Working with large data sets

Some data sets (for instance, the full travel time matrix) are too large to be
pushed to GitHub (the limit is 100 MB per file), and can make your notebook slow:

- Only load the columns and rows you need (e.g., `usecols=` in `pandas.read_csv()`,
  `columns=` or `bbox=` in `geopandas.read_file()`), and filter the data early.
- Save intermediate results in a compact format (e.g., GeoPackage or Parquet) to the
  `data` folder, and only commit files that are reasonably small.
- If you use a large data set, don’t commit it: instead, describe in your notebook
  where to download it, and commit only a small sample (if needed).

You can find this feedback in the [‘Pull Request’](../pull/1) that has been
automatically opened when you [accepted the GitHub classroom 
assignment](#).

## Start working

 - [Problem 1 (10 points)](Exercise-5-problem-1.ipynb)
 - [Problem 2 (10 points)](Exercise-5-problem-2.ipynb)
