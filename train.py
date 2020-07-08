# -*- coding: utf-8 -*-
from __future__ import division
"""
Copy of GAN with Generator: LSTM, Discriminator: Convolutional NN with ECG Data

 Introduction
 ------------
    The aim of this script is to use a convolutional neural network with 
    a max pooling layer in the discrimiantor. 
    This was found to work well with the Physionet ECG data in a paper. 
    They used two convolutional NN so we will compare the difference between the 
    images generated using a single layer of CNN in the discriminator and 2 CNN layers 
    to see if this improves the quality of series generated.

"""
"""
Bringing in required dependencies as defined in the GitHub repo: 
    https://github.com/josipd/torch-two-sample/blob/master/torch_two_sample/permutation_test.pyx"""

import torch
from tqdm import tqdm
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

from torchvision import transforms
from torch.autograd.variable import Variable
sns.set(rc={'figure.figsize':(11, 4)})

import datetime 
from datetime import date
today = date.today()

import random
import json as js
import pickle
import os

from data import ECGData, PD_to_Tensor
from Model import Generator, Discriminator 

device = torch.device('cuda:0')

"""#MMD Evaluation Metric Definition
Using MMD to determine the similarity between distributions

PDIST code comes from torch-two-sample utils code: 
    https://github.com/josipd/torch-two-sample/blob/master/torch_two_sample/util.py
"""

def pdist(sample_1, sample_2, norm=2, eps=1e-5):
    r"""Compute the matrix of all squared pairwise distances.
    Arguments
    ---------
    sample_1 : torch.Tensor or Variable
        The first sample, should be of shape ``(n_1, d)``.
    sample_2 : torch.Tensor or Variable
        The second sample, should be of shape ``(n_2, d)``.
    norm : float
        The l_p norm to be used.
    Returns
    -------
    torch.Tensor or Variable
        Matrix of shape (n_1, n_2). The [i, j]-th entry is equal to
        ``|| sample_1[i, :] - sample_2[j, :] ||_p``."""
    n_1, n_2 = sample_1.size(0), sample_2.size(0)
    norm = float(norm)
    
    if norm == 2.:
        norms_1 = torch.sum(sample_1**2, dim=1, keepdim=True)
        norms_2 = torch.sum(sample_2**2, dim=1, keepdim=True)
        norms = (norms_1.expand(n_1, n_2) +
                 norms_2.transpose(0, 1).expand(n_1, n_2))
        distances_squared = norms - 2 * sample_1.mm(sample_2.t())
        return torch.sqrt(eps + torch.abs(distances_squared))
    else:
        dim = sample_1.size(1)
        expanded_1 = sample_1.unsqueeze(1).expand(n_1, n_2, dim)
        expanded_2 = sample_2.unsqueeze(0).expand(n_1, n_2, dim)
        differences = torch.abs(expanded_1 - expanded_2) ** norm
        inner = torch.sum(differences, dim=2, keepdim=False)
        return (eps + inner) ** (1. / norm)


def permutation_test_mat(matrix,
                         n_1,  n_2,  n_permutations,
                          a00=1,  a11=1,  a01=0):
    """Compute the p-value of the following statistic (rejects when high)
        \sum_{i,j} a_{\pi(i), \pi(j)} matrix[i, j].
    """
    n = n_1 + n_2
    pi = np.zeros(n, dtype=np.int8)
    pi[n_1:] = 1

    larger = 0.
    count = 0
    
    for sample_n in range(1 + n_permutations):
        count = 0.
        for i in range(n):
            for j in range(i, n):
                mij = matrix[i, j] + matrix[j, i]
                if pi[i] == pi[j] == 0:
                    count += a00 * mij
                elif pi[i] == pi[j] == 1:
                    count += a11 * mij
                else:
                    count += a01 * mij
        if sample_n == 0:
            statistic = count
        elif statistic <= count:
            larger += 1

        np.random.shuffle(pi)

    return larger / n_permutations

"""Code from Torch-Two-Samples at https://torch-two-sample.readthedocs.io/en/latest/#"""

