Note this plugin is currently in development and its accuracy cannot be guaranteed 
# Generalized Linear Model Plugin
The GLM plugin allows users to implement generalized linear model functionality within DSS visual machine learning 

GLMs in the doctor are  not currently feasible as the doctor is not compatible with newer version of sklearn. 
This plugin writes the statsmodel glms in the sklearn framework and is now compatible.


# Implemented

1. Binary Classification Model
2. Regression Model

# To Do

1. Implement Multiclass GLMs
2. Implement grid search strategy
 - Known issue: 3 hyper parameters are used for grid search (Power, Var Power, Alpha), 
   at any time the max a model will need defined is two hyper parameters, but it still tries to optimise based on third which causes an error as there is no change in performance.
   Solution 1: Custom grid search
   Solution 2: Make it not essential to define hyper parameters, so they are ignored in grid search