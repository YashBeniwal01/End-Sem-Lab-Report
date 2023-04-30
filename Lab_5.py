# -*- coding: utf-8 -*-
"""Lab5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wN29X5tQzyChNOQiTDz6LTYUkFFJQ-7E
"""

install.packages("bnlearn")
install.packages("epiDisplay")
install.packages("bnclassify")
install.packages("e1071")
install.packages("caret")

library(bnlearn)
library(epiDisplay)
library(bnclassify)
library(e1071)
library(caret)

grades.grades <- read.csv('2020_bn_nb_data.txt', sep = "\t", head = TRUE, stringsAsFactors=TRUE)
grades.courses <- grades.grades[, -9]

head(grades.grades)

summary(grades.grades)

""" Part 1) Learning dependencies between the courses

Using hill climbing search, we learn dependencies between different grades. We use two score and compare the result between them.

"""

grades.hc.k2 <- hc(grades.courses, score = "k2")
grades.hc.k2

plot(grades.hc.k2, main = "Hill Climbing with k2 score")

grades.hc.bic <- hc(grades.courses, score = "bic")
grades.hc.bic

plot(grades.hc.bic, main = "Hill Climbing with bic score")

grades.courses.fitted <- bn.fit(grades.hc.k2, grades.courses)

grades.courses.plots <- lapply(grades.courses.fitted, bn.fit.barchart)

"""Part 3) What grade will a student get in PH100 if he earns DD in EC100, CC in IT101 and CD in MA101

"""

grades.courses.PH100Grade <- data.frame((cpdist(grades.courses.fitted, nodes=c("PH100"), evidence= (EC100 == "DD") & (IT101 == "CC") & (MA101 == "CD"))))
tab1(grades.courses.PH100Grade, sort.group = "decreasing", main = "Distribution of grades in PH100 with given evidence")

split <- sample(c(rep(0, 0.7*nrow(grades.grades)), rep(1, 0.3*nrow(grades.grades))))

table(split)

data_train <- grades.grades[split == 0,]
data_test <- grades.grades[split == 1,]
head(data_test)

split_data <- function() {
  split <- sample(c(rep(0, 0.7*nrow(grades.grades)), rep(1, 0.3*nrow(grades.grades))))
  data_train <- grades.grades[split == 0,]
  data_test <- grades.grades[split == 1,]
  list("data_train" = data_train, "data_test" = data_test)
}

if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

BiocManager::install("graph")
BiocManager::install("Rgraphviz")

nb.grades_indep <- nb(class = "QP", dataset = data_train)
nb.grades_indep <- lp(nb.grades_indep, data_train, smooth = 0)
plot(nb.grades_indep)

p_indep <- predict(nb.grades_indep, data_test)
confusionMatrix(p_indep, data_test$QP)

for (i in 1:20){
  data <- split_data()
  data_test <- data$data_test
  data_train <- data$data_train
  nb.grades_indep <- nb(class = "QP", dataset = data_train)
  nb.grades_indep <- lp(nb.grades_indep, data_train, smooth = 0)
  p_indep <- predict(nb.grades_indep, data_test)
  print(accuracy(p_indep, data_test$QP))
}

nb.grades_dep <- tan_cl("QP", data_train)
nb.grades_dep <- lp(nb.grades_dep, data_train, smooth = 1)
plot(nb.grades_dep)

p_dep <- predict(nb.grades_dep, data_test)
confusionMatrix(p_dep, data_test$QP)

for (i in 1:20){
  data <- split_data()
  data_test <- data$data_test
  data_train <- data$data_train
  nb.grades_dep <- tan_cl("QP", data_train)
  nb.grades_dep <- lp(nb.grades_dep, data_train, smooth = 1)
  p_dep <- predict(nb.grades_dep, data_test)
  print(accuracy(p_dep, data_test$QP))
}