class MMDStatistic:
    r"""The *unbiased* MMD test of :cite:`gretton2012kernel`.

    The kernel used is equal to:

    .. math ::
        k(x, x') = \sum_{j=1}^k e^{-\alpha_j\|x - x'\|^2},

    for the :math:`\alpha_j` proved in :py:meth:`~.MMDStatistic.__call__`.

    Arguments
    ---------
    n_1: int
        The number of points in the first sample.
    n_2: int
        The number of points in the second sample."""

    def __init__(self, n_1, n_2):
        self.n_1 = n_1
        self.n_2 = n_2

        # The three constants used in the test.
        self.a00 = 1. / (n_1 * (n_1 - 1))
        self.a11 = 1. / (n_2 * (n_2 - 1))
        self.a01 = - 1. / (n_1 * n_2)

    def __call__(self, sample_1, sample_2, alphas, ret_matrix=False):
        r"""Evaluate the statistic.

        The kernel used is

        .. math::

            k(x, x') = \sum_{j=1}^k e^{-\alpha_j \|x - x'\|^2},

        for the provided ``alphas``.

        Arguments
        ---------
        sample_1: :class:`torch:torch.autograd.Variable`
            The first sample, of size ``(n_1, d)``.
        sample_2: variable of shape (n_2, d)
            The second sample, of size ``(n_2, d)``.
        alphas : list of :class:`float`
            The kernel parameters.
        ret_matrix: bool
            If set, the call with also return a second variable.

            This variable can be then used to compute a p-value using
            :py:meth:`~.MMDStatistic.pval`.

        Returns
        -------
        :class:`float`
            The test statistic.
        :class:`torch:torch.autograd.Variable`
            Returned only if ``ret_matrix`` was set to true."""
        sample_12 = torch.cat((sample_1, sample_2), 0)
        distances = pdist(sample_12, sample_12, norm=2)

        kernels = None
        for alpha in alphas:
            kernels_a = torch.exp(- alpha * distances ** 2)
            if kernels is None:
                kernels = kernels_a
            else:
                kernels = kernels + kernels_a

        k_1 = kernels[:self.n_1, :self.n_1]
        k_2 = kernels[self.n_1:, self.n_1:]
        k_12 = kernels[:self.n_1, self.n_1:]

        mmd = (2 * self.a01 * k_12.sum() +
               self.a00 * (k_1.sum() - torch.trace(k_1)) +
               self.a11 * (k_2.sum() - torch.trace(k_2)))
        if ret_matrix:
            return mmd, kernels
        else:
            return mmd


    def pval(self, distances, n_permutations=1000):
        r"""Compute a p-value using a permutation test.

        Arguments
        ---------
        matrix: :class:`torch:torch.autograd.Variable`
            The matrix computed using :py:meth:`~.MMDStatistic.__call__`.
        n_permutations: int
            The number of random draws from the permutation null.

        Returns
        -------
        float
            The estimated p-value."""
        if isinstance(distances, Variable):
            distances = distances.data
        return permutation_test_mat(distances.cpu().numpy(),
                                    self.n_1, self.n_2,
                                    n_permutations,
                                    a00=self.a00, a11=self.a11, a01=self.a01)

"""

This paper 
https://arxiv.org/pdf/1611.04488.pdf says that the most common way to 
calculate sigma is to use the median pairwise distances between the joint data.

"""

def pairwisedistances(X,Y,norm=2):
    dist = pdist(X,Y,norm)
    return np.median(dist.numpy())


""" 

Function for loading ECG Data 

"""
def GetECGData(source_file,class_id):
  compose = transforms.Compose(
        [PD_to_Tensor()
        ])
  return ECGData(source_file ,class_id = class_id, transform = compose)

"""

Creating the training set of sine/ECG signals

"""

#Taking normal ECG data for now
source_filename = './bitalino_train.csv'
#source_filename = './mitbih_train.csv'
ecg_data = GetECGData(source_file = source_filename,class_id = 0)

sample_size = 119 #batch size needed for Data Loader and the noise creator function.

# Create loader with data, so that we can iterate over it

data_loader = torch.utils.data.DataLoader(ecg_data, batch_size=sample_size, shuffle=True)
# Num batches
num_batches = len(data_loader)
print(num_batches)

ROWS = 15936

"""Creating the Test Set"""
test_filename =  './bitalino_test.csv'
#test_filename =  './mitbih_test.csv'

ecg_data_test = GetECGData(source_file = test_filename,class_id = 0)

data_loader_test = torch.utils.data.DataLoader(ecg_data_test[:16227], batch_size=sample_size, shuffle=True)



"""##Defining the noise creation function"""

