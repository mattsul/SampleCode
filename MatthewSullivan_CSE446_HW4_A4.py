# -*- coding: utf-8 -*-
"""MatthewSullivan_CSE446_HW4_A4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MN5hhGR8p4T7MLOG0J-KVzykLu52KTMV
"""

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional
import torchvision
from torchvision import datasets, models, transforms


# Downloading Datasets
mnist = datasets.MNIST(root="./data", train=True, download=True, transform=transforms.ToTensor())
mnist_test = datasets.MNIST(root="./data", train=False, download=True, transform=transforms.ToTensor())

# Initiating dataloaders to iterate over the data
data_loader = torch.utils.data.DataLoader(mnist, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(mnist_test, batch_size=64, shuffle=True)

# putting this puppy into the GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Using {} device'.format(device))

# function for reconstruction error 
def reconstruction_error(X_hat, X):
    error = torch.mean(torch.square(X_hat - X))
    return error.item()


# Training functions
#   Networks F1 and F2 defined homework
#   Use network F1 when which_network = False
#   Use network F2 when which_network = True
def train(which_network=False):
    D_input = 28*28
    learning_rate = 1E-2
    criterion = nn.MSELoss()
    h_all = [32,64,128]
    collection_of_images = {}
    collection_of_labels = {}
    
    # interating over all H's
    for h in h_all:
        print("Starting H=",h)
        if which_network == True:
            # F2 = defined in homework
            network = nn.Sequential(
                nn.Linear(D_input, h),
                nn.ReLU(),
                nn.Linear(h, D_input),
                nn.ReLU(),
                )
        else:
            # F1 = defined in homework
            network = nn.Sequential(
                nn.Linear(D_input, h),
                nn.Linear(h, D_input),
                )

        network = network.to(device)
        optim = torch.optim.Adam(network.parameters(), lr=learning_rate)
        epoch = 0 
        if h == 32:
            error = 99
            if which_network == True:
                # If F2 is selected
                standard = 0.025
            else:
                standard = 0.02
        else:
            standard = error
            error = 99
        while (error > standard):
            images, labels = next(iter(data_loader))
            images = images.to(device)
            images = images.view(-1, 784)
            
            optim.zero_grad()
            X_hat = network(images)
            loss = criterion(X_hat, images)
            loss.backward()
            optim.step()
            error = reconstruction_error(X_hat, images)
            epoch += 1
            if epoch % 1000 == 0:
                print("\tEpoch ", epoch, ":", error)
            if (error <= standard):
                print("\tFinal Error: ", error)
        ten_images = []
        ten_labels = []

        # Part A -- Showing 10 Images
        for i in range(10):
            images, labels = next(iter(data_loader))
            images = images.to(device)
            labels = labels.to(device)
            images = images.view(-1, 784)
            X_hat = network(images)
            ten_images.append(X_hat[0])
            ten_labels.append(labels[0])
        collection_of_images[h] = ten_images
        collection_of_labels[h] = ten_labels

        # # Part C - Analyzing with Test Set
        if h == 128:
            H128_error = np.zeros(157)
            with torch.no_grad():
                for i, data in enumerate(test_loader):
                    images, labels = data
                    images = images.to(device)
                    images = images.view(-1, 784)
            
                    X_hat = network(images)
                    H128_error[i] = reconstruction_error(X_hat, images)

    for k in collection_of_images:
        plt.figure(figsize=(8,8))
        ten_img = collection_of_images[k]
        ten_labels = collection_of_labels[k]
        count = 0
        for img in ten_img:
            plt.subplot(3,4,count+1)
            img = img.cpu()
            plt.imshow(img.detach().numpy().reshape(-1,28))
            title = "H=" + str(k) + " : Label=" + str(ten_labels[count].item())
            plt.title(title)
            plt.xticks([])
            plt.yticks([])
            count += 1

    return H128_error

# Part A
PartC_error = train()

plt.figure()
plt.plot(PartC_error)
plt.plot(range(len(PartC_error)), np.mean(PartC_error)*np.ones(len(PartC_error)))
plt.xlabel("Batch of 64")
plt.ylabel("Error")
plt.title("A.4.C h=128 Test Error with F1")
plt.legend(["Error", "Avg Error"])
print("Avg Test Set Error: ", np.mean(PartC_error))

# Part B

PartC_error = train(True)
plt.figure()
plt.plot(PartC_error)
plt.plot(range(len(PartC_error)), np.mean(PartC_error)*np.ones(len(PartC_error)))
plt.xlabel("Batch of 64")
plt.ylabel("Error")
plt.title("A.4.C h=128 Test Error with F2")
plt.legend(["Error", "Avg Error"])
print("Avg Test Set Error: ", np.mean(PartC_error))