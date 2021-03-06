# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 22:19:18 2018

@author: sixge
"""

import numpy as np
#import cv2, os
#import sys
import pandas as pd
import tensorflow as tf
#import psutil

from modeltestwin1_batchnorm import Tensorflow_Model
from readtestingimagedata import readtestingimage
from readimagedata import readimage

class dl_model():

    EXT_TRAIN_DATA = 'train'
    EXT_TEST_DATA = 'test'
    EXT_TRAIN_CSV = 'trainLabels.csv'
    EXT_TEST_CSV = 'testLabels.csv'
    
    IMAGE_WIDTH = 512 #1536
    IMAGE_HEIGHT = 340 #1024
    N_CHANNELS = 3

    GENERATOR_BATCH_SIZE = 50
    GENERATOR_TEST_BATCH_SIZE = 100
    #NB_EPOCH_PER_BATCH = 1
    NB_EPOCH = 4800
    
    train_loss = []
    train_accuracy = []
    test_accuracy = []
    testing_accuracy = []
    t_accuracy = []
    #argv = "/Users/sixge/Google Drive/graduate seminar/Code/data"
    
    def __init__(self):
        self.BASE_PATH = "/Users/sixge/Desktop/data"
        self.LOG1_PATH = "/Users/sixge/Desktop/data/trainingResults.csv"
        self.LOG2_PATH = "/Users/sixge/Desktop/data/testingResults.csv"
        self.LABEL_PATH = "/Users/sixge/Desktop/data/Confusiontable.csv"
#        self.BASE_PATH = "/Users/sixge/Google Drive/graduate seminar/Code/data"
#        self.LOG1_PATH = "/Users/sixge/Google Drive/graduate seminar/Code/data/trainingResult.csv"
#        self.LOG2_PATH = "/Users/sixge/Google Drive/graduate seminar/Code/data/testingResults.csv"
#        self.BASE2_PATH = "/Users/deyi/Google Drive/graduate seminar/Code/data"
        self.dims_image = {'width': self.IMAGE_WIDTH, 'height': self.IMAGE_HEIGHT, 'channel': self.N_CHANNELS}
        self.dims_output = 5
        self.sess = tf.Session()  
        
    def one_hot(self, Y):
#        max = np.max(Y)
        #print(Y)
        one_hot_encoded = np.zeros([Y.shape[0], 5])
        for i, y in enumerate(Y):
            one_hot_encoded[i, y] = 1
        return one_hot_encoded


    def get_x_y(self, data):
#        print('Data shape: {}'.format(data.shape))
#        print('Y values: {}'.format(data[:, 1]))
        x = np.array([x for x in data[:, 0]]).reshape([-1, self.dims_image['height'], self.dims_image['width'], self.dims_image['channel']])
        y = self.one_hot(data[:, 1])
#        print('x shape: {}'.format(x.shape))
#        print('y shape: {}'.format(y.shape))

        return x, y
              
    def execute(self):
#        with tf.device('/device:GPU:0'):
        #with tf.device('/cpu:0'):
        
            pred_label = []
            test_label = []
            x = tf.placeholder(tf.float32, [None, self.dims_image['height'], self.dims_image['width'], self.dims_image['channel']])
            y = tf.placeholder(tf.float32, [None, self.dims_output])
            tf_model = Tensorflow_Model(self.dims_image, self.dims_output) # CALCULATE dims_output
            _y =  tf_model.model(x)
            cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=_y, labels=y))
            extra_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
            with tf.control_dependencies(extra_update_ops):
                optimizer = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(cost)
            corr = tf.equal(tf.argmax(_y, 1), tf.argmax(y, 1))
            accr = tf.reduce_mean(tf.cast(corr, tf.float32))
            prediction = tf.argmax(_y, 1)
            og_label = tf.argmax(y, 1)
            
######################################################################
##save model and parameters            
            
            
            self.sess.run(tf.global_variables_initializer())    
            
#            saver = tf.train.Saver()
            saver = tf.train.Saver()
        
            for i in range (0, self.NB_EPOCH):
                print("Training iteration",i)
                avg_cost = 0
                training_batch_generator = readimage(self.GENERATOR_BATCH_SIZE, self.EXT_TRAIN_CSV).execute()
                for j, element in enumerate(training_batch_generator):
                    training_batch = element
#                    print("type is ",type(training_batch))
                batch_x, batch_y =  self.get_x_y(training_batch)      
#                tf.map_fn(lambda frame: tf.image.per_image_standardization(batch_x), batch_x)
                self.sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
                avg_cost += self.sess.run(cost, feed_dict={x: batch_x, y: batch_y})/self.dims_output
                train_acc = self.sess.run(accr, feed_dict={x: batch_x, y: batch_y})
                self.train_loss.append(avg_cost)
                self.train_accuracy.append(train_acc)
                print('Average Cost: {}, Training Accuracy: {}'.format(avg_cost, train_acc))
                
                if (i+1) % 2400 == 0:
                    for k in range(0, 51):
                        print("Testing iteration", k)
                        batch_point = k * 100
                        testing_batch_generator = readtestingimage(batch_point, self.EXT_TEST_CSV).execute()
                        for j, element in enumerate(testing_batch_generator):
                            testing_batch = element
#                        for label_values in testing_batch[1]:
#                            test_label.append(label_values)
#                        print('test_label', test_label)
                        batch_x, batch_y =  self.get_x_y(testing_batch)
#                    self.sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
                        
                        test_acc = self.sess.run(accr, feed_dict={x: batch_x, y: batch_y})
#                        org_label = self.sess.run(og_label, feed_dict={x: batch_x, y: batch_y})
#                        for label_values in org_label:
#                            test_label.append(label_values)
##                        print('test_label', test_label)
#                        predictions = self.sess.run(prediction, feed_dict={x: batch_x, y: batch_y})
#                        for pred_value in predictions:
#                            pred_label.append(pred_value)
#                        print('pred_label', pred_label)
#                        print('Testing Accuracy: {}'.format(test_acc))
                        self.testing_accuracy.append(test_acc)
                        
                        if (i+1) % 600 == 0:
                             org_label = self.sess.run(og_label, feed_dict={x: batch_x, y: batch_y})
                             for label_values in org_label:
                                 test_label.append(label_values)
#                        print('test_label', test_label)
                             predictions = self.sess.run(prediction, feed_dict={x: batch_x, y: batch_y})
                             for pred_value in predictions:
                                 pred_label.append(pred_value)
#                        print('pred_label', pred_label)
                                
                    
                    
                    
                    temp_accuracy = sum(self.testing_accuracy)  / 51
                    self.testing_accuracy = []
                    self.test_accuracy.append(temp_accuracy)
                    print('Testing Tempery Accuracy: {}'.format(temp_accuracy))
                    
##########################################################################################################        
            # Save the variables to disk.
#            saver.save(self.sess, "/tmp/model.ckpt")
            saver.save(self.sess, "/tmp/savedmodel.ckpt")
      
            
            log_data = {'loss':self.train_loss, 'train accuracy':self.train_accuracy}
            df = pd.DataFrame(log_data, columns = ['loss', 'train accuracy'])
            df.to_csv(self.LOG1_PATH,index=False)
#
#            self.t_accuracy.append(self.test_accuracy)
            log_data = {'test accuracy':self.test_accuracy}
            df = pd.DataFrame(log_data, columns = ['test accuracy'])
            df.to_csv(self.LOG2_PATH,index=False)
#            
            log_data = {'test label':test_label, 'predict label':pred_label}
            df = pd.DataFrame(log_data, columns = ['test label', 'predict label'])
            df.to_csv(self.LABEL_PATH,index=False)
            ##########################################################
#            #Calculate testing accuracy
            
#                if (i+1) % 10 == 0:
#                    print('Testing Accuracy: {}'.format(test_acc))
#                    self.test_accuracy = []
                    
dl_model().execute()
