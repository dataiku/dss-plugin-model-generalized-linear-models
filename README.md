# Generalized Linear Model Plugin
The GLM plugin allows users to implement generalized linear model functionality within DSS visual machine learning.
Binary Classification and Regression are available but multiclass is not. The models use the same logic as the 
[statsmodels library](https://www.statsmodels.org/stable/glm.html). Please note this plugin is not supported 
and its accuracy therefore is not able to be guaranteed. The regression spline computations use the [patsy library](https://patsy.readthedocs.io/en/latest/spline-regression.html).

# Components

The plugin contains the following components:
- Generalized Linear Model Regression to run GLM regression inside the visual ML interface
- Generalized Linear Model Classification to run GLM binary classification inside the visual ML interface
- Actual vs Expected view inside the Visual Analysis and the Deployed Model windows
- Regression Spline Prepare step to compute B-Spline basis row by row
- Regression Spline Recipe to compute B-spline basis in a separate recipe

# Release Notes

See the [changelog](CHANGELOG.md) for a history of notable changes to this plugin.

# License

This plugin is distributed under the [Apache License version 2.0](LICENSE).