def noise(batch_size, features):
  noise_vec = torch.randn(batch_size, features).to(device)
  return noise_vec

"""#Initialising Parameters"""

seq_length = ecg_data[0].size()[0] #Number of features


#Params for the generator
hidden_nodes_g = 50
layers = 2
tanh_layer = False

#No. of training rounds per epoch
D_rounds = 3
G_rounds = 1
num_epoch = 35
learning_rate = 0.0002

#Params for the Discriminator
minibatch_layer = 0
minibatch_normal_init_ = True
num_cvs = 2
cv1_out= 10
cv1_k = 3
cv1_s = 1
p1_k = 3
p1_s = 2
cv2_out = 10
cv2_k = 3
cv2_s = 1
p2_k = 3
p2_s = 2

"""# Evaluation of GAN with 2 CNN Layer in Discriminator

##Generator and Discriminator training phase
"""

minibatch_out = [0,3,5,8,10]
for minibatch_layer in minibatch_out:
  path = "./your_path/Run_"+str(today.strftime("%d_%m_%Y"))+"_"+ str(datetime.datetime.now().time()).split('.')[0]
  os.makedirs(path)
  
  dict = {'data' : source_filename, 
          'sample_size' : sample_size, 
          'seq_length' : seq_length,
          'num_layers': layers, 
          'tanh_layer': tanh_layer,
          'hidden_dims_generator': hidden_nodes_g, 
          'minibatch_layer': minibatch_layer,
          'minibatch_normal_init_' : minibatch_normal_init_,
          'num_cvs':num_cvs,
          'cv1_out':cv1_out,
          'cv1_k':cv1_k,
          'cv1_s':cv1_s,
          'p1_k':p1_k,
          'p1_s':p1_s,
          'cv2_out':cv2_out,
          'cv2_k':cv2_k,
          'cv2_s':cv2_s,
          'p2_k':p2_k,
          'p2_s':p2_s,
          'num_epoch':num_epoch,
          'D_rounds': D_rounds,
          'G_rounds': G_rounds,  
          'learning_rate' : learning_rate
         }

  json = js.dumps(dict)
  f = open(path+"/settings.json","w")
  f.write(json)
  f.close()

  generator_1 = Generator(seq_length,sample_size,hidden_dim =  hidden_nodes_g, tanh_output = tanh_layer).to(device)
  discriminator_1 = Discriminator(seq_length, sample_size ,minibatch_normal_init = minibatch_normal_init_, minibatch = minibatch_layer,num_cv = num_cvs, cv1_out = cv1_out,cv1_k = cv1_k, cv1_s = cv1_s, p1_k = p1_k, p1_s = p1_s, cv2_out= cv2_out, cv2_k = cv2_k, cv2_s = cv2_s, p2_k = p2_k, p2_s = p2_s).to(device)
  #Loss function 
  loss_1 = torch.nn.BCELoss()

  generator_1.train()
  discriminator_1.train()
  
  d_optimizer_1 = torch.optim.Adam(discriminator_1.parameters(),lr = learning_rate)
  g_optimizer_1 = torch.optim.Adam(generator_1.parameters(),lr = learning_rate)

  G_losses = []
  D_losses = []
  mmd_list = []
  series_list = np.zeros((1,seq_length))


  for n in tqdm(range(num_epoch)):
     # for k in range(1):

      for n_batch, sample_data in enumerate(data_loader):
      ### TRAIN DISCRIMINATOR ON FAKE DATA
        for d in range(D_rounds):
          discriminator_1.zero_grad()

          h_g = generator_1.init_hidden()

          #Generating the noise and label data
          noise_sample = Variable(noise(len(sample_data),seq_length))

          #Use this line if generator outputs hidden states: dis_fake_data, (h_g_n,c_g_n) = generator.forward(noise_sample,h_g)
          dis_fake_data = generator_1.forward(noise_sample,h_g).detach()

          y_pred_fake = discriminator_1(dis_fake_data)

          loss_fake = loss_1(y_pred_fake,torch.zeros([len(sample_data),1]).to(device))
          loss_fake.backward()    

          #Train discriminator on real data   
          real_data = Variable(sample_data.float()).to(device)    
          y_pred_real  = discriminator_1.forward(real_data)

          loss_real = loss_1(y_pred_real,torch.ones([len(sample_data),1]).to(device))
          loss_real.backward()

          d_optimizer_1.step() #Updating the weights based on the predictions for both real and fake calculations.



        #Train Generator  
        for g in range(G_rounds):
          generator_1.zero_grad()
          h_g = generator_1.init_hidden()

          noise_sample = Variable(noise(len(sample_data), seq_length))


          #Use this line if generator outputs hidden states: gen_fake_data, (h_g_n,c_g_n) = generator.forward(noise_sample,h_g)
          gen_fake_data = generator_1.forward(noise_sample,h_g)
          y_pred_gen = discriminator_1(gen_fake_data)

          error_gen = loss_1(y_pred_gen,torch.ones([len(sample_data),1]).to(device))
          error_gen.backward()
          g_optimizer_1.step()         
    
      if n_batch ==( num_batches - 1):
          G_losses.append(error_gen.item())
          D_losses.append((loss_real+loss_fake).item())
          
          torch.save(generator_1.state_dict(), path+'/generator_state_'+str(n)+'.pt')
          torch.save(discriminator_1.state_dict(),path+ '/discriminator_state_'+str(n)+'.pt')
          
        # Check how the generator is doing by saving G's output on fixed_noise
          with torch.no_grad():
              h_g = generator_1.init_hidden()
              fake = generator_1(noise(len(sample_data), seq_length),h_g).detach().cpu()
              generated_sample = torch.zeros(1,seq_length).to(device)
              
              for iter in range(0,int(len(ecg_data_test[:ROWS])/sample_size)):
                noise_sample_test = noise(sample_size, seq_length)
                h_g = generator_1.init_hidden()
                generated_data = generator_1.forward(noise_sample_test,h_g).detach().squeeze()
                generated_sample = torch.cat((generated_sample,generated_data),dim = 0)

                # Getting the MMD Statistic for each Training Epoch
              generated_sample = generated_sample[1:][:]
              test1 = ecg_data_test[:ROWS].type(torch.FloatTensor)
              test2 = generated_sample.squeeze().cpu()

              sigma = [pairwisedistances(test1, test2)]

              mmd = MMDStatistic(len(ecg_data_test[:ROWS]), generated_sample.size(0))
              mmd_eval = mmd(test1, test2, sigma, ret_matrix=False)
              mmd_list.append(mmd_eval.item())

              series_list = np.append(series_list, fake[0].numpy().reshape((1, seq_length)), axis=0)
          
  #Dumping the errors and mmd evaluations for each training epoch.
  with open(path+'/generator_losses.txt', 'wb') as fp:
      pickle.dump(G_losses, fp)
  with open(path+'/discriminator_losses.txt', 'wb') as fp:
      pickle.dump(D_losses, fp)   
  with open(path+'/mmd_list.txt', 'wb') as fp:
      pickle.dump(mmd_list, fp)
  
  #Plotting the error graph
  plt.plot(G_losses,'-r',label='Generator Error')
  plt.plot(D_losses, '-b', label = 'Discriminator Error')
  plt.title('GAN Errors in Training')
  plt.legend()
  plt.savefig(path+'/GAN_errors.png')
  plt.close() 
  
  #Plot a figure for each training epoch with the MMD value in the title
  """
  i = 0
  while i < num_epoch:
    if i%3==0:
      fig, ax = plt.subplots(3,1,constrained_layout=True)
      fig.suptitle("Generated fake data")
    for j in range(0,3):
      ax[j].plot(series_list[i][:])
      ax[j].set_title('Epoch '+str(i)+ ', MMD: %.4f' % (mmd_list[i]))
      i = i+1
     
    plt.savefig(path+'/Training_Epoch_Samples_MMD_'+str(i)+'.png')
    plt.close(fig) 
   """
  #Checking the diversity of the samples:
  generator_1.eval()
  h_g = generator_1.init_hidden()
  test_noise_sample = noise(sample_size, seq_length)
  gen_data= generator_1.forward(test_noise_sample,h_g).detach()


  plt.title("Generated ECG Waves")
  plt.plot(gen_data[random.randint(0,sample_size-1)].tolist(),'-b')
  plt.plot(gen_data[random.randint(0,sample_size-1)].tolist(),'-r')
  plt.plot(gen_data[random.randint(0,sample_size-1)].tolist(),'-g')
  plt.plot(gen_data[random.randint(0,sample_size-1)].tolist(),'-', color = 'orange')
  plt.savefig(path+'/Generated_Data_Sample1.png')
  plt.close()
